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
- https://raw.githubusercontent.com/home-assistant/core/2026.9.0/pylint/plugins/hass_imports.py (in full)

## Defect class

Every failure that could succeed on a second attempt is retried; every failure that cannot
stops at once with a message that says why.

## Rules applied

<<RULES>>

## Cases

| # | Kind | Situation | Expected | Proof |
|---|---|---|---|---|
| 1 | reported | codeload answers 404 | stops at once, says the tag may not exist | test_404_stops |
| 2 | sibling | codeload answers 503 | retried | test_503_retried |
| 3 | guard | a good download | one attempt, no wait | test_success_no_retry |

## Single source

| Fact | Owner | Pointers |
|---|---|---|
| which failures are retried | scripts/pylint_upstream.py › module docstring | README.md › The pylint rules |

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
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert shipped in reason
    text = text.replace(_rules(), _rules((shipped,)))
    assert bg.decide(_agent(_write(tmp_path, text))) is None


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
        "| # | Kind | Situation | Expected | Proof |", "| # | Kind | What |"
    )
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "Cases" in reason


def test_single_source_accepts_the_no_fact_line(tmp_path) -> None:
    """A change that moves no fact says so in one line."""
    start = VALID.index("| Fact |")
    end = VALID.index("\n## Files")
    text = VALID[:start] + "No fact introduced or moved.\n" + VALID[end:]
    assert bg.decide(_agent(_write(tmp_path, text))) is None


def test_single_source_with_neither_form_is_refused(tmp_path) -> None:
    """A vague owner is the restatement the table exists to prevent."""
    start = VALID.index("| Fact |")
    end = VALID.index("\n## Files")
    text = VALID[:start] + "The docstring, I think.\n" + VALID[end:]
    reason = bg.decide(_agent(_write(tmp_path, text)))
    assert reason is not None
    assert "Single source" in reason


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
