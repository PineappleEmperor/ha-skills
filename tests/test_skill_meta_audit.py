"""Unit tests for scripts/skill_meta_audit.py — the authoring checks.

These live apart from test_skill_audit.py for the same reason the scripts do: nothing
here can fire in a scaffolded integration, so nothing here ships to one.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location("skill_meta_audit", _SCRIPTS / "skill_meta_audit.py")
audit = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(audit)


def _skill(root, name, frontmatter, body="body\n"):
    d = root / "plugins/ha/skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n{body}")


def test_docs_naming_a_dead_job_fails(tmp_path) -> None:
    """`commit-summary` was deleted from pr-checks.yml; six passages still described it."""
    skill = tmp_path / "plugins/ha/skills/ha-integration"
    wfs = skill / "templates/.github/workflows"
    wfs.mkdir(parents=True)
    (wfs / "pr-checks.yml").write_text("jobs:\n  label:\n    steps: []\n")
    (skill / "reference").mkdir()
    (skill / "SKILL.md").write_text("the `pr-checks.yml` workflow runs on every PR\n")
    (skill / "reference/github-actions.md").write_text(
        "| Job | `needs:` | Does |\n|---|---|---|\n"
        "| `label` | — | labels |\n| `commit-summary` | — | writes the body |\n")

    fails, _ = audit.check_docs_match_templates(audit.Repo(tmp_path))
    assert any("commit-summary" in f for f in fails)
    assert not any("`label`" in f or ": label" in f for f in fails)

    # A workflow the docs name but the scaffold does not ship.
    (skill / "SKILL.md").write_text("run `cut_rc.yml` to mint a candidate\n")
    fails, _ = audit.check_docs_match_templates(audit.Repo(tmp_path))
    assert any("cut_rc.yml" in f for f in fails)


def test_docs_may_name_a_workflow_that_is_gone(tmp_path) -> None:
    """History and opt-in add-ons are documented on purpose, not drift."""
    skill = tmp_path / "plugins/ha/skills/ha-integration"
    (skill / "templates/.github/workflows").mkdir(parents=True)
    (skill / "reference").mkdir()
    (skill / "SKILL.md").write_text(
        "Superseded: `pr-labeler.yml` is folded into pr-checks.\n"
        "Historical note: `create-dev-pr.yml` raced the labeler.\n"
        "Add `update_manifest_floors.yml` when the manifest carries `>=` floors.\n")
    (skill / "reference/github-actions.md").write_text("")
    assert audit.check_docs_match_templates(audit.Repo(tmp_path)) == ([], [])


def test_skill_without_a_name_field_fails(tmp_path) -> None:
    """ha-panel-design shipped seven releases with no name in its frontmatter."""
    _skill(tmp_path, "ha-panel-design", "description: Use when changing a panel")
    fails, _ = audit.check_skill_frontmatter(audit.Repo(tmp_path))
    assert any("no name field" in f for f in fails)


def test_description_summarising_the_skill_fails(tmp_path) -> None:
    """A description that says what the skill does gets followed instead of the skill."""
    _skill(tmp_path, "ha-thing", "name: ha-thing\ndescription: Material 3 type scale and tokens")
    fails, _ = audit.check_skill_frontmatter(audit.Repo(tmp_path))
    assert any("must start with 'Use when'" in f for f in fails)


def test_name_must_match_its_directory(tmp_path) -> None:
    _skill(tmp_path, "ha-thing", "name: ha-other\ndescription: Use when doing a thing")
    fails, _ = audit.check_skill_frontmatter(audit.Repo(tmp_path))
    assert any("name field is 'ha-other'" in f for f in fails)


def test_valid_frontmatter_passes_and_size_only_warns(tmp_path) -> None:
    _skill(tmp_path, "ha-thing", "name: ha-thing\ndescription: Use when doing a thing",
           body="word " * 5001)
    fails, warns = audit.check_skill_frontmatter(audit.Repo(tmp_path))
    assert fails == []
    assert any("move heavy sections" in w for w in warns)


def test_reference_link_to_a_missing_file_fails(tmp_path) -> None:
    """A renamed reference file leaves the router pointing at nothing."""
    _skill(tmp_path, "ha-thing", "name: ha-thing\ndescription: Use when doing a thing",
           body="Read [scaffold](reference/scaffold.md) first.\n")
    fails, _ = audit.check_reference_links(audit.Repo(tmp_path))
    assert any("links reference/scaffold.md" in f for f in fails)


def test_orphan_reference_file_fails(tmp_path) -> None:
    """A reference file nothing links to is never read again."""
    _skill(tmp_path, "ha-thing", "name: ha-thing\ndescription: Use when doing a thing",
           body="No links here.\n")
    ref = tmp_path / "plugins/ha/skills/ha-thing/reference"
    ref.mkdir()
    (ref / "orphan.md").write_text("content\n")
    fails, _ = audit.check_reference_links(audit.Repo(tmp_path))
    assert any("orphan.md is linked from nothing" in f for f in fails)


def test_backticked_reference_counts_as_a_link(tmp_path) -> None:
    """The skill cites some references in backticks rather than as markdown links."""
    _skill(tmp_path, "ha-thing", "name: ha-thing\ndescription: Use when doing a thing",
           body="See `reference/patterns.md` for the rules.\n")
    ref = tmp_path / "plugins/ha/skills/ha-thing/reference"
    ref.mkdir()
    (ref / "patterns.md").write_text("content\n")
    assert audit.check_reference_links(audit.Repo(tmp_path)) == ([], [])

