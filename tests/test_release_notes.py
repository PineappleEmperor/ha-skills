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
