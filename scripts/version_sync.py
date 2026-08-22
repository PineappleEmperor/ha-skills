#!/usr/bin/env python3
"""Check that every copy of the Python version agrees.

The Python version an integration targets is written in four places, each read by a
different tool: the CI workflow, ruff, pyright, and (indirectly) the pinned
`pytest-homeassistant-custom-component`, which hard-pins the Home Assistant release the
suite runs against. Nothing compared them, so a bump in one place left the others behind
and CI stayed green while linting a version nobody runs.

`requirements.test.txt` is the source: it names the HA release. Everything else derives
from it and is checked against the workflow's `python-version`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

PHCC = re.compile(r"^\s*pytest-homeassistant-custom-component\s*==\s*(?P<version>\S+)", re.M)
RUFF_TARGET = re.compile(r'target-version\s*=\s*"py(?P<major>\d)(?P<minor>\d+)"')
PY_VERSION = re.compile(r'python-version:\s*["\']?(?P<version>\d+\.\d+)')


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def collect(root: pathlib.Path) -> dict[str, str | None]:
    """Every declared Python version, keyed by the file that declares it."""
    found: dict[str, str | None] = {}

    workflow = _read(root / ".github/workflows/python_validate.yml")
    m = PY_VERSION.search(workflow)
    found["python_validate.yml"] = m.group("version") if m else None

    pyproject = _read(root / "pyproject.toml")
    m = RUFF_TARGET.search(pyproject)
    found["pyproject.toml ruff target-version"] = (
        f"{m.group('major')}.{m.group('minor')}" if m else None)

    pyright = _read(root / "pyrightconfig.json")
    if pyright:
        try:
            found["pyrightconfig.json"] = json.loads(pyright).get("pythonVersion")
        except json.JSONDecodeError:
            found["pyrightconfig.json"] = None
    else:
        found["pyrightconfig.json"] = None

    return found


def problems(root: pathlib.Path) -> list[str]:
    """Disagreements between the declared versions; empty means they line up."""
    found = collect(root)
    declared = {k: v for k, v in found.items() if v is not None}
    out: list[str] = []

    distinct = set(declared.values())
    if len(distinct) > 1:
        detail = ", ".join(f"{k}={v}" for k, v in sorted(declared.items()))
        out.append(f"python version disagrees across {len(declared)} files: {detail}")

    # The pin is what fixes the HA release under test; without it the suite silently
    # follows whatever HA published today.
    reqs = _read(root / "requirements.test.txt")
    if reqs and not PHCC.search(reqs):
        out.append("requirements.test.txt does not pin pytest-homeassistant-custom-component "
                   "(the suite would test against whichever HA release is current)")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="repository root to inspect")
    args = ap.parse_args(argv)

    found = problems(pathlib.Path(args.root))
    for p in found:
        print(f"❌ FAIL: {p}")
    if not found:
        print("✅ declared python versions agree")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
