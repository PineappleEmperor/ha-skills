#!/usr/bin/env python3
"""Authoring audit for the skills in THIS repository.

`skill_audit.py` answers "was the ha-integration skill followed in this integration"
and ships to every scaffolded repo. These checks answer "are the skills in this
repository well built" — frontmatter the spec requires, a router whose links resolve,
docs that describe workflows the templates actually ship, prose a reader can act on.
None of it can fire in a consuming repo, which has no `plugins/*/skills/`, so shipping
it there would be dead weight in a file people are asked to read.

Exit 1 on any FAIL. Runs locally and in `quality_audit.yml`.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

Result = tuple[list[str], list[str]]


class Repo:
    """Just enough of skill_audit's Repo for these checks."""

    def __init__(self, root: pathlib.Path) -> None:
        self.root = root


def _template_dir(repo: Repo) -> pathlib.Path | None:
    found = sorted(repo.root.glob("plugins/*/skills/*/templates"))
    return found[0] if found else None


# A workflow or job named in the docs but absent from templates/. The
# `commit-summary` job was deleted from pr-checks.yml, and six passages went on
# describing it as the thing that writes the PR body — including the table a
# reader consults first. Documenting a job the scaffold does not ship is worse than
# documenting nothing: it gets followed.
DOCS_EXCUSED = re.compile(r"supersede|do not reinstate|removed|deleted|replaced by|historical", re.I)
# Described on purpose without being shipped: the floor-bumper is an opt-in add-on
# the reader builds when a manifest carries `>=` requirements, so the skill explains
# it rather than scaffolding it into every repo.
DOCS_OPTIONAL = {"update_manifest_floors.yml"}


def check_docs_match_templates(repo: Repo) -> Result:
    """Every workflow and job the skill's docs name must exist in templates/."""
    tmpl = _template_dir(repo)
    if not tmpl or not (tmpl / ".github/workflows").is_dir():
        return [], []
    import yaml as _yaml

    shipped = {p.name for p in (tmpl / ".github").rglob("*.yml")}
    jobs: set[str] = set()
    for wf in (tmpl / ".github/workflows").glob("*.yml"):
        try:
            data = _yaml.safe_load(wf.read_text()) or {}
        except Exception:
            continue
        jobs |= set((data.get("jobs") or {}).keys())

    fails = []
    for doc in sorted((tmpl.parent).glob("SKILL.md")) + sorted((tmpl.parent / "reference").glob("*.md")):
        for n, line in enumerate(doc.read_text().splitlines(), 1):
            if DOCS_EXCUSED.search(line):
                continue
            for name in re.findall(r"`([a-z0-9_.-]+\.yml)`", line):
                if name not in shipped and name not in DOCS_OPTIONAL:
                    fails.append(f"{doc.name}:{n} names a workflow that is not shipped: {name}")
            # The job table in the workflow reference, identified by its `needs:`
            # column so that a settings table elsewhere is not read as job names.
            if doc.name == "github-actions.md" and (
                    m := re.match(r"\|\s*`([a-z0-9-]+)`\s*\|\s*(?:—|`[a-z0-9-]+`)\s*\|", line)):
                if m.group(1) not in jobs:
                    fails.append(f"{doc.name}:{n} documents a job that no workflow defines: {m.group(1)}")
    return fails, []


def check_skill_frontmatter(repo: Repo) -> Result:
    """Each SKILL.md must carry the frontmatter the skill spec requires.

    `name` and `description` are the two required fields, the block is capped at 1024
    characters, and the description states WHEN to reach for the skill. ha-panel-design
    shipped seven releases with no `name` at all, and a description that summarised what
    the skill does — which is the documented way to get an agent to act on the summary
    instead of reading the skill.
    """
    fails, warns = [], []
    for skill in sorted(repo.root.glob("plugins/*/skills/*/SKILL.md")):
        text = skill.read_text()
        parts = text.split("---", 2)
        if len(parts) < 3 or parts[0].strip():
            fails.append(f"{skill.parent.name}/SKILL.md has no frontmatter block")
            continue
        fm = parts[1]
        fields = dict(re.findall(r"^([a-z-]+):\s*(.*)$", fm, re.M))
        if "name" not in fields:
            fails.append(f"{skill.parent.name}/SKILL.md frontmatter has no name field")
        elif fields["name"].strip() != skill.parent.name:
            fails.append(f"{skill.parent.name}/SKILL.md name field is {fields['name'].strip()!r}")
        if "description" not in fields:
            fails.append(f"{skill.parent.name}/SKILL.md frontmatter has no description field")
        elif not fields["description"].lstrip().startswith("Use when"):
            fails.append(f"{skill.parent.name}/SKILL.md description must start with 'Use when' "
                         "and state triggers, not what the skill does")
        if len(fm) > 1024:
            fails.append(f"{skill.parent.name}/SKILL.md frontmatter is {len(fm)} chars (max 1024)")
        # Token budget: a skill loads in full once triggered. Past a few thousand words the
        # heavy sections belong in reference/ files, loaded only when the mode needs them.
        words = len(parts[2].split())
        if words > 5000:
            warns.append(f"{skill.parent.name}/SKILL.md is {words} words — move heavy sections "
                         "to reference/ files and leave pointers")
    return fails, warns


def check_reference_links(repo: Repo) -> Result:
    """A SKILL.md that routes to reference files must link every one, and only real ones.

    Splitting a skill into on-demand files trades one big document for a router. The
    router rots in two directions: a link to a file that was renamed sends the agent
    nowhere, and a reference file nothing links to is never read again.
    """
    fails = []
    for skill in sorted(repo.root.glob("plugins/*/skills/*/SKILL.md")):
        ref_dir = skill.parent / "reference"
        text = skill.read_text()
        linked = set(re.findall(r"\]\((reference/[A-Za-z0-9._-]+\.md)\)", text))
        linked |= set(re.findall(r"`(reference/[A-Za-z0-9._-]+\.md)`", text))
        for target in sorted(linked):
            if not (skill.parent / target).is_file():
                fails.append(f"{skill.parent.name}/SKILL.md links {target}, which does not exist")
        if ref_dir.is_dir():
            for f in sorted(ref_dir.glob("*.md")):
                if f"reference/{f.name}" not in linked:
                    fails.append(f"{skill.parent.name}/reference/{f.name} is linked from nothing")
    return fails, []


def check_paragraph_length(repo: Repo) -> Result:
    """A 400-word paragraph is a wall, and a reader skims walls.

    Measured across this skill: the longest paragraph was 491 words, and two reference
    files carried nine and eleven paragraphs over 120. Prose that long is where a
    conditional rule hides in the middle and gets applied unconditionally — which is
    exactly how the manual-bump instruction survived the move to tag-driven releases.
    """
    warns = []
    for skill in sorted(repo.root.glob("plugins/*/skills/*/")):
        if skill.name.startswith("."):
            continue
        for doc in sorted(skill.rglob("*.md")):
            # A dot-directory under skills/ is tooling, not content, and may not even be
            # readable — an unreadable file must not crash an audit.
            if any(part.startswith(".") for part in doc.parts) or \
                    "evals" in doc.parts or "templates" in doc.parts:
                continue
            try:
                text = doc.read_text()
            except OSError as exc:
                warns.append(f"{doc}: unreadable ({exc.strerror})")
                continue
            for para in re.split(r"\n\s*\n", text):
                if para.strip().startswith("```") or para.lstrip().startswith("|"):
                    continue
                n = len(para.split())
                if n > 200:
                    first = " ".join(para.split())[:60]
                    warns.append(f"{doc.relative_to(repo.root)}: {n}-word paragraph — split it ({first}...)")
    return [], warns


CHECKS = (check_docs_match_templates, check_skill_frontmatter, check_reference_links,
          check_paragraph_length)


def audit(root: pathlib.Path) -> Result:
    repo = Repo(root)
    fails: list[str] = []
    warns: list[str] = []
    for check in CHECKS:
        f, w = check(repo)
        fails += f
        warns += w
    return fails, warns


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--list", action="store_true", help="print the checks and exit")
    args = ap.parse_args(argv)

    if args.list:
        for check in CHECKS:
            print(f"{check.__name__[len('check_'):]:26} {(check.__doc__ or '').strip().splitlines()[0]}")
        return 0

    fails, warns = audit(pathlib.Path(args.root))
    for w in warns:
        print(f"⚠️  WARN: {w}")
    for f in fails:
        print(f"❌ FAIL: {f}")
    print("skill authoring audit FAILED" if fails else "✅ skill authoring audit passed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
