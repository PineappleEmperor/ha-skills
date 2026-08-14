#!/usr/bin/env python3
"""Group a PR's commit subjects by Conventional Commit type.

Used by the `commit-summary` job in .github/workflows/pr-checks.yml to build the
marked block in a PR body, and by the `title-check` job to suggest a title type.

Lives in a script, not inline in the workflow, so it can be unit-tested — an
inline heredoc cannot be, and a silently-wrong classifier corrupts release notes
without ever failing a build.
"""

from __future__ import annotations

import argparse
import re
import sys

TYPE = re.compile(r"^(?P<type>[a-zA-Z]+)(\((?P<scope>[^)]*)\))?(?P<bang>!)?:\s*(?P<desc>.*)$")

# Types the release-drafter autolabeler folds into `chore` -> 🧰 Maintenance.
MAINT = frozenset({"chore", "docs", "refactor", "perf", "test", "build", "ci", "style"})

# The manifest/plugin version bump is release plumbing, not a changelog entry.
# Anchored on the SHAPE ("bump … version"), not on "any bump mentioning something
# version-shaped": an earlier pattern ended in `to v?\d+\.\d+`, which silently ate
# `chore: bump actions/checkout from 6.0.0 to 7.0.1` — i.e. every semver dependency
# bump vanished from the notes.
BUMP = re.compile(
    r"^[a-z]+(\([^)]*\))?:\s*bump\s+(the\s+)?"
    r"((manifest|plugin|integration|skill)\s+)?version\b",
    re.I,
)

ORDER = ("breaking", "feat", "fix", "maint", "other")
# Mirrors the emoji categories in .github/release-drafter.yml. House style: these
# are standard for GitHub release notes, and matching the surrounding document beats
# scrubbing a pattern that only reads as machine-written out of context.
# The two-space indent nests the block under release-drafter's
# `- $TITLE @$AUTHOR (#$NUMBER)` bullet, so no line may sit flush left.
# Labels are LIST ITEMS, with their bullets nested one level under them. A plain
# indented line does not start a list in markdown without a preceding blank line,
# so the earlier `  **Label**` + `  - item` shape rendered as one run-on paragraph
# in a PR body: no list, no labels. Adding blank lines fixes the PR body but breaks
# the release notes, where the block is inlined after `- $TITLE ...` and the label
# gets absorbed into that item while later labels escape the list entirely.
# This form is the only one that renders correctly in both.
HEADINGS = {
    "breaking": "  - **🚨 Breaking**",
    "feat": "  - **🚀 Features**",
    "fix": "  - **🔧 Fixes**",
    "maint": "  - **🧰 Maintenance**",
    "other": "  - **📦 Other**",
}
# Suggested PR title type per winning commit group: (title, category, semver bump).
SUGGESTIONS = {
    "breaking": ("`feat!:` (or any `type!:`)", "🚨 Breaking Change", "major"),
    "feat": ("`feat:`", "🚀 Features", "minor"),
    "fix": ("`fix:`", "🔧 Fixes", "patch"),
    "maint": ("`chore:`", "🧰 Maintenance", "patch"),
    "other": ("`chore:`", "🧰 Maintenance", "patch"),
}


def _strip_type(subject: str) -> str:
    """The description part of a Conventional Commit subject, lowercased."""
    m = TYPE.match(subject)
    return (m.group("desc") if m else subject).strip().lower()


def classify(subject: str) -> tuple[str, str]:
    """Return (group, description) for one commit subject."""
    m = TYPE.match(subject)
    if not m:
        return "other", subject.strip()
    desc = m.group("desc").strip()
    if not desc:
        # `feat:` with no description carries no information; keep the raw subject
        # so it is visible rather than rendering an empty bullet.
        return "other", subject.strip()
    if m.group("bang"):
        return "breaking", desc
    t = m.group("type").lower()
    if t in ("feat", "feature"):
        return "feat", desc
    if t == "fix":
        return "fix", desc
    if t in MAINT:
        return "maint", desc
    return "other", desc


def group(subjects: list[str]) -> dict[str, list[str]]:
    """Group non-plumbing subjects by type, preserving order within each group."""
    groups: dict[str, list[str]] = {k: [] for k in ORDER}
    for s in subjects:
        s = s.strip()
        if not s or BUMP.match(s):
            continue
        key, desc = classify(s)
        if desc not in groups[key]:  # a rebase can duplicate a subject verbatim
            groups[key].append(desc)
    return groups


def render(subjects: list[str], title: str | None = None) -> str:
    """The marked-block body, or "" when it would add nothing.

    A single bullet is always the PR title minus its type prefix, so the block
    just restates the heading above it. Measured on three published releases:
    every one carried at least one such block and none carried the multi-type
    case the sub-heads exist for. Emit nothing and let the caller drop the block.
    """
    groups = group(subjects)

    # Drop any bullet that merely restates the PR title. The title is meant to be
    # the winning commit subject, so on most PRs one bullet duplicates the heading
    # it sits under. Release notes then say the same thing twice.
    if title:
        want = _strip_type(title)
        for k in groups:
            groups[k] = [d for d in groups[k] if d.strip().lower() != want]

    used = [k for k in ORDER if groups[k]]
    if not used:
        return ""
    # Without a title we fall back to a heuristic: a lone bullet is almost always
    # the title minus its prefix. With a title the check above is exact, so a
    # surviving single bullet says something the title does not and is kept.
    if title is None and sum(len(groups[k]) for k in used) == 1:
        return ""
    lines: list[str] = []
    labelled = len(used) > 1
    for key in used:
        # Labels only when the PR spans >1 type: release-drafter already files the
        # PR under one category heading, so a lone label duplicates it.
        if labelled:
            lines.append(HEADINGS[key])
        indent = "    " if labelled else "  "
        lines += [f"{indent}- {d}" for d in groups[key]]
    return "\n".join(lines)


def winning(subjects: list[str]) -> str:
    """Highest-impact group present — the title type a PR's commits imply."""
    groups = group(subjects)
    for key in ORDER:
        if groups[key]:
            return key
    return "maint"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("render", "winning"), default="render")
    ap.add_argument("--subjects", default="-", help="file of commit subjects, or - for stdin")
    ap.add_argument("--title", help="PR title; bullets that merely restate it are dropped")
    args = ap.parse_args()

    src = sys.stdin if args.subjects == "-" else open(args.subjects, encoding="utf-8")
    with src as fh:
        subjects = fh.read().splitlines()

    print(render(subjects, args.title) if args.mode == "render" else winning(subjects))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
