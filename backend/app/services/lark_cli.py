"""lark-cli subprocess wrapper.

Single chokepoint for invoking the `lark-cli` Node CLI from the Python backend:
controlled cwd, timeout, JSON parsing, normalized errors. Authorization is a
one-time manual `lark-cli auth login` (self-use); this only consumes the stored
token. Any failure raises LarkCliError so callers can fall back gracefully.
"""
import os
import json
import asyncio
import logging
import shutil
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

_LARK_BIN = os.environ.get("LARK_CLI_BIN", "lark-cli")
_DEFAULT_TIMEOUT = 60  # seconds


class LarkCliError(Exception):
    """lark-cli unavailable, unauthorized, timed out, or returned an error."""


def lark_available() -> bool:
    """True if the lark-cli binary is on PATH."""
    return shutil.which(_LARK_BIN) is not None


async def run_lark(
    args: List[str],
    *,
    timeout: int = _DEFAULT_TIMEOUT,
    cwd: Optional[str] = None,
    parse_json: bool = True,
) -> Any:
    """Run `lark-cli <args>` and return parsed JSON (or raw text if parse_json=False).

    Raises LarkCliError on missing binary, non-zero exit, timeout, or unparseable
    JSON. The caller is expected to catch this and fall back.
    """
    if not lark_available():
        raise LarkCliError(f"{_LARK_BIN} not found on PATH")

    cmd = [_LARK_BIN, *args]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        raise LarkCliError(f"lark-cli timed out after {timeout}s: {' '.join(args[:3])}")
    except (FileNotFoundError, OSError) as e:
        raise LarkCliError(f"lark-cli exec failed: {e}")

    if proc.returncode != 0:
        raise LarkCliError(
            f"lark-cli exited {proc.returncode}: {stderr.decode(errors='replace')[:400]}"
        )

    text = stdout.decode(errors="replace").strip()
    if not parse_json:
        return text
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LarkCliError(f"lark-cli output not JSON ({e}): {text[:300]}")


def demo() -> None:
    """Self-check: missing-binary path raises, available-binary path returns JSON."""
    import app.services.lark_cli as m

    # Missing binary → LarkCliError, never a raw OSError.
    orig = m._LARK_BIN
    m._LARK_BIN = "definitely-not-a-real-binary-xyz"
    try:
        asyncio.run(run_lark(["whatever"]))
        assert False, "should have raised LarkCliError for missing binary"
    except LarkCliError:
        pass
    finally:
        m._LARK_BIN = orig

    # If real lark-cli is present and authed, auth status returns a dict.
    if lark_available():
        result = asyncio.run(run_lark(["auth", "status", "--json"]))
        assert isinstance(result, dict) and "appId" in result, "auth status should return dict"
        print("lark_cli demo OK (lark-cli present, auth status parsed)")
    else:
        print("lark_cli demo OK (missing-binary path; lark-cli not installed here)")


if __name__ == "__main__":
    demo()
