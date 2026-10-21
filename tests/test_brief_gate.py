"""Unit tests for scripts/brief_gate.py, the hook that holds every build dispatch to a brief.

Load the standalone script by path; it is not an importable package.
"""

import hashlib
import importlib.util
import io
import json
import pathlib

import pytest

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location("brief_gate", _SCRIPTS / "brief_gate.py")
bg = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(bg)
_REAL_QUOTE_SOURCES = bg.quote_sources


@pytest.fixture(autouse=True)
def _no_reads_required(monkeypatch, tmp_path) -> None:
    """Shape tests get no read log and one stub source; later tests install their own."""
    monkeypatch.setattr(bg, "required_reads", lambda bodies: [])
    monkeypatch.setattr(bg, "READ_LOG", tmp_path / "reads.jsonl")
    source = tmp_path / "source.py"
    source.write_text('raise SystemExit(\n    "try\n    again")\n')
    monkeypatch.setattr(bg, "quote_sources", lambda bodies: [source])


_RULES_HEAD = "| Rule | Applies | How the plan meets it |\n|---|---|---|\n"


def _rules(extra: tuple[str, ...] = ()) -> str:
    """A rules table answering every invariant, plus an anti-patterns row per file."""
    rows = [
        f"| Invariant {n} | no | nothing in this change touches it |"
        for n in bg.invariants()
    ]
    rows += [f"| Anti-patterns: {path} | yes | read; none applies |" for path in extra]
    return _RULES_HEAD + "\n".join(rows)


_TEMPLATE = """\
# Brief: retry every transient download failure

## Goal

The sync script survives a flaky network and says plainly when a tag does not exist.

## Repository

/home/juicebox/ha-integration-ci on feat/mypy-gate

## Sources read

- scripts/pylint_upstream.py (in full)
- tests/test_pylint_upstream.py (in full)
- https://raw.githubusercontent.com/home-assistant/core/2026.9.0/pylint/plugins/hass_imports.py (in full)

## Defect class

Every failure that could succeed on a second attempt is retried; every failure that cannot
stops at once with a message that says why.

## Facts

| ID | Fact | Owner | Pointers |
|---|---|---|---|
| F1 | a 404 means the tag does not exist, so a retry cannot help | scripts/pylint_upstream.py › module docstring | README.md › The pylint rules |
| F2 | a 5xx is transient, so a retry can help | scripts/pylint_upstream.py › module docstring | README.md › The pylint rules |

## Rules applied

<<RULES>>

## Cases

| # | Kind | Situation | Facts | Expected | Proof | Seen |
|---|---|---|---|---|---|---|
| 1 | reported | codeload answers 404 | F1 | stops at once, says the tag may not exist | test_404_stops | today: three attempts, then "try again" |
| 2 | sibling | codeload answers 503 | F2 | retried | test_503_retried | today: not retried |
| 3 | guard | a good download | F2 | one attempt, no wait | test_success_no_retry | today: one attempt |

## Files

- scripts/pylint_upstream.py
- tests/test_pylint_upstream.py

## Out of scope

The download URL and the tarball layout; neither changes.

## Commits

- fix: retry every transient download failure

## Checks

```
python -m pytest tests/ -q -p no:homeassistant
```

## Stop and report if

- a failure cannot be told apart from a transient one by its type
"""
VALID = _TEMPLATE.replace("<<RULES>>", _rules())


def _write(
    tmp_path: pathlib.Path, text: str, verdict: str | None = "complete"
) -> pathlib.Path:
    """Write a brief and, unless verdict is None, a review of its current bytes."""
    brief = tmp_path / "b.md"
    brief.write_text(text)
    if verdict is not None:
        digest = hashlib.sha256(text.encode()).hexdigest()
        (tmp_path / "b.review").write_text(f"{digest}\nVERDICT: {verdict}\n")
    return brief


def _agent(brief: pathlib.Path | None, subagent: str = "general-purpose") -> dict:
    prompt = f"Brief: {brief}" if brief else "Fix the retry in the sync script."
    return {
        "tool_name": "Agent",
        "tool_input": {"prompt": prompt, "subagent_type": subagent},
    }


def test_a_complete_reviewed_brief_passes(tmp_path) -> None:
    """The reported shape: every section, every kind of case, a matching review."""
    assert bg.decide(_agent(_write(tmp_path, VALID))) is None


def test_a_builder_without_a_brief_is_refused() -> None:
    """A prose prompt is exactly what produced narrow fixes; it names the schema file."""
    reason = bg.decide(_agent(None))
    assert reason is not None
    assert "docs/brief.md" in reason


def test_an_omitted_subagent_type_is_a_builder() -> None:
    """The Agent tool defaults to general-purpose, which can write files."""
    payload = {"tool_name": "Agent", "tool_input": {"prompt": "Fix it."}}
    assert bg.decide(payload) is not None


@pytest.mark.parametrize(
    "subagent", ["reviewer", "Explore", "Plan", "claude-code-guide"]
)
def test_a_read_only_agent_needs_no_brief(subagent) -> None:
    """Reviewers and searchers change nothing, so there is nothing to brief."""
    assert bg.decide(_agent(None, subagent)) is None


def test_a_brief_that_does_not_exist_is_refused(tmp_path) -> None:
    """A path that names no file is refused by name, not silently allowed."""
    reason = bg.decide(_agent(tmp_path / "nope.md"))
    assert reason is not None
    assert "nope.md" in reason


@pytest.mark.parametrize("section", bg.SECTIONS)
def test_every_missing_section_is_named(tmp_path, section) -> None:
    """Each section is required; the refusal says which one is absent."""
    head = f"## {section}\n"
    start = VALID.index(head)
    nxt = VALID.find("\n## ", start + len(head))
    text = VALID[:start] + (VALID[nxt + 1 :] if nxt != -1 else "")
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert section in reason


def test_sections_out_of_order_are_refused(tmp_path) -> None:
    """The order is fixed so a reader finds each section where the schema puts it."""
    text = VALID.replace("## Goal", "## Tmp").replace("## Repository", "## Goal")
    text = text.replace("## Tmp", "## Repository")
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "order" in reason


def test_invariants_are_read_from_the_review_standard() -> None:
    """The planning checklist is docs/review.md's, so a new invariant binds briefs too."""
    found = bg.invariants()
    assert found == list(range(1, len(found) + 1))
    assert len(found) >= 10


def test_each_invariant_names_the_documents_it_checks_against() -> None:
    """The documents come from docs/review.md's own wording, not a copy of it."""
    named = bg.invariant_sources()
    assert "docs/skill-file-hierarchy.md" in named[2]
    assert "docs/skill-schema.md" in named[10]


def test_an_invariant_names_files_of_any_type() -> None:
    """Invariants 7 and 10 name a settings file and a script, not only documents."""
    named = bg.invariant_sources()
    assert ".claude/settings.json" in named[7]
    assert "scripts/skill_schema_audit.py" in named[10]


def test_a_backticked_name_that_is_no_file_is_not_a_source() -> None:
    """`breaks_in_ha_version` and a URL template are words, not files to read."""
    named = [doc for docs in bg.invariant_sources().values() for doc in docs]
    assert all((bg.ROOT / doc).is_file() for doc in named)


def test_an_invariant_answered_yes_needs_its_documents_read(tmp_path) -> None:
    """Invariant 10 answered without reading docs/skill-schema.md was a real miss."""
    text = VALID.replace(
        "| Invariant 10 | no | nothing in this change touches it |",
        "| Invariant 10 | yes | every table keeps its columns |",
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "docs/skill-schema.md" in reason
    text = text.replace(
        "- scripts/pylint_upstream.py (in full)\n",
        "- scripts/pylint_upstream.py (in full)\n- docs/skill-schema.md (in full)\n"
        "- scripts/skill_schema_audit.py (in full)\n",
    )
    assert bg.decide(_agent(_write(tmp_path, text))) is None


def test_every_invariant_needs_a_row(tmp_path) -> None:
    """A rule the plan never weighed is the finding a review would make later."""
    text = VALID.replace(
        "| Invariant 3 | no | nothing in this change touches it |\n", ""
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "Invariant 3" in reason


def test_applies_is_yes_or_no(tmp_path) -> None:
    """A rule either shapes the plan or it does not; maybe is an unmade decision."""
    text = VALID.replace("| Invariant 2 | no |", "| Invariant 2 | maybe |")
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "maybe" in reason


def test_a_rule_row_names_how_it_is_met(tmp_path) -> None:
    """A bare yes or no is a box ticked, not a rule applied."""
    text = VALID.replace(
        "| Invariant 4 | no | nothing in this change touches it |",
        "| Invariant 4 | yes |  |",
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "Invariant 4" in reason


def test_a_rules_table_with_other_columns_is_refused(tmp_path) -> None:
    """The columns are fixed so every rule says whether and how it applies."""
    text = VALID.replace(
        "| Rule | Applies | How the plan meets it |", "| Rule | Note |"
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "Rules applied" in reason


def test_a_shipped_file_needs_its_anti_patterns_weighed(tmp_path) -> None:
    """Each skill file the change touches carries rules of its own; the plan reads them."""
    shipped = "plugins/ha/skills/ha-integration/reference/testing.md"
    text = VALID.replace(
        "- tests/test_pylint_upstream.py\n",
        f"- tests/test_pylint_upstream.py\n- {shipped} (edited)\n",
    ).replace(
        "- tests/test_pylint_upstream.py (in full)\n",
        f"- tests/test_pylint_upstream.py (in full)\n- {shipped} (in full)\n",
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert shipped in reason
    text = text.replace(_rules(), _rules((shipped,)))
    assert bg.decide(_agent(_write(tmp_path, text))) is None


def test_every_file_changed_is_read_first(tmp_path) -> None:
    """A brief written before reading what it changes is how round one missed things."""
    text = VALID.replace("- tests/test_pylint_upstream.py (in full)\n", "")
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "tests/test_pylint_upstream.py" in reason


def test_a_new_file_needs_no_reading(tmp_path) -> None:
    """A file the change creates has nothing to read yet."""
    text = VALID.replace(
        "- tests/test_pylint_upstream.py\n",
        "- tests/test_pylint_upstream.py\n- scripts/new_helper.py (new)\n",
    )
    assert bg.decide(_agent(_write(tmp_path, text))) is None


def test_every_case_records_what_was_seen(tmp_path) -> None:
    """A case is an observation made while planning, not a prediction written as fact."""
    text = VALID.replace("| today: not retried |", "|  |")
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "Seen" in reason


def test_a_quote_the_sources_do_not_hold_is_refused(tmp_path) -> None:
    """A `today:` quote is copied from a file read, never paraphrased from memory."""
    text = VALID.replace('"try again"', '"try later"')
    _refused_with(tmp_path, text, "case 1", "try later")


def test_a_quote_wrapped_across_lines_in_its_source_passes(tmp_path) -> None:
    """Line breaks and indentation in the source are not part of what it says."""
    assert bg.decide(_agent(_write(tmp_path, VALID))) is None


def test_a_quote_may_hold_a_semicolon(monkeypatch, tmp_path) -> None:
    """A semicolon inside the quotes is quoted text, not the end of the `today:` part."""
    source = tmp_path / "semi.md"
    source.write_text("does not fix this; neither\ndoes `pythonpath`.\n")
    monkeypatch.setattr(bg, "quote_sources", lambda bodies: [source])
    text = VALID.replace(
        '"try again"', '"does not fix this; neither does `pythonpath`"'
    )
    assert bg.decide(_agent(_write(tmp_path, text))) is None


def test_quotes_outside_the_today_part_are_not_checked(tmp_path) -> None:
    """Tool output a case observed is quoted after the `today:` part, not from a file."""
    text = VALID.replace(
        '| today: three attempts, then "try again" |',
        '| today: three attempts, then "try again"; the run: "All checks passed!" |',
    )
    assert bg.decide(_agent(_write(tmp_path, text))) is None


def test_quote_sources_are_the_local_files_under_sources_read(tmp_path) -> None:
    """The quotes are checked against what the brief says it read, and nothing else."""
    source = tmp_path / "script.py"
    source.write_text("y\n")
    bodies = {
        "Repository": f"{tmp_path} on main",
        "Sources read": "- script.py (in full)\n- https://example.com/a.py (in full)",
    }
    assert _REAL_QUOTE_SOURCES(bodies) == [source]


@pytest.mark.parametrize(
    "section", ["Goal", "Defect class", "Rules applied", "Files", "Out of scope"]
)
def test_an_empty_section_is_refused(tmp_path, section) -> None:
    """A heading with nothing under it is not the section."""
    head = f"## {section}\n"
    start = VALID.index(head) + len(head)
    nxt = VALID.index("\n## ", start)
    text = VALID[:start] + "\n" + VALID[nxt:]
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert section in reason


def test_a_source_not_read_in_full_is_refused(tmp_path) -> None:
    """A source skimmed is not a source read; every bullet says it was read whole."""
    text = VALID.replace(
        "- scripts/pylint_upstream.py (in full)", "- scripts/pylint_upstream.py"
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "(in full)" in reason


def test_core_without_a_core_source_at_a_tag_is_refused(tmp_path) -> None:
    """The tests/ruff.toml miss: a change that mirrors core names the core file it read."""
    text = VALID.replace(
        "- https://raw.githubusercontent.com/home-assistant/core/2026.9.0/"
        "pylint/plugins/hass_imports.py (in full)\n",
        "",
    ).replace("Every failure", "As core does, every failure")
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "core" in reason


def test_a_brief_that_never_mentions_core_needs_no_core_source(tmp_path) -> None:
    """The core rule applies only where the brief invokes core."""
    text = VALID.replace(
        "- https://raw.githubusercontent.com/home-assistant/core/2026.9.0/"
        "pylint/plugins/hass_imports.py (in full)\n",
        "",
    )
    assert "core" not in text.lower().replace("codeload", "")
    assert bg.decide(_agent(_write(tmp_path, text))) is None


def test_the_schemas_core_rule_is_not_home_assistant_core(tmp_path) -> None:
    """`core rule` is docs/skill-schema.md's term for a file's bold line."""
    text = VALID.replace(
        "- https://raw.githubusercontent.com/home-assistant/core/2026.9.0/"
        "pylint/plugins/hass_imports.py (in full)\n",
        "",
    ).replace("Every failure", "Per the file's core rule, every failure")
    assert bg.decide(_agent(_write(tmp_path, text))) is None


@pytest.mark.parametrize("kind", ["reported", "sibling", "guard"])
def test_every_case_kind_is_required(tmp_path, kind) -> None:
    """A brief with no sibling case is the narrow patch; with no guard, the regression."""
    others = [k for k in ("reported", "sibling", "guard") if k != kind]
    text = VALID.replace(f"| {kind} |", f"| {others[0]} |")
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert kind in reason


def test_an_unknown_case_kind_is_refused(tmp_path) -> None:
    """A kind outside the three is a typo or an invention, not a case."""
    text = VALID.replace("| 3 | guard |", "| 3 | guard |\n| 4 | maybe |")
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "maybe" in reason


def test_a_cases_table_with_other_columns_is_refused(tmp_path) -> None:
    """The columns are fixed so every case names its situation, result and proof."""
    text = VALID.replace(
        "| # | Kind | Situation | Facts | Expected | Proof | Seen |",
        "| # | Kind | What |",
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "Cases" in reason


def _refused_with(tmp_path, text: str, *needles: str) -> None:
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    for needle in needles:
        assert needle in reason


def test_a_facts_table_with_other_columns_is_refused(tmp_path) -> None:
    """Every fact carries its ID, its owner and its pointers, in that shape."""
    text = VALID.replace("| ID | Fact | Owner | Pointers |", "| Fact | Owner |")
    _refused_with(tmp_path, text, "Facts")


def test_a_fact_id_used_twice_is_refused(tmp_path) -> None:
    """Two rows under one ID are two facts a citation cannot tell apart."""
    text = VALID.replace("| F2 | a 5xx", "| F1 | a 5xx")
    _refused_with(tmp_path, text, "F1")


def test_the_same_claim_twice_is_refused(tmp_path) -> None:
    """One fact, one row: a second row saying the same thing is a restatement."""
    text = VALID.replace(
        "a 5xx is transient, so a retry can help",
        "a 404 means the tag does not exist, so a retry cannot help",
    )
    _refused_with(tmp_path, text, "same claim")


def test_a_fact_with_no_owner_is_refused(tmp_path) -> None:
    """A fact nobody owns is the drift the owner column exists to stop."""
    text = VALID.replace(
        "| F2 | a 5xx is transient, so a retry can help | "
        "scripts/pylint_upstream.py › module docstring |",
        "| F2 | a 5xx is transient, so a retry can help |  |",
    )
    _refused_with(tmp_path, text, "F2", "owner")


def test_a_case_citing_an_unknown_fact_is_refused(tmp_path) -> None:
    """A citation must resolve, or the case rests on nothing written down."""
    text = VALID.replace(
        "| 2 | sibling | codeload answers 503 | F2 |",
        "| 2 | sibling | codeload answers 503 | F9 |",
    )
    _refused_with(tmp_path, text, "F9")


def test_a_case_citing_no_fact_is_refused(tmp_path) -> None:
    """A case proves a fact; one that cites none has an expectation from nowhere."""
    text = VALID.replace(
        "| 2 | sibling | codeload answers 503 | F2 |",
        "| 2 | sibling | codeload answers 503 |  |",
    )
    _refused_with(tmp_path, text, "case 2")


def test_a_fact_no_case_proves_is_refused(tmp_path) -> None:
    """A fact nothing proves is a claim the build will not check."""
    text = VALID.replace(
        "| F2 | a 5xx",
        "| F3 | a success needs one attempt | scripts/pylint_upstream.py › main "
        "| none |\n| F2 | a 5xx",
    )
    _refused_with(tmp_path, text, "F3")


def test_an_undefined_fact_cited_anywhere_is_refused(tmp_path) -> None:
    """A rules cell citing a fact the table lacks is as broken as a case doing so."""
    text = VALID.replace(
        "| Invariant 6 | no | nothing in this change touches it |",
        "| Invariant 6 | yes | F7 is observed in its case |",
    )
    _refused_with(tmp_path, text, "F7")


def test_an_escaped_pipe_stays_inside_its_cell(tmp_path) -> None:
    """A Facts cell holding an escaped pipe crashed the gate with too many values to unpack."""
    text = VALID.replace("so a retry can help |", "so a retry can help \\| twice |")
    assert bg.decide(_agent(_write(tmp_path, text))) is None


@pytest.mark.parametrize(
    ("old", "new", "row", "cells"),
    [
        ("so a retry can help |", "so a retry can help | twice |", "F2", "5 cells"),
        ("| retried |", "| retried | twice |", "case 2", "8 cells"),
        (
            "| Invariant 4 | no | nothing in this change touches it |",
            "| Invariant 4 | no | nothing | in this change |",
            "Invariant 4",
            "4 cells",
        ),
    ],
)
def test_a_row_with_a_stray_pipe_is_refused_not_crashed(
    tmp_path, old, new, row, cells
) -> None:
    """An unescaped pipe splits a cell, in any table; the gate says so rather than raising."""
    _refused_with(tmp_path, VALID.replace(old, new), row, cells)


def test_an_escaped_pipe_ending_the_last_cell_survives() -> None:
    """Only the row's own closing pipe is stripped, not an escaped one just before it."""
    assert bg._table("| a | b |\n|---|---|\n| F1 | ends \\||") == (
        ["a", "b"],
        [["F1", "ends |"]],
    )


def test_checks_without_a_fenced_block_are_refused(tmp_path) -> None:
    """The commands are copyable exactly as the builder will run them."""
    text = VALID.replace(
        "```\npython -m pytest tests/ -q -p no:homeassistant\n```", "run the tests"
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "Checks" in reason


def test_an_unreviewed_brief_is_refused(tmp_path) -> None:
    """No builder starts before a reviewer has asked whether a case is missing."""
    reason = bg.decide(_agent(_write(tmp_path, VALID, verdict=None)))
    assert reason is not None
    assert "case review" in reason


def test_a_review_of_an_earlier_version_is_refused(tmp_path) -> None:
    """Editing a brief after its review invalidates the review."""
    brief = _write(tmp_path, VALID)
    brief.write_text(VALID.replace("survives a flaky", "survives any flaky"))
    reason = bg.decide(_agent(brief))
    assert reason is not None
    assert "sha256" in reason


def test_a_review_that_found_missing_cases_is_refused(tmp_path) -> None:
    """A review that found gaps blocks the build until the brief is fixed."""
    reason = bg.decide(_agent(_write(tmp_path, VALID, verdict="missing")))
    assert reason is not None
    assert "missing" in reason


def test_every_problem_is_reported_at_once(tmp_path) -> None:
    """One refusal lists them all, so a brief is not fixed one round-trip at a time."""
    text = VALID.replace("(in full)", "").replace("| guard |", "| sibling |")
    reason = bg.decide(_agent(_write(tmp_path, text, verdict=None)))
    assert reason is not None
    assert "(in full)" in reason
    assert "guard" in reason
    assert "case review" in reason


_REAL_REQUIRED_READS = bg.required_reads


def _log_read(path: pathlib.Path, session: str = "s1", full: bool = True) -> None:
    """Append a read of path, at its current content, to the gate's read log."""
    entry = {
        "session": session,
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "full": full,
    }
    with bg.READ_LOG.open("a") as log:
        log.write(json.dumps(entry) + "\n")


def _needs(monkeypatch, tmp_path) -> tuple[pathlib.Path, dict]:
    """A brief that requires one corpus file read, and the dispatch that sends it."""
    corpus_file = tmp_path / "skill.md"
    corpus_file.write_text("the rule\n")
    monkeypatch.setattr(bg, "required_reads", lambda bodies: [corpus_file])
    payload = _agent(_write(tmp_path, VALID))
    payload["session_id"] = "s1"
    return corpus_file, payload


def test_a_file_never_read_is_refused(monkeypatch, tmp_path) -> None:
    """Planning from memory of a file is what the read log exists to stop."""
    corpus_file, payload = _needs(monkeypatch, tmp_path)
    reason = bg.decide(payload)
    assert reason is not None
    assert str(corpus_file) in reason


def test_a_whole_read_in_this_session_passes(monkeypatch, tmp_path) -> None:
    """The one read that counts: the whole file, at its current content, this session."""
    corpus_file, payload = _needs(monkeypatch, tmp_path)
    _log_read(corpus_file)
    assert bg.decide(payload) is None


def test_a_read_in_another_session_is_refused(monkeypatch, tmp_path) -> None:
    """A read from an earlier session is memory, not reading."""
    corpus_file, payload = _needs(monkeypatch, tmp_path)
    _log_read(corpus_file, session="old")
    assert bg.decide(payload) is not None


def test_a_partial_read_is_refused(monkeypatch, tmp_path) -> None:
    """A slice of a file is a search result, not a read."""
    corpus_file, payload = _needs(monkeypatch, tmp_path)
    _log_read(corpus_file, full=False)
    assert bg.decide(payload) is not None


def test_a_file_changed_since_it_was_read_is_refused(monkeypatch, tmp_path) -> None:
    """What was read is no longer what is there."""
    corpus_file, payload = _needs(monkeypatch, tmp_path)
    _log_read(corpus_file)
    corpus_file.write_text("the rule, changed\n")
    reason = bg.decide(payload)
    assert reason is not None
    assert str(corpus_file) in reason


def test_required_reads_add_every_local_source_to_the_corpus(
    monkeypatch, tmp_path
) -> None:
    """A source the brief cites is read too; a URL is not a local file."""
    corpus_file = tmp_path / "skill.md"
    corpus_file.write_text("x\n")
    source = tmp_path / "script.py"
    source.write_text("y\n")
    monkeypatch.setattr(bg, "corpus", lambda: [corpus_file])
    bodies = {
        "Repository": f"{tmp_path} on main",
        "Sources read": "- script.py (in full)\n- https://example.com/a.py (in full)",
    }
    assert _REAL_REQUIRED_READS(bodies) == [corpus_file, source]


def test_the_corpus_is_the_whole_skill_and_what_governs_it() -> None:
    """Every shipped text file, the governing docs and the CI READMEs; no search."""
    names = {str(path) for path in bg.corpus()}
    skill = bg.ROOT / "plugins/ha/skills/ha-integration"
    for expected in (
        skill / "SKILL.md",
        skill / "reference/testing.md",
        skill / "templates/pyproject.toml",
        bg.ROOT / "docs/review.md",
        bg.ROOT / "docs/skill-schema.md",
    ):
        assert str(expected) in names
    assert not any(name.endswith(".png") for name in names)
    assert not any("_cache/" in name for name in names), "untracked tool caches"


def _workflow(script: str) -> dict:
    return {"tool_name": "Workflow", "tool_input": {"script": script}}


def test_a_workflow_naming_no_brief_is_refused() -> None:
    """A workflow that builds names the briefs its agents work from."""
    reason = bg.decide(_workflow("await agent('fix the retry')"))
    assert reason is not None
    assert "brief" in reason


def test_a_read_only_workflow_may_say_so() -> None:
    """A workflow of reviewers only changes nothing; the marker is visible in the script."""
    script = "// brief-gate: read-only\nawait agent('review', {agentType: 'reviewer'})"
    assert bg.decide(_workflow(script)) is None


def test_a_workflow_is_held_to_every_brief_it_names(tmp_path) -> None:
    """One bad brief among good ones refuses the whole workflow."""
    good = _write(tmp_path, VALID)
    bad = tmp_path / "bad.md"
    bad.write_text("# Brief: nothing\n")
    assert bg.decide(_workflow(f"agent('Brief: {good}')")) is None
    reason = bg.decide(_workflow(f"agent('Brief: {good}'); agent('Brief: {bad}')"))
    assert reason is not None
    assert "bad.md" in reason


def test_a_workflow_by_script_path_is_read_from_disk(tmp_path) -> None:
    """A workflow passed by path is read from disk and held to the same rule."""
    script = tmp_path / "wf.js"
    script.write_text("await agent('fix it')")
    payload = {"tool_name": "Workflow", "tool_input": {"scriptPath": str(script)}}
    assert bg.decide(payload) is not None


def _run(monkeypatch, capsys, raw: str) -> dict | None:
    monkeypatch.setattr("sys.stdin", io.StringIO(raw))
    assert bg.main() == 0
    out = capsys.readouterr().out
    return json.loads(out) if out else None


def test_the_hook_denies_with_the_reason(monkeypatch, capsys) -> None:
    """The refusal reaches the agent as a deny that names the schema file."""
    out = _run(monkeypatch, capsys, json.dumps(_agent(None)))
    assert out is not None
    decision = out["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "docs/brief.md" in decision["permissionDecisionReason"]


def test_the_hook_stays_silent_when_allowed(monkeypatch, capsys) -> None:
    """No output means allow; a hook that prints on the happy path is noise."""
    assert _run(monkeypatch, capsys, json.dumps(_agent(None, "reviewer"))) is None
    assert _run(monkeypatch, capsys, json.dumps({"tool_name": "Bash"})) is None


def test_unparseable_input_is_not_grounds_to_block(monkeypatch, capsys) -> None:
    """A payload the hook cannot read is the harness's problem, not a reason to block."""
    assert _run(monkeypatch, capsys, "not json") is None
