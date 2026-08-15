"""Unit tests for scripts/commit_summary.py.

Load the standalone script by path — it is not an importable package.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "commit_summary",
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "commit_summary.py",
)
cs = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(cs)


# --- classify ---------------------------------------------------------------

@pytest.mark.parametrize(
    ("subject", "group", "desc"),
    [
        ("feat: add reconfigure flow", "feat", "add reconfigure flow"),
        ("feature: add thing", "feat", "add thing"),
        ("fix: close the session", "fix", "close the session"),
        ("chore: tidy", "maint", "tidy"),
        ("docs: explain", "maint", "explain"),
        ("refactor: split api.py", "maint", "split api.py"),
        ("perf: cache lookups", "maint", "cache lookups"),
        ("test: cover unload", "maint", "cover unload"),
        ("build: pin ruff", "maint", "pin ruff"),
        ("ci: add pytest step", "maint", "add pytest step"),
        ("style: reformat", "maint", "reformat"),
        # Breaking wins over the base type, with or without a scope.
        ("feat!: drop create-dev-pr", "breaking", "drop create-dev-pr"),
        ("fix!: change the payload shape", "breaking", "change the payload shape"),
        ("chore(deps)!: require python 3.14", "breaking", "require python 3.14"),
        ("feat(coordinator): add polling", "feat", "add polling"),
        # `revert:` is Conventional but maps to no autolabeler rule.
        ("revert: undo the flow change", "other", "undo the flow change"),
        # Case-insensitive type.
        ("FEAT: shout", "feat", "shout"),
        ("Fix: capitalised", "fix", "capitalised"),
        # No space after the colon.
        ("feat:no space", "feat", "no space"),
        # Extra whitespace is trimmed.
        ("fix:   padded   ", "fix", "padded"),
        # Not Conventional Commits at all.
        ("Merge branch 'main' into feat/x", "other", "Merge branch 'main' into feat/x"),
        ("WIP", "other", "WIP"),
        ("", "other", ""),
        # A scope containing a colon still parses (the group is [^)]*).
        ("feat(a:b): scoped", "feat", "scoped"),
        # Empty description keeps the raw subject rather than rendering "- ".
        ("feat:", "other", "feat:"),
        ("chore: ", "other", "chore:"),
    ],
)
def test_classify(subject: str, group: str, desc: str) -> None:
    """Each subject lands in the expected group with a clean description."""
    assert cs.classify(subject) == (group, desc)


# --- the version-bump filter (the regression that shipped) ------------------

@pytest.mark.parametrize(
    "subject",
    [
        "chore: bump manifest version to v5.0.1",
        "chore: bump plugin version to 5.0.1",
        "chore: bump version to 5.0.1",
        "chore: bump the manifest version",
        "chore: bump integration version to 1.2.3",
        # The bare form the release workflow actually writes. It leaked into
        # Maintenance in the v7.0.1 draft because the pattern demanded the word
        # "version" after the noun.
        "chore: bump to 7.0.1",
        "chore: bump the ha plugin to 6.4.0",
    ],
)
def test_release_plumbing_is_dropped(subject: str) -> None:
    """The manifest/plugin bump is plumbing, not a changelog entry."""
    assert cs.group([subject, "fix: real change"]) ["maint"] == []


@pytest.mark.parametrize(
    "subject",
    [
        "chore: bump actions/checkout from 6 to 7",
        # The shipped regression: `to v?\d+\.\d+` ate every semver dependency bump.
        "chore: bump actions/checkout from 6.0.0 to 7.0.1",
        "chore: bump pytest-homeassistant-custom-component from 0.13.350 to 0.13.354",
        "chore: bump homeassistant floor to 2026.8.0",
        "chore(deps): bump aiohttp from 3.9.0 to 3.10.1",
    ],
)
def test_dependency_bumps_survive(subject: str) -> None:
    """Dependabot's bumps are real changes and must reach the notes."""
    assert cs.group([subject])["maint"] == [subject.split(": ", 1)[1]]


# --- render -----------------------------------------------------------------

def test_single_commit_renders_nothing() -> None:
    """One bullet is the PR title minus its prefix — the block would add nothing."""
    assert cs.render(["feat: add reconfigure flow"]) == ""
    assert cs.render(["fix: close the session"]) == ""


def test_two_commits_still_render() -> None:
    """The block earns its place as soon as it says more than the title."""
    assert cs.render(["fix: one", "fix: two"]) == "  - one\n  - two"


def test_single_type_has_no_subheads() -> None:
    """One type -> the category heading above already says it; no sub-head."""
    out = cs.render(["fix: one", "fix: two"])
    assert out == "  - one\n  - two"


def test_multiple_types_are_one_flat_list_in_severity_order() -> None:
    """No group labels: the release category above already names the PR.

    A label inside the entry repeats that heading four lines later, and on a PR
    spanning types it files fixes under Features. Measured at 3 of 8 merged PRs,
    so this is the common case, not the rare one.
    """
    out = cs.render(["chore: c", "fix: b", "feat!: a", "feat: d"])
    assert out.splitlines() == ["  - a", "  - d", "  - b", "  - c"]
    assert "**" not in out, f"group label leaked into the block:\n{out}"


def test_block_renders_as_a_list_not_a_paragraph() -> None:
    """The block must render as a list in BOTH places it appears.

    A plain indented line does not start a markdown list without a preceding blank
    line, so `  **Label**` + `  - item` collapsed into one run-on paragraph in a PR
    body. Blank lines fix that but break the release notes, where the block is
    inlined after `- $TITLE ...`. Only a nested list works in both.
    """
    # CommonMark, because that is what GitHub renders with. python-markdown needs
    # four spaces to nest a list where CommonMark needs two, so it reported this
    # block as broken when GitHub showed it fine, and fine when GitHub showed it
    # broken. A test against the wrong parser is worse than no test.
    MarkdownIt = pytest.importorskip("markdown_it").MarkdownIt
    md = MarkdownIt("commonmark")
    block = cs.render(["feat!: a", "feat: d", "fix: b", "chore: c"])

    standalone = md.render(block)
    assert "<li>" in standalone, f"PR body renders as a paragraph, not a list:\n{standalone}"

    nested = md.render(f"- feat: a title @dev (#1)\n{block}")
    assert nested.count("<ul>") > 1, f"release note does not nest the block:\n{nested}"


def test_a_bullet_never_restates_the_pr_title() -> None:
    """The title is the winning commit subject, so one bullet usually duplicates it."""
    subs = ["docs: describe the artefacts", "docs: lead with install"]
    out = cs.render(subs, title="docs: describe the artefacts")
    assert "describe the artefacts" not in out
    assert "lead with install" in out
    # If the only commit IS the title, the block says nothing and is dropped.
    assert cs.render(["fix: only change"], title="fix: only change") == ""


def test_every_line_keeps_its_indent() -> None:
    """No line may sit flush left.

    The block is spliced into a PR body and then inlined under release-drafter's
    `- $TITLE ...` bullet, so every line carries a two-space base indent. A bare
    .strip() in the splice step once removed it from the FIRST line only, leaving
    the opening label flush left while every later one stayed indented.
    """
    out = cs.render(["chore: c", "fix: b", "feat!: a"])
    for line in out.splitlines():
        assert line.startswith("  "), f"flush-left line: {line!r}"
    assert out.strip("\n") == out, "render must not emit leading/trailing blank lines"


def test_empty_and_plumbing_only_input() -> None:
    """A PR with nothing but a version bump renders a placeholder, not junk."""
    assert cs.render([]) == ""
    assert cs.render(["chore: bump manifest version to v1.0.0"]) == ""
    assert cs.render(["", "   ", ""]) == ""


def test_duplicate_subjects_collapse() -> None:
    """A rebase can replay an identical subject; don't list it twice.

    Collapsing to one bullet then makes the block redundant, so it renders empty.
    """
    assert cs.render(["fix: same", "fix: same"]) == ""
    assert cs.render(["fix: same", "fix: same", "fix: other"]) == "  - same\n  - other"


def test_render_never_emits_an_empty_bullet() -> None:
    """Any input line must produce a bullet with visible text."""
    for line in cs.render(["feat:", "chore: ", "fix: real"]).splitlines():
        if line.strip().startswith("- "):
            assert line.strip()[2:].strip(), f"empty bullet from {line!r}"


# --- winning (drives the title suggestion) ----------------------------------

@pytest.mark.parametrize(
    ("subjects", "expected"),
    [
        (["feat: a"], "feat"),
        (["fix: a"], "fix"),
        (["chore: a"], "maint"),
        # Highest impact wins regardless of order.
        (["fix: a", "feat: b"], "feat"),
        (["feat: b", "fix: a"], "feat"),
        (["chore: a", "fix: b"], "fix"),
        (["fix: b", "chore: a"], "fix"),
        (["chore: a", "feat!: b", "fix: c"], "breaking"),
        (["feat: a", "feat!: b"], "breaking"),
        # No commits at all -> the most conservative suggestion.
        ([], "maint"),
        (["chore: bump manifest version to v1.0.0"], "maint"),
        # A lone unmappable subject.
        (["revert: undo"], "other"),
    ],
)
def test_winning(subjects: list[str], expected: str) -> None:
    """The suggested title type reflects the most impactful commit present."""
    assert cs.winning(subjects) == expected


def test_every_group_has_a_title_suggestion() -> None:
    """No group can be reached that lacks a suggestion for title-check."""
    for key in cs.ORDER:
        assert key in cs.SUGGESTIONS
