#!/usr/bin/env python3
"""Generate release notes grouped by commit type, the way HACS repos do it.

release-drafter's `$CHANGES` categorises each **PR** by its single label, so a
`fix:` commit inside a `feat:`-titled PR is filed under Features. Across a release
that scatters one kind of change over several headings, and a reader looking for
"what was fixed" finds no Fixes section.

Surveyed 2026-08-15 against alexa_media_player, alandtse/tesla, hacs/integration
and SonoffLAN. All four group by the type of change at the top level, one line per
change, each linking to the PR it came from. None nests commits under a PR entry.

Output shape:

    ## 🚀 Features

    - add powerwall mode select for charging ([#1216](…/pull/1216))

    ## 🔧 Fixes

    - strip whitespace from the region domain ([#3524](…/pull/3524))

    **Full Changelog**: [v1.2.0...v1.3.0](…/compare/v1.2.0...v1.3.0)

Usage:
    release_notes.py --range v1.2.0..HEAD --repo-url https://github.com/o/r \\
                     --previous v1.2.0 --version 1.3.0
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commit_summary as cs  # noqa: E402  same classifier the PR body uses

MERGE = re.compile(r"^Merge pull request #(?P<pr>\d+) ")
ORDER = ("breaking", "feat", "fix", "maint", "other")
HEADINGS = {
    "breaking": "## 🚨 Breaking Changes",
    "feat": "## 🚀 Features",
    "fix": "## 🔧 Fixes",
    "maint": "## 🧰 Maintenance",
    "other": "## 📦 Other",
}


def _git(*args: str) -> str:
    return subprocess.run(("git", *args), capture_output=True, text=True, check=True).stdout


def pr_for(sha: str, head: str) -> str | None:
    """The PR a commit arrived with, from the merge commit that introduced it.

    git log is newest-first, so the introducing merge is the OLDEST containing it.
    Taking the first line instead credits every commit to the most recent merge.
    """
    out = subprocess.run(
        ("git", "log", "--merges", "--reverse", "--format=%s", f"{sha}..{head}", "--ancestry-path"),
        capture_output=True, text=True,
    ).stdout
    for line in out.splitlines():
        if m := MERGE.match(line):
            return m.group("pr")
    return None


def build(rev_range: str, repo_url: str | None = None, head: str = "HEAD",
          previous: str | None = None, version: str | None = None) -> str:
    groups: dict[str, list[str]] = {k: [] for k in ORDER}
    seen: set[tuple[str, str]] = set()

    for line in _git("log", "--reverse", "--format=%H%x00%s", rev_range).splitlines():
        if "\0" not in line:
            continue
        sha, subject = line.split("\0", 1)
        if MERGE.match(subject) or cs.BUMP.match(subject):
            continue  # merge noise and release plumbing
        key, desc = cs.classify(subject)
        if (key, desc) in seen:  # a rebase can replay a subject verbatim
            continue
        seen.add((key, desc))
        ref = ""
        if pr := pr_for(sha, head):
            ref = f" ([#{pr}]({repo_url}/pull/{pr}))" if repo_url else f" (#{pr})"
        groups[key].append(f"- {desc}{ref}")

    out: list[str] = []
    for key in ORDER:
        if groups[key]:
            out += [HEADINGS[key], "", *groups[key], ""]

    if not out:
        return "_No user-facing changes._"

    if repo_url and previous and version:
        tag = version if version.startswith("v") else f"v{version}"
        out.append(f"**Full Changelog**: [{previous}...{tag}]({repo_url}/compare/{previous}...{tag})")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--range", required=True, help="git revision range, e.g. v1.2.0..HEAD")
    ap.add_argument("--head", default="HEAD", help="tip used to resolve PR attribution")
    ap.add_argument("--repo-url", help="https://github.com/owner/repo, to link PRs")
    ap.add_argument("--previous", help="previous tag, for the compare link")
    ap.add_argument("--version", help="version being released, for the compare link")
    args = ap.parse_args()
    print(build(args.range, args.repo_url, args.head, args.previous, args.version), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
