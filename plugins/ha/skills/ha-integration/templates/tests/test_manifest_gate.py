"""Unit tests for the manifest version gate decision logic."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "manifest_gate", Path(__file__).parents[1] / "scripts" / "manifest_gate.py"
)
assert _SPEC and _SPEC.loader
manifest_gate = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(manifest_gate)
evaluate = manifest_gate.evaluate


def ok(*args, **kwargs) -> bool:
    return evaluate(*args, **kwargs)[0]


def test_unchanged_vs_last_release_fails() -> None:
    assert not ok("1.1.0", "1.1.0", "1.1.0", ["fix"])

def test_feature_minor_bump_passes() -> None:
    assert ok("1.1.0", "1.1.0", "1.2.0", ["feature"])

def test_feature_only_patch_under_bumps() -> None:
    assert not ok("1.1.0", "1.1.0", "1.1.1", ["feature"])

def test_chore_rides_in_cycle_minor() -> None:  # the shipped regression
    assert ok("1.1.0", "1.2.0", "1.2.0", ["chore"])

def test_chore_overbump_beyond_cycle_fails() -> None:
    assert not ok("1.1.0", "1.2.0", "2.0.0", ["chore"])

def test_breaking_major_passes() -> None:
    assert ok("1.1.0", "1.2.0", "2.0.0", ["xfeat"])

def test_prerelease_only_needs_to_differ() -> None:
    assert ok("1.1.0", "1.1.0", "2.0.0rc1", ["feature"])
    assert not ok("2.0.0rc1", "2.0.0rc1", "2.0.0rc1", ["feature"])

def test_final_graduates_prerelease() -> None:  # 2.0.0rc19 -> 2.0.0, even feature-labelled
    assert ok("2.0.0rc19", "2.0.0rc20", "2.0.0", ["feature"])
    assert not ok("2.0.0", "2.0.0", "2.0.0", ["feature"])  # already final -> still must bump

def test_dependabot_exempt() -> None:
    assert ok("1.1.0", "1.1.0", "1.1.0", [], dependabot=True)

def test_no_managed_label_passes_when_changed() -> None:
    assert ok("1.1.0", "1.1.0", "1.1.5", [])


# --- title/commit breaking agreement -----------------------------------------
# v7.0.0 was labelled major from a `feat!:` PR title while no commit carried `!`,
# so the generated notes had no Breaking Changes section. The reverse ships a
# breaking change as a minor. Neither was caught, because the version came from
# the title and the notes came from the commits.

def test_breaking_title_without_breaking_commit_fails() -> None:
    ok, reason = evaluate("6.5.0", "6.5.0", "7.0.0", ["xfeat"], breaking_commits=0)
    assert not ok
    assert "no commit" in reason


def test_breaking_commit_without_breaking_title_fails() -> None:
    ok, reason = evaluate("6.5.0", "6.5.0", "6.6.0", ["feature"], breaking_commits=1)
    assert not ok
    assert "without a" in reason


def test_breaking_title_with_breaking_commit_passes() -> None:
    ok, _ = evaluate("6.5.0", "6.5.0", "7.0.0", ["xfeat"], breaking_commits=1)
    assert ok


def test_non_breaking_agreement_passes() -> None:
    ok, _ = evaluate("6.5.0", "6.5.0", "6.6.0", ["feature"], breaking_commits=0)
    assert ok


def test_omitting_the_count_skips_the_check() -> None:
    """Existing callers that pass no count keep their old behaviour."""
    ok, _ = evaluate("6.5.0", "6.5.0", "7.0.0", ["xfeat"])
    assert ok


def test_dependabot_still_exempt_with_a_count() -> None:
    ok, _ = evaluate("6.5.0", "6.5.0", "6.5.1", [], dependabot=True, breaking_commits=1)
    assert ok

def test_suggest_prints_the_version_the_labels_imply(capsys) -> None:
    """The advisory check in a tag-driven repo needs a number, not a verdict.

    No PR carries a bump there, so there is nothing to validate — the useful output
    is what the next release will be if this PR merges.
    """
    assert manifest_gate.main(["--suggest", "--last-release", "0.1.0", "--labels", "feature"]) == 0
    assert capsys.readouterr().out.strip() == "v0.2.0"

    assert manifest_gate.main(["--suggest", "--last-release", "0.1.0", "--labels", "fix"]) == 0
    assert capsys.readouterr().out.strip() == "v0.1.1"

    # No increment-bearing label implies no release, which is not the same as a patch.
    assert manifest_gate.main(["--suggest", "--last-release", "0.1.0", "--labels", ""]) == 0
    assert capsys.readouterr().out.strip() == "v0.1.0"
