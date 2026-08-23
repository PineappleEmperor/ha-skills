#!/usr/bin/env python3
"""Write a release tag's version into plugin.json.

An integration is installed from the release zip, so `release.yml` patches
`manifest.json` into that artefact and the committed value stays a placeholder. A
plugin marketplace has no artefact: Claude Code reads the plugin from the repository
tree, and a declared version is what gates updates — users receive a new copy only
when that string changes. The tag still owns the number; this writes it back.

Only `plugin.json` carries it. Per the marketplace reference: "Avoid setting `version`
in both `plugin.json` and the marketplace entry. Claude Code always uses the
`plugin.json` value without warning, so a stale manifest version can mask a version you
set in `marketplace.json`." A version in the marketplace entry is therefore a defect,
and `--check` reports it.

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


def shadowed(root: pathlib.Path, plugin: str) -> bool:
    """True when the marketplace entry declares a version plugin.json will shadow."""
    market = root / MARKETPLACE
    data = json.loads(market.read_text())
    entries = [p for p in data.get("plugins", []) if p.get("name") == plugin]
    if not entries:
        sys.exit(f"{MARKETPLACE} lists no plugin named {plugin!r}")
    return any("version" in p for p in entries)


def patch(root: pathlib.Path, version: str, plugin: str) -> list[str]:
    """Set `version` in plugin.json. Returns the files that changed."""
    manifest = root / PLUGIN_MANIFEST.format(plugin=plugin)
    if not manifest.is_file():
        sys.exit(f"no manifest at {manifest}: is {plugin!r} the right plugin name?")
    if shadowed(root, plugin):
        sys.exit(f"{MARKETPLACE} declares a version for {plugin!r}; plugin.json silently "
                 "wins, so remove it there")
    data = json.loads(manifest.read_text())
    if data.get("version") == version:
        return []
    data["version"] = version
    manifest.write_text(json.dumps(data, indent=2) + "\n")
    return [str(manifest.relative_to(root))]


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
        problems = []
        manifest = json.loads((root / PLUGIN_MANIFEST.format(plugin=args.plugin)).read_text())
        if manifest.get("version") != version:
            problems.append(f"plugin.json is {manifest.get('version')}, tag says {version}")
        if shadowed(root, args.plugin):
            problems.append(f"{MARKETPLACE} declares a version that plugin.json shadows")
        for p in problems:
            print(f"drift: {p}")
        if problems:
            return 1
        print(f"plugin.json matches {version}")
        return 0

    changed = patch(root, version, args.plugin)
    print("\n".join(changed) if changed else f"already at {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
