"""Unit tests for scripts/governance_gate.py.

The gate's whole value is that it refuses. Every test asserting a refusal has a matching test
asserting the allow, because a gate stuck shut and a gate stuck open are both failures and only
the pair distinguishes them.

Fixtures rebind REPO and TIERS onto a tmp tree so the suite never depends on — or mutates — the
real governing docs. The gate module is imported rather than the server, so CI, which installs
only pytest and pyyaml, never needs the MCP SDK.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location("governance_gate", _SCRIPTS / "governance_gate.py")
gs = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(gs)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A tiny repo: one governing doc, one governed file, one ungoverned file."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/rules.md").write_text("the rules\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/t.py").write_text("a = 1\nb = 2\nc = 3\nb = 2\n")
    (tmp_path / "README.md").write_text("ungoverned\n")
    monkeypatch.setattr(gs, "REPO", tmp_path)
    monkeypatch.setattr(gs, "TIERS", {"scripts/": ("docs/rules.md",)})
    return tmp_path


def _keys(rel="scripts/t.py"):
    """Docs receipt, then the file receipt it unlocks — the intended two-step."""
    docs_key = gs.current_receipt_key("scripts/")
    gs.get_file(rel, docs_key)
    return docs_key, gs.current_edit_key(rel)


# --------------------------------------------------------------------- tiers


def test_governed_and_ungoverned_paths_resolve(repo) -> None:
    assert gs.resolve_tier("scripts/t.py") == "scripts/"
    assert gs.resolve_tier("README.md") is None


def test_specific_tier_wins_over_general(monkeypatch, repo) -> None:
    """Ordering matters: a file with its own tier must not fall into the broader one."""
    monkeypatch.setattr(
        gs, "TIERS", {"scripts/special.py": ("docs/rules.md",), "scripts/": ("docs/rules.md",)}
    )
    assert gs.resolve_tier("scripts/special.py") == "scripts/special.py"
    assert gs.resolve_tier("scripts/other.py") == "scripts/"


# ------------------------------------------------------------ key derivation


def test_key_is_stable_within_a_window_and_rotates_across(repo) -> None:
    now = 10_000.0
    assert gs.current_receipt_key("scripts/", now) == gs.current_receipt_key("scripts/", now + 1)
    assert gs.current_receipt_key("scripts/", now) != gs.current_receipt_key(
        "scripts/", now + gs.ROTATION_SECONDS
    )


def test_previous_window_is_honoured_as_grace(repo) -> None:
    """A read just before rotation must not strand the write that follows it."""
    now = 10_000.0
    previous = gs.current_receipt_key("scripts/", now - gs.ROTATION_SECONDS)
    assert previous in gs.valid_receipt_keys("scripts/", now)


def test_editing_a_governing_doc_invalidates_outstanding_keys(repo) -> None:
    """The divergence from ha-mcp: change the rules and every outstanding key dies."""
    docs_key, edit_key = _keys()
    (repo / "docs/rules.md").write_text("the rules, amended\n")
    assert docs_key not in gs.valid_receipt_keys("scripts/")
    assert edit_key not in gs.valid_edit_keys("scripts/t.py")


def test_the_two_key_kinds_are_not_interchangeable(repo) -> None:
    docs_key, _ = _keys()
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/t.py", "a = 1", "a = 9", docs_key)


# ------------------------------------------------------- reading before writing


def test_reading_a_governed_file_requires_the_docs_receipt(repo) -> None:
    with pytest.raises(gs.GateError):
        gs.get_file("scripts/t.py", None)
    out = gs.get_file("scripts/t.py", gs.current_receipt_key("scripts/"))
    assert "c = 3" in out, "the whole file must be emitted, not a fragment"
    assert gs.current_edit_key("scripts/t.py") in out


def test_patch_is_refused_without_a_file_receipt_and_allowed_with_one(repo) -> None:
    """Patching cheaply is fine; patching something unread is the failure being prevented."""
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/t.py", "a = 1", "a = 9", None)
    assert (repo / "scripts/t.py").read_text().startswith("a = 1")

    _, edit_key = _keys()
    gs.patch_file("scripts/t.py", "a = 1", "a = 9", edit_key)
    assert (repo / "scripts/t.py").read_text().startswith("a = 9")


def test_a_file_receipt_dies_when_the_file_changes(repo) -> None:
    """Bound to content, so a stale key means the file moved under the reader."""
    _, edit_key = _keys()
    gs.patch_file("scripts/t.py", "a = 1", "a = 9", edit_key)
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/t.py", "c = 3", "c = 9", edit_key)


def test_a_receipt_for_one_file_does_not_unlock_another(repo) -> None:
    (repo / "scripts/other.py").write_text("z = 0\n")
    _, edit_key = _keys("scripts/t.py")
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/other.py", "z = 0", "z = 1", edit_key)


# ------------------------------------------------------------------ patching


def test_an_ambiguous_old_string_is_refused(repo) -> None:
    """Two matches means the gate would be choosing; that is the caller's job."""
    _, edit_key = _keys()
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file("scripts/t.py", "b = 2", "b = 9", edit_key)
    assert "2 times" in str(excinfo.value)
    assert (repo / "scripts/t.py").read_text().count("b = 2") == 2


def test_a_new_file_can_be_created_through_the_gate(repo) -> None:
    """Otherwise a governed directory becomes unextendable once other writers are denied."""
    docs_key = gs.current_receipt_key("scripts/")
    gs.get_file("scripts/new.py", docs_key)
    gs.patch_file("scripts/new.py", "", "fresh = 1\n", gs.current_edit_key("scripts/new.py"))
    assert (repo / "scripts/new.py").read_text() == "fresh = 1\n"


def test_an_empty_old_string_will_not_clobber_an_existing_file(repo) -> None:
    """Creation is the only empty-old_string case; anything else is a whole-file overwrite."""
    _, edit_key = _keys()
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/t.py", "", "clobbered\n", edit_key)
    assert (repo / "scripts/t.py").read_text().startswith("a = 1")


def test_an_absent_old_string_is_refused(repo) -> None:
    _, edit_key = _keys()
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/t.py", "nowhere", "somewhere", edit_key)


def test_the_report_shows_the_actual_diff(repo) -> None:
    """Counts prove volume, not correctness: the changed lines themselves are the evidence."""
    _, edit_key = _keys()
    out = gs.patch_file("scripts/t.py", "a = 1", "a = 9\nextra = 1", edit_key)
    assert "+2 -1" in out
    assert "-a = 1" in out and "+a = 9" in out and "+extra = 1" in out
    assert "b = 2" in out, "surrounding context must be shown, not just the changed lines"


def test_the_report_says_so_when_nothing_changed(repo) -> None:
    """A replacement identical to the original must not read as a successful edit."""
    _, edit_key = _keys()
    out = gs.patch_file("scripts/t.py", "a = 1", "a = 1", edit_key)
    assert "no textual change" in out


# ------------------------------------------------------------------- refusals


def test_refusal_never_contains_a_key(repo) -> None:
    """A refusal that leaks the key hands over exactly what the gate withholds."""
    _, edit_key = _keys()
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file("scripts/t.py", "a = 1", "a = 9", "wrong")
    assert edit_key not in str(excinfo.value)
    assert gs.current_receipt_key("scripts/") not in str(excinfo.value)


def test_paths_outside_the_repo_are_refused(repo) -> None:
    for attempt in ("../escape.txt", "/etc/passwd", "scripts/../../escape.txt"):
        with pytest.raises(gs.GateError):
            gs.safe_relpath(attempt)


def test_a_symlink_out_of_the_repo_is_refused(repo) -> None:
    """resolve() follows the link, so the escape is caught rather than written through."""
    outside = repo.parent / "outside.txt"
    outside.write_text("original\n")
    (repo / "scripts/link.txt").symlink_to(outside)
    with pytest.raises(gs.GateError):
        gs.safe_relpath("scripts/link.txt")
    assert outside.read_text() == "original\n"


def test_ungoverned_files_are_not_writable_through_the_gate(repo) -> None:
    """The gate is not a general-purpose writer; ungoverned edits use the ordinary tools."""
    _, edit_key = _keys()
    with pytest.raises(gs.GateError):
        gs.patch_file("README.md", "ungoverned", "clobbered", edit_key)
    assert (repo / "README.md").read_text() == "ungoverned\n"


def test_unknown_tier_is_refused(repo) -> None:
    with pytest.raises(gs.GateError):
        gs.get_docs("nope/")


# ----------------------------------------------------------------- fail open


def test_unreadable_governing_doc_fails_open(repo) -> None:
    """A broken doc makes the key unobtainable; bricking every edit would be worse."""
    (repo / "docs/rules.md").unlink()
    assert gs.current_receipt_key("scripts/") is None
    assert gs.valid_receipt_keys("scripts/") == set()
    result = gs.patch_file("scripts/t.py", "a = 1", "a = 9", None)
    assert "OPEN" in result
    assert (repo / "scripts/t.py").read_text().startswith("a = 9")


def test_emitted_docs_carry_the_key_and_the_content(repo) -> None:
    out = gs.get_docs("scripts/")
    assert gs.current_receipt_key("scripts/") in out
    assert "the rules" in out


def test_the_old_tool_names_are_gone(repo) -> None:
    """A renamed tool that keeps its old alias is two names for one gate, and docs drift."""
    for old in ("get_governing_docs", "get_governed_file", "governed_edit"):
        assert not hasattr(gs, old), old


# --------------------------------------------------------------- rolling key


def test_a_patch_hands_back_the_key_for_the_file_it_just_wrote(repo) -> None:
    """Read once, patch many times: the reply carries the next key, so no re-read is needed.

    Eleven of thirteen reads of one file in a session were re-reads forced by a key that died
    on every patch. The server holds the bytes it just wrote and the caller saw the diff, so
    handing the next key back keeps the guarantee and drops the cost.
    """
    _, edit_key = _keys()
    out = gs.patch_file("scripts/t.py", "a = 1", "a = 9", edit_key)
    fresh = gs.current_edit_key("scripts/t.py")
    assert fresh in out and fresh != edit_key
    gs.patch_file("scripts/t.py", "c = 3", "c = 9", fresh)
    assert (repo / "scripts/t.py").read_text() == "a = 9\nb = 2\nc = 9\nb = 2\n"
