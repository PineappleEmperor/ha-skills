#!/usr/bin/env python3
# skill-audit: local-tool
"""PostToolUse hook: record every file read, whole or partial, with its content hash.

scripts/brief_gate.py reads this log to decide whether a brief's author read what the
brief rests on, so "read in full" is something the log shows rather than something a brief
says. A Read counts as whole when it starts at the first line and its limit, or Read's
default of 2000 lines, covers the file; a governance `get_file` always emits the whole
file. The hash is taken from disk as the read happens, so a later edit makes the read stale.
"""

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / ".tmp" / "reads.jsonl"
DEFAULT_LIMIT = 2000

HOME = ROOT.parent
GATE_ROOTS = {
    "mcp__governance__": ROOT,
    "mcp__governance-ha-integration-ci__": HOME / "ha-integration-ci",
    "mcp__governance-ha-panel-ci__": HOME / "ha-panel-ci",
    "mcp__governance-release-flow__": HOME / "release-flow",
    "mcp__governance-ha-ci-testing__": HOME / "ha-ci-testing",
}


def _whole(data: bytes, args: dict) -> bool:
    """Whether a Read with these arguments covered every line of data."""
    offset = args.get("offset") or 1
    limit = args.get("limit") or DEFAULT_LIMIT
    return offset <= 1 and limit >= len(data.splitlines())


def record(payload: dict) -> dict | None:
    """The log entry for this tool call, or None when it read no file."""
    tool = payload.get("tool_name") or ""
    args = payload.get("tool_input") or {}
    if tool == "Read" and args.get("file_path"):
        path = pathlib.Path(args["file_path"])
    elif tool.endswith("get_file") and args.get("path"):
        root = next((r for p, r in GATE_ROOTS.items() if tool.startswith(p)), None)
        if root is None:
            return None
        path = root / args["path"]
    else:
        return None
    if not path.is_file():
        return None
    data = path.read_bytes()
    return {
        "session": payload.get("session_id"),
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(data).hexdigest(),
        "full": tool != "Read" or _whole(data, args),
    }


def main() -> int:
    """Append this call's entry to the log; never block and never print."""
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    entry = record(payload)
    if entry is not None:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as log:
            log.write(json.dumps(entry) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
