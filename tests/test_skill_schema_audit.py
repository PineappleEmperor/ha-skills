"""Tests for the structural audit, and for the shipped files it holds to.

Every unit test builds a tiny repository in `tmp_path` — a schema document and one skill
file — so a check is exercised against text this file states, not against whatever the real
skill files happen to say today.

The last test is not a unit test. It runs the audit over the committed skill files and
fails when any of them drifts, which is the same thing `ci.yml` does; it is here so a local
`pytest` catches it before a push does.
"""

import importlib.util
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_SPEC = importlib.util.spec_from_file_location(
    "skill_schema_audit",
    Path(__file__).resolve().parents[1] / "scripts" / "skill_schema_audit.py",
)
audit = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(audit)

REPO = Path(__file__).resolve().parents[1]

SCHEMA = """# Schema

## Canonical tables

| Table | Columns |
|---|---|
| anti-pattern | `anti-pattern \\| use instead \\| why (one clause) \\| reference` |
| layout | `file \\| holds`, or `file \\| holds \\| when` where the step says which to write |
| rule | `rule \\| value` — the default where no narrower shape fits |

## Block types, and the only cases that earn one

| Block | Written as | Earned when |
|---|---|---|
| row | a table line | always the default |
| `**Symptom:**` | one line | the failure misattributes its own cause |
| `**Fix:**` | one line | there is a fix path, or there is provably none |
| `> **Note:**` | blockquote, ≤ 3 lines | a caveat that changes the action in one case |

## Something else

| Table | Columns |
|---|---|
| not canonical | `never \\| read` |
"""


def _repo(tmp_path: Path, body: str, schema: str = SCHEMA) -> Path:
    """A repository holding the schema and one shipped reference file."""
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/skill-schema.md").write_text(schema, encoding="utf-8")
    where = tmp_path / "plugins/ha/skills/demo/reference"
    where.mkdir(parents=True, exist_ok=True)
    (where / "topic.md").write_text(body, encoding="utf-8")
    return tmp_path


# ----------------------------------------------------------------- the schema


def test_the_column_sets_are_read_from_the_schema_not_from_the_code() -> None:
    """A checker carrying its own copy of the rule is the drift it exists to stop."""
    found = audit.canonical_columns(SCHEMA)
    assert ("rule", "value") in found
    assert ("file", "holds") in found
    assert ("file", "holds", "when") in found, "a row may name more than one tuple"
    assert ("never", "read") not in found, "only the Canonical tables section counts"


def test_the_real_schema_still_names_its_column_sets() -> None:
    """An empty set would let every table through while the audit still exited 0."""
    found = audit.canonical_columns((REPO / audit.SCHEMA).read_text(encoding="utf-8"))
    assert ("anti-pattern", "use instead", "why (one clause)", "reference") in found
    assert len(found) >= 10


# ----------------------------------------------------------------- the checks


def test_a_table_shape_the_schema_does_not_name_fails(tmp_path) -> None:
    """Nine invented shapes in one file is what this exists to catch."""
    root = _repo(tmp_path, "# T\n\n| key | value |\n|---|---|\n| a | b |\n")
    fails, _ = audit.check_table_columns(root)
    assert len(fails) == 1 and "key | value" in fails[0]


def test_a_canonical_table_passes_whatever_its_case(tmp_path) -> None:
    """Headings are written for a reader, so matching ignores case and backticks."""
    root = _repo(tmp_path, "# T\n\n| Rule | `Value` |\n|---|---|\n| a | b |\n")
    assert audit.check_table_columns(root) == ([], [])


def test_a_pipe_inside_a_fence_is_not_a_table(tmp_path) -> None:
    """A code block full of pipes would otherwise read as a wall of bad tables."""
    root = _repo(tmp_path, "# T\n\n```\n| key | value |\n|---|---|\n```\n")
    assert audit.check_table_columns(root) == ([], [])


def test_a_paragraph_fails_and_a_lead_in_does_not(tmp_path) -> None:
    """The core rule: every block is a labelled field or a table row."""
    lead_in = "# T\n\n" + "one line about the step.\n" * audit.MAX_PROSE_RUN
    assert audit.check_no_prose_blocks(_repo(tmp_path, lead_in)) == ([], [])

    blob = "# T\n\n" + "a line of prose.\n" * (audit.MAX_PROSE_RUN + 1)
    fails, _ = audit.check_no_prose_blocks(_repo(tmp_path, blob))
    assert len(fails) == 1 and "consecutive" in fails[0]


def test_frontmatter_is_not_prose(tmp_path) -> None:
    """A router's YAML block is metadata, and the schema's folded description is ten lines.

    A three-field block was exactly `MAX_PROSE_RUN` lines of "prose" — `---`, two fields,
    `---` — so it passed by coincidence, and the TRIGGER/SYMPTOMS form the schema asks for
    failed the moment it was written. The block is delimited; it is classified as such.
    """
    root = _repo(tmp_path, "# T\n")
    router = root / "plugins/ha/skills/demo/SKILL.md"
    router.write_text(
        "---\nname: demo\ndescription: >-\n  Use when demoing.\n  TRIGGER WHEN:\n"
        "  - asked\n  - told\n  SYMPTOMS:\n  - a demo\n  - another\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    assert audit.check_no_prose_blocks(root) == ([], [])
    kinds = {kind for _, kind, _ in audit.classify(router.read_text(encoding="utf-8"))}
    assert "frontmatter" in kinds and "prose" not in kinds

    # A `---` that is not at the top of the file is a rule, not a block opener.
    router.write_text("# Demo\n\ntext\n\n---\n\nmore\n", encoding="utf-8")
    kinds = [kind for _, kind, _ in audit.classify(router.read_text(encoding="utf-8"))]
    assert "frontmatter" not in kinds


def test_a_bullet_that_runs_to_a_paragraph_is_prose_wearing_a_dash(tmp_path) -> None:
    """The schema's wording; the wrapped continuations carry no marker of their own."""
    body = "# T\n\n- the bullet starts here\n" + "  and wraps, and wraps.\n" * 6
    fails, _ = audit.check_no_prose_blocks(_repo(tmp_path, body))
    assert len(fails) == 1


def test_a_contents_list_that_misses_a_heading_fails(tmp_path) -> None:
    """A list that has to be maintained by hand is a list that goes stale."""
    body = "# T\n\n## Contents\n\n1. One\n\n## One\n\n## Two\n"
    fails, _ = audit.check_contents_matches_headings(root := _repo(tmp_path, body))
    assert len(fails) == 1 and "not listed: two" in fails[0]

    good = "# T\n\n## Contents\n\n1. One\n2. Two\n\n## One\n\n## Two\n"
    assert audit.check_contents_matches_headings(_repo(tmp_path, good)) == ([], [])
    assert root == tmp_path


def test_a_file_with_no_contents_list_is_not_forced_to_grow_one(tmp_path) -> None:
    """The schema asks for one only where a file has more than three sections."""
    assert audit.check_contents_matches_headings(
        _repo(tmp_path, "# T\n\n## One\n\n## Two\n")
    ) == ([], [])


def test_steps_out_of_order_fail_and_restart_at_each_procedure(tmp_path) -> None:
    """A file with two procedures numbers each from 1, per the schema."""
    body = "# T\n\n## A\n\n### Step 1: x\n\n### Step 3: y\n"
    fails, _ = audit.check_step_numbering(_repo(tmp_path, body))
    assert len(fails) == 1 and "is Step 3, expected Step 2" in fails[0]

    two = "# T\n\n## A\n\n### Step 1: x\n\n## B\n\n### Step 1: y\n\n### Step 2: z\n"
    assert audit.check_step_numbering(_repo(tmp_path, two)) == ([], [])


def test_the_block_caps_are_read_from_the_schema_not_from_the_code() -> None:
    """The *Written as* column states each cap; the checker must not carry its own copy."""
    caps = audit.block_caps(SCHEMA)
    assert caps["note"] == 3
    assert caps["symptom"] == audit.MAX_PROSE_RUN, "a one-line block may still wrap"
    assert caps["fix"] == audit.MAX_PROSE_RUN
    assert "row" not in caps, "a table line carries no label to measure"


def test_the_real_schema_still_names_its_block_caps() -> None:
    """An empty map would let every paragraph-length block through, silently."""
    caps = audit.block_caps((REPO / audit.SCHEMA).read_text(encoding="utf-8"))
    assert caps["note"] == 3
    assert {"symptom", "timing", "fix"} <= set(caps)


def test_a_note_longer_than_the_schema_allows_fails(tmp_path) -> None:
    """`> **Note:**` is capped at three lines by the *Block types* table itself."""
    body = "# T\n\n> **Note:** one\n> two\n> three\n"
    assert audit.check_labelled_block_length(_repo(tmp_path, body)) == ([], [])

    body = "# T\n\n> **Note:** one\n> two\n> three\n> four\n"
    fails, _ = audit.check_labelled_block_length(_repo(tmp_path, body))
    assert len(fails) == 1 and "runs 4 lines" in fails[0]


def test_a_labelled_one_liner_may_wrap_but_not_become_a_paragraph(tmp_path) -> None:
    """A wrapped line is still one line; a `**Fix:**` of six is a paragraph with a label."""
    wrapped = "# T\n\n**Fix:** the fix starts here\n" + "and wraps.\n" * (
        audit.MAX_PROSE_RUN - 1
    )
    assert audit.check_labelled_block_length(_repo(tmp_path, wrapped)) == ([], [])

    paragraph = "# T\n\n**Fix:** the fix starts here\n" + "and wraps.\n" * 5
    fails, _ = audit.check_labelled_block_length(_repo(tmp_path, paragraph))
    assert len(fails) == 1 and "**Fix:**" in fails[0]


def test_a_block_ends_at_the_next_block_rather_than_swallowing_it(tmp_path) -> None:
    """Two labels in a row are two blocks; a table or a fence ends one as a blank line does."""
    body = "# T\n\n**Symptom:** one\n**Fix:** two\n\n| Rule | Value |\n|---|---|\n| a | b |\n"
    assert audit.check_labelled_block_length(_repo(tmp_path, body)) == ([], [])


# ------------------------------------------------------ the committed artefact


def test_every_committed_skill_file_matches_the_schema() -> None:
    """What `ci.yml` runs, run here too, so a local pytest catches the drift first."""
    failures = [f for check in audit.CHECKS for f in check(REPO)[0]]
    assert not failures, "\n".join(failures)
