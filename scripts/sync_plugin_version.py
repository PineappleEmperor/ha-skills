#!/usr/bin/env python3
"""Write a release tag's version into the plugin manifests.

An integration is installed from the release zip, so `release.yml` patches
`manifest.json` into that artefact and the committed value stays a placeholder. A
plugin marketplace has no artefact in the path: Claude Code reads
`.claude-plugin/marketplace.json` from the repository tree. The number therefore has
to be committed — so the tag still owns the version, and this writes it back.

Usage:
    sync_plugin_version.py --version 7.4.0 [--plugin ha] [--check]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+((a|b|rc)[0-9]+)?$")
PLUGIN_MANIFEST = "plugins/{plugin}/.claude-plugin/plugin.json"
MARKETPLACE = ".claude-plugin/marketplace.json"


def patch(root: pathlib.Path, version: str, plugin: str) -> list[str]:
    """Set `version` in both manifests. Returns the files that changed."""
    changed = []

    manifest = root / PLUGIN_MANIFEST.format(plugin=plugin)
    if not manifest.is_file():
        sys.exit(f"no manifest at {manifest}: is {plugin!r} the right plugin name?")
    data = json.loads(manifest.read_text())
    if data.get("version") != version:
        data["version"] = version
        manifest.write_text(json.dumps(data, indent=2) + "\n")
        changed.append(str(manifest.relative_to(root)))

    market = root / MARKETPLACE
    data = json.loads(market.read_text())
    entries = [p for p in data.get("plugins", []) if p.get("name") == plugin]
    if not entries:
        sys.exit(f"{MARKETPLACE} lists no plugin named {plugin!r}")
    if any(p.get("version") != version for p in entries):
        for p in entries:
            p["version"] = version
        market.write_text(json.dumps(data, indent=2) + "\n")
        changed.append(str(market.relative_to(root)))

    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", required=True, help="version, with or without a leading v")
    ap.add_argument("--plugin", default="ha")
    ap.add_argument("--root", default=".")
    ap.add_argument("--check", action="store_true", help="report drift without writing")
    args = ap.parse_args(argv)

    version = args.version.lstrip("v")
    if not VERSION.match(version):
        sys.exit(f"not a valid version: {args.version!r}")

    root = pathlib.Path(args.root)
    if args.check:
        manifest = json.loads((root / PLUGIN_MANIFEST.format(plugin=args.plugin)).read_text())
        if manifest.get("version") != version:
            print(f"drift: plugin.json is {manifest.get('version')}, tag says {version}")
            return 1
        print(f"manifests match {version}")
        return 0

    changed = patch(root, version, args.plugin)
    print("\n".join(changed) if changed else f"already at {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
