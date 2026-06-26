"""Diagram regeneration engine (shared capability).

LLM/whiteboard emits D2 DSL text → `d2` (dagre layout engine) renders SVG →
base64 data URI embedded in the content (no static-file infra to manage).

d2 computes node coordinates itself, so the LLM only describes topology
(`a -> b -> c`) — no coordinate math, which was the failure mode of the old
fireworks + hand-layout approach.

Any failure returns None — callers MUST keep the original image as fallback.
"""
import os
import re
import base64
import asyncio
import logging
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

# d2 binary. In the container it's installed to /usr/local/bin/d2 (Dockerfile);
# on a host dev box it's on PATH (e.g. /opt/homebrew/bin/d2).
_D2_BIN = os.environ.get("D2_BIN", "d2")

_SUBPROCESS_TIMEOUT = 60  # seconds


def d2_available() -> bool:
    """True if the d2 binary is callable."""
    import shutil
    return shutil.which(_D2_BIN) is not None


async def render_diagram(dsl: str) -> Optional[str]:
    """Render a D2 DSL string to a base64 SVG data URI.

    dsl: D2 source text (topology like `a -> b -> c`). Empty/None → None.
    Returns 'data:image/svg+xml;base64,...' on success, None on any failure
    (missing d2, render error, timeout, empty DSL) so callers fall back.
    """
    if not dsl or not dsl.strip():
        return None
    if not d2_available():
        logger.warning(f"diagram engine: d2 binary not found ({_D2_BIN})")
        return None

    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "diagram.d2")
        out_path = os.path.join(tmp, "diagram.svg")
        try:
            with open(in_path, "w", encoding="utf-8") as f:
                f.write(dsl)
        except OSError as e:
            logger.warning(f"diagram engine: write .d2 failed: {e}")
            return None

        try:
            proc = await asyncio.create_subprocess_exec(
                _D2_BIN, in_path, out_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=_SUBPROCESS_TIMEOUT)
        except (asyncio.TimeoutError, FileNotFoundError, OSError) as e:
            logger.warning(f"diagram engine: d2 render failed: {e}")
            return None
        if proc.returncode != 0 or not os.path.exists(out_path):
            logger.warning(f"diagram engine: d2 returned {proc.returncode}: {stderr.decode(errors='replace')[:300]}")
            return None

        with open(out_path, "rb") as f:
            svg_text = f.read().decode("utf-8", "replace")
        svg_b64 = base64.b64encode(svg_text.encode("utf-8")).decode()
        return f"data:image/svg+xml;base64,{svg_b64}"


def demo() -> None:
    """Self-check: render a small DSL → SVG data URI; empty DSL → None."""
    dsl = "用户提问 -> LLM分析 -> 生成回答"
    uri = asyncio.run(render_diagram(dsl))
    assert uri and uri.startswith("data:image/svg+xml;base64,"), "render_diagram should return an SVG data URI"
    assert len(uri) > 200, "data URI suspiciously short — SVG likely empty"
    # d2 output has a viewBox; verify it's a real SVG.
    svg = base64.b64decode(uri.split(",", 1)[1]).decode("utf-8", "replace")
    assert 'viewBox=' in svg and '<svg' in svg, "d2 output should be an SVG with viewBox"

    # Empty/whitespace DSL returns None (nothing to draw).
    assert asyncio.run(render_diagram("")) is None, "empty DSL should return None"
    assert asyncio.run(render_diagram("   ")) is None, "whitespace DSL should return None"
    assert asyncio.run(render_diagram(None)) is None, "None DSL should return None"
    print("diagram_service demo OK")


if __name__ == "__main__":
    demo()
