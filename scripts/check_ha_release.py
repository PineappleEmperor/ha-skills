#!/usr/bin/env python3
# skill-audit: local-tool
"""Fail once Home Assistant ships a minor newer than the one the skill is written for.

`reference/freshness.md` carries a row naming the release the guidance was last checked
against. Nothing made that row true — it was a note to a future reader, and the table's own
"re-derive anything older than ~3 months" rule is exactly the kind of rule nobody runs. So
CI reads the row and compares it with PyPI, and the week a new minor lands the build goes
red naming the procedure to follow, which is `docs/release-refresh.md` and not here.

Only the minor is compared: `2026.9.2` and `2026.9.0` are the same guidance window, and a
patch release changes nothing an integration author has to read. Being *ahead* of PyPI is
fine too — a beta gets captured before the final ships — so this fails on behind, never on
mismatch.

The parse is deliberately narrow: a table row whose first cell is exactly ROW_NAME, whose
second cell is a backticked `YYYY.M`. Anything else exits 2 rather than guessing, because a
check that silently passes when it cannot find its input is worse than no check.
"""

from collections.abc import Callable
import json
from pathlib import Path
import re
import sys
import urllib.request

ROW_NAME = "HA release the skill is current for"
DEFAULT_FILE = "plugins/ha/skills/ha-integration/reference/freshness.md"
REFRESH_DOC = "docs/release-refresh.md"
PYPI = "https://pypi.org/pypi/homeassistant/json"

_MINOR = re.compile(r"^(\d{4})\.(\d{1,2})")


def _fetch(url: str) -> str:
    """Read a URL as text; the default injection point so tests never hit the network."""
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode()


def _parse_minor(value: str, source: str) -> tuple[int, int]:
    """Turn a `YYYY.M...` string into a comparable (year, minor) pair."""
    match = _MINOR.match(value.strip().strip("`"))
    if not match:
        raise ValueError(f"{source}: {value!r} is not a YYYY.M version")
    return int(match.group(1)), int(match.group(2))


def captured_minor(text: str) -> tuple[int, int]:
    """The minor in the named row's value cell, which is a backticked `YYYY.M`."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) >= 2 and cells[0] == ROW_NAME:
            return _parse_minor(cells[1], f"the {ROW_NAME!r} row")
    raise ValueError(f"no row named {ROW_NAME!r}")


def latest_minor(fetch: Callable[[str], str]) -> tuple[int, int]:
    """The newest Home Assistant minor PyPI is serving."""
    version = json.loads(fetch(PYPI))["info"]["version"]
    return _parse_minor(version, "PyPI")


def main(argv: list[str] | None = None, fetch: Callable[[str], str] = _fetch) -> int:
    """0 when the skill is current, 1 when behind, 2 when either side cannot be read."""
    args = list(sys.argv[1:] if argv is None else argv)
    path = Path(DEFAULT_FILE)
    if "--file" in args:
        index = args.index("--file") + 1
        if index >= len(args):
            print("--file needs a path", file=sys.stderr)
            return 2
        path = Path(args[index])
    try:
        captured = captured_minor(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        print(f"cannot read the captured release from {path}: {err}", file=sys.stderr)
        return 2
    try:
        latest = latest_minor(fetch)
    except Exception as err:  # noqa: BLE001 - any failure is "cannot tell", not "behind"
        print(f"cannot read the latest release from PyPI: {err}", file=sys.stderr)
        return 2
    if captured >= latest:
        print(f"skill is current for HA {captured[0]}.{captured[1]}")
        return 0
    print(
        f"skill is current for HA {captured[0]}.{captured[1]} but PyPI has "
        f"{latest[0]}.{latest[1]}: follow {REFRESH_DOC}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
