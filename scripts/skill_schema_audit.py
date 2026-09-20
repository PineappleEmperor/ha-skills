#!/usr/bin/env python3
"""Structural audit of the shipped skill files against `docs/skill-schema.md`.

`skill_meta_audit.py` asks whether these skills are well built — frontmatter the spec
requires, a router whose links resolve, docs that match the templates that ship. This asks
the narrower question the schema asks: is every block a labelled field or a table row, does
every table use a column set the schema names, and does the contents list match the
headings underneath it.

THE CANONICAL COLUMN SETS ARE READ OUT OF THE SCHEMA, not copied here. A checker carrying
its own copy of a rule is the drift the schema exists to stop, and the brand row is what
that looks like when it happens. Adding a shape means adding a row to *Canonical tables*,
which is where a reader looks for it anyway.

What it deliberately does not check: whether a fact is in the file that owns it.
`docs/skill-file-hierarchy.md` records that a keyword checker for ownership was tried and
reverted, because a phrase deny-list is unbounded and cannot tell a restatement from a
pointer without reading. Structure is different in kind — a column set either matches or it
does not — which is why this one is mechanical and that one stays a review.

Exit 1 on any FAIL. Runs locally and in this repository's `ci.yml`.
"""

import argparse
import pathlib
import re
import sys

Result = tuple[list[str], list[str]]  # (failures, warnings)

SCHEMA = "docs/skill-schema.md"
# The longest run of consecutive unlabelled prose lines a shipped file may carry. Not a
# taste: it is what the converted files already achieve, measured rather than chosen, so it
# admits a step's one- or two-line lead-in and refuses a paragraph.
MAX_PROSE_RUN = 4
# The one heading a contents list never names: the list itself.
_CONTENTS = "contents"
_BULLET = re.compile(r"^(?:[-*+]\s|\d+[.)]\s)")
_LABELLED = re.compile(r"^(?:>\s*)?\*\*")
_SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")
_NUMBERED = re.compile(r"^\s*(\d+)[.)]\s+(.*)$")


def normalise(cell: str) -> str:
    """A column name reduced to what a comparison should care about."""
    return re.sub(r"\s+", " ", cell.replace("`", "").replace("*", "")).strip().lower()


def section(text: str, heading: str) -> list[str]:
    """The lines under one `##` heading, up to the next heading of that level."""
    out: list[str] = []
    taking = False
    for line in text.splitlines():
        if line.startswith("## "):
            taking = normalise(line[3:]) == normalise(heading)
            continue
        if taking:
            out.append(line)
    return out


def canonical_columns(schema: str) -> set[tuple[str, ...]]:
    """Every column set the schema's *Canonical tables* names.

    Read from the document so the two cannot disagree. A row's Columns cell may carry more
    than one backticked tuple, which is how `layout` states its optional third column.
    """
    found: set[tuple[str, ...]] = set()
    for line in section(schema, "Canonical tables"):
        if not line.startswith("|") or _SEPARATOR.match(line):
            continue
        cells = line.strip("|").split("|")
        if len(cells) < 2 or normalise(cells[0]) in {"table", ""}:
            continue
        for span in re.findall(r"`([^`]+)`", "|".join(cells[1:])):
            if r"\|" in span:
                found.add(tuple(normalise(c) for c in span.split(r"\|")))
    return found


def classify(text: str) -> list[tuple[int, str, str]]:
    """Every line as (1-based number, kind, text), with fenced blocks resolved.

    Kinds: fence, heading, table, bullet, labelled, quote, blank, prose. Only `prose` is
    unlabelled, which is what the core rule forbids in quantity.

    A wrapped continuation line carries no marker of its own, so it classifies as prose and
    a bullet that runs to a paragraph is counted as the paragraph it is. That is the
    schema's own rule — "a bullet that runs to a paragraph is prose wearing a dash" — and
    it is deliberate here rather than an artefact of stripping the indent.
    """
    out: list[tuple[int, str, str]] = []
    fenced = False
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith("```"):
            fenced = not fenced
            out.append((number, "fence", line))
        elif fenced:
            out.append((number, "fence", line))
        elif not line:
            out.append((number, "blank", line))
        elif line.startswith("#"):
            out.append((number, "heading", line))
        elif line.startswith("|"):
            out.append((number, "table", line))
        elif _LABELLED.match(line):
            out.append((number, "labelled", line))
        elif line.startswith(">"):
            out.append((number, "quote", line))
        elif _BULLET.match(line):
            out.append((number, "bullet", line))
        else:
            out.append((number, "prose", line))
    return out


def shipped(root: pathlib.Path) -> list[pathlib.Path]:
    """Every file the schema governs: each skill's router and its reference files."""
    found = sorted(root.glob("plugins/*/skills/*/SKILL.md"))
    found += sorted(root.glob("plugins/*/skills/*/reference/*.md"))
    return found


def check_table_columns(root: pathlib.Path) -> Result:
    """Every table header is a column set *Canonical tables* names."""
    allowed = canonical_columns((root / SCHEMA).read_text(encoding="utf-8"))
    if not allowed:
        return [
            f"{SCHEMA} names no canonical column sets; this audit holds nothing"
        ], []
    failures = []
    for path in shipped(root):
        lines = classify(path.read_text(encoding="utf-8"))
        for index, (number, kind, line) in enumerate(lines):
            if kind != "table" or index + 1 >= len(lines):
                continue
            if not _SEPARATOR.match(lines[index + 1][2]):
                continue
            columns = tuple(normalise(c) for c in line.strip("|").split("|"))
            if columns not in allowed:
                failures.append(
                    f"{path.relative_to(root)}:{number} table `{' | '.join(columns)}` is "
                    f"not a canonical column set ({SCHEMA}, Canonical tables)"
                )
    return failures, []


def check_no_prose_blocks(root: pathlib.Path) -> Result:
    """No run of unlabelled prose longer than a lead-in."""
    failures = []
    for path in shipped(root):
        run: list[int] = []
        lines = [*classify(path.read_text(encoding="utf-8")), (0, "blank", "")]
        for number, kind, _ in lines:
            if kind == "prose":
                run.append(number)
                continue
            if len(run) > MAX_PROSE_RUN:
                failures.append(
                    f"{path.relative_to(root)}:{run[0]}-{run[-1]} {len(run)} consecutive "
                    f"lines of unlabelled prose, over the {MAX_PROSE_RUN} a lead-in takes"
                )
            run = []
    return failures, []


def check_contents_matches_headings(root: pathlib.Path) -> Result:
    """A contents list names every heading under it, in order, and invents none."""
    failures = []
    for path in shipped(root):
        text = path.read_text(encoding="utf-8")
        listed = [
            normalise(match.group(2))
            for line in section(text, _CONTENTS)
            if (match := _NUMBERED.match(line))
        ]
        if not listed:
            continue
        actual = [
            normalise(line.lstrip("#"))
            for _, kind, line in classify(text)
            if kind == "heading" and line.startswith(("## ", "### "))
        ]
        actual = [heading for heading in actual if heading != _CONTENTS]
        if listed == actual:
            continue
        missing = [heading for heading in actual if heading not in listed]
        extra = [heading for heading in listed if heading not in actual]
        detail = "; ".join(
            part
            for part in (
                f"not listed: {', '.join(missing)}" if missing else "",
                f"listed but absent: {', '.join(extra)}" if extra else "",
                "out of order" if not missing and not extra else "",
            )
            if part
        )
        failures.append(
            f"{path.relative_to(root)} contents does not match its headings — {detail}"
        )
    return failures, []


def check_step_numbering(root: pathlib.Path) -> Result:
    """Step headings run 1, 2, 3 within each procedure, restarting at each `##`."""
    failures = []
    for path in shipped(root):
        expected = 1
        for number, kind, line in classify(path.read_text(encoding="utf-8")):
            if kind != "heading":
                continue
            if line.startswith("## "):
                expected = 1
            elif match := re.match(r"^### Step (\d+):", line):
                got = int(match.group(1))
                if got != expected:
                    failures.append(
                        f"{path.relative_to(root)}:{number} is Step {got}, "
                        f"expected Step {expected}"
                    )
                expected = got + 1
    return failures, []


CHECKS = (
    check_table_columns,
    check_no_prose_blocks,
    check_contents_matches_headings,
    check_step_numbering,
)


def main(argv: list[str] | None = None, root: pathlib.Path | None = None) -> int:
    """Run every check over the shipped skill files. 0 when nothing failed."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=pathlib.Path, default=root or pathlib.Path.cwd())
    parser.add_argument(
        "--list", action="store_true", help="print the registry and exit"
    )
    args = parser.parse_args(argv)
    if args.list:
        for check in CHECKS:
            print(f"{check.__name__:32} {check.__doc__.splitlines()[0]}")
        return 0

    failed = 0
    for check in CHECKS:
        failures, warnings = check(args.root)
        for warning in warnings:
            print(f"WARN  {warning}")
        for failure in failures:
            print(f"FAIL  {failure}")
        failed += len(failures)
    print(f"\n{failed} failure(s) across {len(shipped(args.root))} shipped file(s).")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
