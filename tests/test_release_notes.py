"""Unit tests for scripts/release_notes.py.

Load the standalone script by path; it is not an importable package.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(_SCRIPTS))
_SPEC = importlib.util.spec_from_file_location("release_notes", _SCRIPTS / "release_notes.py")
rn = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(rn)


def test_groups_by_commit_type_not_pr_label(monkeypatch) -> None:
    """A fix inside a feature PR belongs under Fixes.

    This is the whole reason the notes are generated: release-drafter files every
    commit of a PR under that PR's single label, so a `fix:` in a `feat:`-titled
    PR lands under Features and a reader finds no Fixes section.
    """
    log = "\n".join([
        "aaa\x00feat: add polling",
        "bbb\x00fix: close the session",
        "ccc\x00chore: tidy",
    ])
    monkeypatch.setattr(rn, "_git", lambda *a: log)
    monkeypatch.setattr(rn, "pr_for", lambda sha, head: "7")
    out = rn.build("v1..HEAD", repo_url="https://x/y", head="HEAD")

    assert out.index("## 🚀 Features") < out.index("## 🔧 Fixes") < out.index("## 🧰 Maintenance")
    fixes = out.split("## 🔧 Fixes")[1].split("##")[0]
    assert "close the session" in fixes
    assert "add polling" not in fixes


def test_merge_commits_and_version_bumps_are_dropped(monkeypatch) -> None:
    """Neither is a changelog entry."""
    log = "\n".join([
        "aaa\x00Merge pull request #3 from o/b",
        "bbb\x00chore: bump manifest version to v1.2.3",
        "ccc\x00fix: a real change",
    ])
    monkeypatch.setattr(rn, "_git", lambda *a: log)
    monkeypatch.setattr(rn, "pr_for", lambda sha, head: None)
    out = rn.build("v1..HEAD")
    assert "a real change" in out
    assert "Merge pull request" not in out
    assert "bump manifest version" not in out


def test_compare_link_appended(monkeypatch) -> None:
    """Every surveyed HACS repo ends with a full-changelog compare link."""
    monkeypatch.setattr(rn, "_git", lambda *a: "aaa\x00feat: thing")
    monkeypatch.setattr(rn, "pr_for", lambda sha, head: None)
    out = rn.build("v1..HEAD", repo_url="https://x/y", previous="v1.0.0", version="1.1.0")
    assert "**Full Changelog**: [v1.0.0...v1.1.0](https://x/y/compare/v1.0.0...v1.1.0)" in out


def test_no_changes_says_so(monkeypatch) -> None:
    """An empty range must not render an empty document."""
    monkeypatch.setattr(rn, "_git", lambda *a: "")
    assert rn.build("v1..HEAD").strip() == "_No user-facing changes._"


def test_empty_range_sentinel_is_flagged() -> None:
    """A published body of `_No user-facing changes._` means the range was wrong.

    v7.2.0 shipped a 25-character body over nine commits, because the previous tag
    resolved to the release being written. Everything else about the body was valid,
    so only a check for the sentinel itself catches it.
    """
    import importlib.util as _il
    spec = _il.spec_from_file_location("check_release_notes", _SCRIPTS / "check_release_notes.py")
    crn = _il.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(crn)

    assert any("empty-range sentinel" in p for p in crn.check("_No user-facing changes._"))
    assert not any("empty-range sentinel" in p for p in crn.check("## 🔧 Fixes\n\n- a real change"))


GH_NOTES = "\n".join([
    "## What's Changed",
    "* fix: close the session by @someone in https://x/y/pull/7",
    "",
    "## New Contributors",
    "* @newbie made their first contribution in https://x/y/pull/7",
    "* @dependabot[bot] made their first contribution in https://x/y/pull/8",
    "",
    "**Full Changelog**: https://x/y/compare/v1.0.0...v1.1.0",
])


def test_new_contributors_takes_only_that_section() -> None:
    """GitHub's `What's Changed` and compare line must not come with it."""
    block = rn.new_contributors(GH_NOTES)
    assert block.startswith("## New Contributors")
    assert "@newbie" in block
    assert "What's Changed" not in block
    assert "Full Changelog" not in block


def test_new_contributors_drops_bots() -> None:
    """Thanking dependabot for its first contribution is noise, not credit."""
    assert "dependabot" not in rn.new_contributors(GH_NOTES)
    assert "dependabot" in rn.new_contributors(GH_NOTES, include_bots=True)


def test_new_contributors_empty_when_only_bots() -> None:
    """Filtering can empty the section, and a bare heading is worse than none."""
    notes = "\n".join([
        "## New Contributors",
        "* @dependabot[bot] made their first contribution in https://x/y/pull/8",
    ])
    assert rn.new_contributors(notes) == ""


def test_new_contributors_spliced_before_the_compare_link(monkeypatch) -> None:
    """The block belongs in the body, above the compare link this file writes."""
    monkeypatch.setattr(rn, "_git", lambda *a: "aaa\x00feat: thing")
    monkeypatch.setattr(rn, "pr_for", lambda sha, head: None)
    out = rn.build("v1..HEAD", repo_url="https://x/y", previous="v1.0.0", version="1.1.0",
                   github_notes=GH_NOTES)
    assert out.index("## New Contributors") < out.index("**Full Changelog**")
    assert out.count("**Full Changelog**") == 1
