"""Diagram regeneration engine (shared capability).

LLM emits structured {nodes, arrows, style, template_type} → fireworks
`generate-from-template.py` deterministically renders SVG → cairosvg → PNG,
embedded as a base64 data URI in the content (no static-file infra to manage).

Why shell out to conda python: cairosvg + libcairo live in the conda base env
(/opt/anaconda3), not the backend .venv. The fireworks render script is pure
stdlib, so the whole pipeline runs under one interpreter that already works.

Any failure returns None — callers MUST keep the original image as fallback.
"""
import os
import re
import sys
import json
import base64
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Interpreter that has cairosvg + libcairo. In the container that's the app's
# own python (cairosvg in requirements, libcairo2 in the image); on a host dev
# box set DIAGRAM_PYTHON=/opt/anaconda3/bin/python (the .venv lacks libcairo).
# ponytail: defaults to sys.executable, DIAGRAM_PYTHON overrides for host dev.
_PYTHON = os.environ.get("DIAGRAM_PYTHON", sys.executable)

# fireworks-tech-graph deterministic SVG renderer. Bundled into the image under
# backend/vendor/ so it ships with the container; FIREWORKS_SCRIPTS overrides on
# a host box pointing at the installed skill.
# ponytail: bundled vendor copy is source of truth, env overrides for host dev.
_FIREWORKS_SCRIPTS = os.environ.get(
    "FIREWORKS_SCRIPTS",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                 "vendor", "fireworks-tech-graph", "scripts"),
)
_GEN_SCRIPT = os.path.join(_FIREWORKS_SCRIPTS, "generate-from-template.py")

# Deterministically-renderable styles only. 6/7/8 are AI-hand-drawn and the
# template renderer can't produce them — clamp out-of-range to 1.
_VALID_STYLES = {1, 2, 3, 4, 5}

# fireworks template types (from generate-from-template.py DEFAULT_VIEWBOX).
_VALID_TEMPLATES = {
    "architecture", "data-flow", "flowchart", "sequence", "comparison",
    "timeline", "mind-map", "agent", "memory", "use-case", "class",
    "state-machine", "er-diagram", "network-topology",
}

_SUBPROCESS_TIMEOUT = 60  # seconds


def _normalize_spec(spec: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Coerce LLM spec into (template_type, render_data). Clamps style to 1-5."""
    template = spec.get("template_type") or spec.get("template") or "architecture"
    if template not in _VALID_TEMPLATES:
        template = "architecture"

    style = spec.get("style", 1)
    try:
        style = int(style)
    except (TypeError, ValueError):
        style = 1
    if style not in _VALID_STYLES:
        style = 1

    data = {
        "style": style,
        "title": spec.get("title", ""),
        "containers": spec.get("containers", []) or [],
        "nodes": _ensure_layout(_split_multiline_labels(spec.get("nodes", []) or [])),
        "arrows": spec.get("arrows", []) or [],
    }
    # Honor LLM-requested canvas size (the skill says: enlarge the canvas rather
    # than pack tighter). Renderer reads data["viewBox"] as "0 0 W H".
    canvas = spec.get("canvas") or {}
    cw, ch = canvas.get("width"), canvas.get("height")
    if isinstance(cw, (int, float)) and isinstance(ch, (int, float)) and (cw, ch) != (960, 700):
        data["viewBox"] = f"0 0 {int(cw)} {int(ch)}"
    if spec.get("style_overrides"):
        data["style_overrides"] = spec["style_overrides"]
    return template, data


# Canvas + node sizing for auto-layout. The fireworks renderer needs every node
# to carry x/y/width/height; LLM/whiteboard specs give only {id,label}, so we
# place any coordinate-less nodes on a grid. The renderer routes the arrows.
_NODE_W, _NODE_H = 200, 64
_COL_GAP, _ROW_GAP = 60, 50
_MARGIN = 40
# CJK char ≈ one em at the node-title font-size (18px); latin ≈ 0.55em. Used to
# size nodes to their label so long Chinese labels don't overflow the box.
# ponytail: rough per-char estimate, not a real text-width measure; tight if
# labels are very long latin — swap for svg text measurement if it shows.
_CJK_RE = re.compile(r"[　-鿿＀-￯]")


def _label_width(label: str, font_size: int = 18, padding: int = 40) -> int:
    """Estimate min node width to fit a (possibly multi-line) label."""
    if not label:
        return _NODE_W
    longest = max((len(line) for line in str(label).split("\n")), default=0)
    widest_line = max(str(label).split("\n"), key=len, default="")
    em = sum(font_size if _CJK_RE.match(c) else font_size * 0.55 for c in widest_line)
    return max(_NODE_W, int(em) + padding)


def _label_height(label: str, line_h: int = 24, min_h: int = 64) -> int:
    """Estimate node height for a multi-line label."""
    if not label:
        return min_h
    lines = max(1, str(label).count("\n") + 1)
    return max(min_h, lines * line_h + 36)


def _split_multiline_labels(nodes: list) -> list:
    """Split multi-line node labels into title + sublabel.

    The fireworks renderer treats label as a single <text> (no wrapping), so a
    label like '用户提问\\n这个项目怎么处理' renders the \\n literally and
    overflows. Split: first line → label (title), rest → sublabel (rendered as a
    smaller line below). Single-line labels are untouched.
    """
    out = []
    for node in nodes:
        m = dict(node)
        label = m.get("label", "")
        if isinstance(label, str) and "\n" in label:
            parts = [p.strip() for p in label.split("\n") if p.strip()]
            if parts:
                m["label"] = parts[0]
                if len(parts) > 1:
                    m["sublabel"] = " ".join(parts[1:])
        out.append(m)
    return out


def _strip_svg_dimensions(svg: str) -> str:
    """Remove fixed width/height from the SVG root, keep viewBox.

    With fixed dimensions the SVG renders at a fixed pixel size (overflowing
    narrow containers or shrinking). viewBox-only lets it scale to the
    container via CSS max-width:100% — matches the reference SVGs.
    """
    # Only touch the root <svg ...> tag (first one), not nested width/height.
    m = re.match(r'(<svg\b)([^>]*)(>)', svg)
    if not m:
        return svg
    attrs = re.sub(r'\s+width="[^"]*"', '', m.group(2))
    attrs = re.sub(r'\s+height="[^"]*"', '', attrs)
    return svg[:m.start(1)] + m.group(1) + attrs + ">" + svg[m.end():]


def _ensure_layout(nodes: list) -> list:
    """Inject x/y/width/height for nodes missing coordinates (grid placement),
    sizing each node to fit its label (so long Chinese labels don't overflow).

    Nodes that already carry x AND y are left in place (e.g. whiteboard passes
    real coords). ponytail: naive grid, ~3 columns; good enough for ≤~20 nodes —
    swap for a real DAG layout if diagrams get dense.
    """
    if not nodes:
        return nodes
    n = len(nodes)
    cols = 1 if n <= 1 else (2 if n <= 4 else 3)
    out = []
    # First pass: compute each node's natural size so columns can be aligned.
    sized = []
    for node in nodes:
        m = dict(node)
        label = m.get("label", "")
        m.setdefault("width", _label_width(label))
        m.setdefault("height", _label_height(label))
        sized.append(m)

    # Align column widths to the widest node in each column (no overlap).
    col_w = [0] * cols
    for i, m in enumerate(sized):
        col_w[i % cols] = max(col_w[i % cols], m["width"])

    auto_i = 0
    for i, m in enumerate(sized):
        if m.get("x") is None or m.get("y") is None:
            row, col = divmod(auto_i, cols)
            x = _MARGIN
            for c in range(col):
                x += col_w[c] + _COL_GAP
            m["x"] = x
            m["width"] = col_w[col]
            m["y"] = _MARGIN + row * (_NODE_H + _ROW_GAP)
            auto_i += 1
        out.append(m)
    return out


async def render_diagram(spec: Dict[str, Any]) -> Optional[str]:
    """Render a structured diagram spec to a base64 SVG data URI.

    spec: {nodes, arrows, style:1-5, template_type?, title?, containers?}
    Returns 'data:image/svg+xml;base64,...' on success, None on any failure
    (missing tools, render error, empty spec) so the caller can fall back.

    Returns SVG (not PNG): the browser renders it with real fonts (PingFang SC
    etc.), avoiding the garbled-text/tofu that cairosvg produces when the render
    host lacks the SVG's CJK fonts. Also skips the cairosvg+libcairo dependency.
    """
    if not spec or not (spec.get("nodes") or spec.get("containers")):
        return None
    if not os.path.exists(_GEN_SCRIPT):
        logger.warning(f"diagram engine: render script missing at {_GEN_SCRIPT}")
        return None

    template, data = _normalize_spec(spec)

    with tempfile.TemporaryDirectory() as tmp:
        svg_path = os.path.join(tmp, "diagram.svg")
        try:
            proc = await asyncio.create_subprocess_exec(
                _PYTHON, _GEN_SCRIPT, template, svg_path, json.dumps(data, ensure_ascii=False),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=_SUBPROCESS_TIMEOUT)
        except (asyncio.TimeoutError, FileNotFoundError, OSError) as e:
            logger.warning(f"diagram engine: SVG render failed: {e}")
            return None
        if proc.returncode != 0 or not os.path.exists(svg_path):
            logger.warning(f"diagram engine: render script returned {proc.returncode}: {stderr[:300]}")
            return None

        with open(svg_path, "rb") as f:
            svg_text = f.read().decode("utf-8", "replace")
        svg_text = _strip_svg_dimensions(svg_text)
        svg_b64 = base64.b64encode(svg_text.encode("utf-8")).decode()
        return f"data:image/svg+xml;base64,{svg_b64}"


def demo() -> None:
    """Self-check: render a coordinate-less spec (the real LLM/whiteboard case)."""
    spec = {
        "style": 1,
        "template_type": "flowchart",
        "title": "demo",
        "nodes": [
            {"id": "a", "label": "输入"},
            {"id": "b", "label": "处理"},
            {"id": "c", "label": "输出"},
        ],
        "arrows": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "c"},
        ],
    }
    # Multi-line label (the real LLM case with embedded \n) splits into title+sublabel.
    multi = _split_multiline_labels([{"id": "a", "label": "用户提问\n这个项目怎么处理\nWebSocket 重连？"}])
    assert multi[0]["label"] == "用户提问", "first line → label"
    assert "这个项目怎么处理" in multi[0]["sublabel"], "rest → sublabel"
    single = _split_multiline_labels([{"id": "b", "label": "短"}])
    assert "sublabel" not in single[0], "single-line label untouched"

    # Node width sizes to its (possibly CJK) label; short label stays at minimum.
    w = _label_width("短")
    assert w == _NODE_W, "short label → min width"
    assert _label_width("这是一个比较长的中文节点标签文本") > _NODE_W, "long CJK label → wider"

    uri = asyncio.run(render_diagram(spec))
    assert uri and uri.startswith("data:image/svg+xml;base64,"), "render_diagram should return an SVG data URI"
    assert len(uri) > 200, "data URI suspiciously short — SVG likely empty"
    # Root dimensions stripped (viewBox kept), so it scales to the container.
    import base64 as _b
    svg = _b.b64decode(uri.split(",", 1)[1]).decode("utf-8", "replace")
    root = re.match(r'<svg\b[^>]*>', svg).group(0)
    assert 'viewBox="0 0 960 700"' in root, "viewBox preserved"
    assert 'width="' not in root and 'height="' not in root, "root width/height stripped"

    # Auto-layout fills coords for bare nodes; existing coords are preserved.
    laid = _ensure_layout(_split_multiline_labels([{"id": "x", "label": "X"}, {"id": "y", "label": "Y", "x": 5, "y": 9}]))
    assert laid[0]["x"] is not None, "bare node should get coords"
    assert laid[1]["x"] == 5 and laid[1]["y"] == 9, "existing coords must be preserved"

    # Out-of-range style clamps to 1, doesn't crash.
    t, d = _normalize_spec({"style": 7, "template_type": "bogus", "nodes": [{"id": "x", "label": "X"}]})
    assert d["style"] == 1 and t == "architecture", "style/template clamp failed"

    # Empty spec returns None (no nodes → nothing to draw).
    assert asyncio.run(render_diagram({"nodes": []})) is None, "empty spec should return None"
    print("diagram_service demo OK")


if __name__ == "__main__":
    demo()
