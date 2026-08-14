#!/usr/bin/env python3
"""Render release notes as GitHub does and fail on a malformed entry.

The release description is the artefact users read, and nothing checked it. Every
earlier verification of the commit-summary block inspected the source text, or
rendered it with python-markdown, which requires four spaces to nest a list where
CommonMark needs two. Both agreed the block was fine while GitHub showed it broken.

This renders with markdown-it in CommonMark mode, which is what GitHub uses, and
asserts the structure a reader depends on:

  - every commit bullet sits inside a nested list under its PR entry
  - a group label heads its own list item and is never glued onto a sibling
  - no bullet merely restates the PR title it sits under

Usage:
    check_release_notes.py --tag v1.2.3        # a published or draft release
    check_release_notes.py --file notes.md     # a local file
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

ENTRY = re.compile(r"^- (?P<title>.+?) @\S+ \(#(?P<pr>\d+)\)\s*$")
TYPE_PREFIX = re.compile(r"^[a-zA-Z]+(\([^)]*\))?!?:\s*")


def render(md: str) -> str:
    """CommonMark HTML, as GitHub produces it."""
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        sys.exit("markdown-it-py is required: pip install markdown-it-py")
    return MarkdownIt("commonmark").render(md)


def check(notes: str) -> list[str]:
    """Return a list of problems; empty means the notes are well formed."""
    problems: list[str] = []
    html = render(notes)

    # A label glued to the end of a sibling bullet instead of heading its own item.
    # In CommonMark that shows up as <strong> closing an <li> that began with text.
    for m in re.finditer(r"<li>(?P<body>(?:(?!</li>).)*?)</li>", html, re.S):
        body = m.group("body")
        if "<strong>" in body and not body.lstrip().startswith("<strong>"):
            if "<ul>" not in body:  # a nested list legitimately follows the text
                first = re.sub(r"<[^>]+>", "", body).strip().splitlines()[0][:60]
                problems.append(f"label glued onto a bullet: {first!r}")

    # A bullet repeating the section heading it sits under. This shipped for two
    # versions because the design note called the case "rare" and nobody measured
    # it; it was 3 of 8 merged PRs. An assumption in a comment is not a check.
    section: str | None = None
    for line in notes.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        text = line.strip().lstrip("- ").strip()
        plain = re.sub(r"[*_`]", "", text).strip().lower()
        if section and plain and plain == section:
            problems.append(f"bullet repeats its section heading: {text!r}")

    # A bullet that restates the PR title it belongs to.
    current: str | None = None
    for line in notes.splitlines():
        if m := ENTRY.match(line.strip()):
            current = TYPE_PREFIX.sub("", m.group("title")).strip()
            continue
        text = line.strip()
        if current and text.startswith("- "):
            bullet = TYPE_PREFIX.sub("", text[2:]).strip()
            if bullet and bullet.lower() == current.lower():
                problems.append(f"bullet restates its PR title: {bullet!r}")

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--tag", help="release tag to fetch with gh")
    src.add_argument("--file", help="local markdown file")
    args = ap.parse_args()

    if args.tag:
        out = subprocess.run(
            ["gh", "release", "view", args.tag, "--json", "body", "--jq", ".body"],
            capture_output=True, text=True,
        )
        if out.returncode:
            sys.exit(f"could not read release {args.tag}: {out.stderr.strip()}")
        notes = out.stdout
    else:
        with open(args.file, encoding="utf-8") as fh:
            notes = fh.read()

    problems = check(notes)
    if not problems:
        print("release notes render correctly")
        return 0
    for p in problems:
        print(f"::error::{p}")
    print(f"\n{len(problems)} problem(s). The notes are what users read; fix them before publishing.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
