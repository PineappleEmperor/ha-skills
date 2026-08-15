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
# Release plumbing, not a changelog entry. The noun list stays closed on purpose:
# allowing arbitrary words before "to <semver>" would swallow every Dependabot
# bump ("bump aiohttp to 3.10.1"), which is a real change and must reach the notes.
BUMP = re.compile(
    r"^[a-z]+(\([^)]*\))?:\s*bump\s+(the\s+)?"
    r"((manifest|plugin|integration|skill|marketplace|ha)\s+)*"
    r"(version\b|to\s+v?\d+\.\d+)",
    re.I,
)

ORDER = ("breaking", "feat", "fix", "maint", "other")

# No group labels. release-drafter already files each PR under one category
# heading, so a label inside the entry repeats it four lines later and, when a PR
# spans types, files fixes under Features. Measured across one session: 3 of 8
# merged PRs spanned more than one type, so this was not the rare case it was
# documented as. The commits keep their severity order; the category above names
# the PR, and the bullets say what it contained.

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
    for key in used:
        lines += [f"  - {d}" for d in groups[key]]
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
