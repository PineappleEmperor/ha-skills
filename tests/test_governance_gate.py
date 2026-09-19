"""Unit tests for scripts/governance_gate.py.

The gate's whole value is that it refuses. Every test asserting a refusal has a matching test
asserting the allow, because a gate stuck shut and a gate stuck open are both failures and only
the pair distinguishes them.

Fixtures rebind REPO and TIERS onto a tmp tree so the suite never depends on — or mutates — the
real governing docs. The gate module is imported rather than the server, so CI, which installs
only pytest and pyyaml, never needs the MCP SDK.
"""

import importlib.util
import pathlib

import pytest

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location(
    "governance_gate", _SCRIPTS / "governance_gate.py"
)
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
    """A path under a tier prefix resolves to it; anything else is ungoverned."""
    assert gs.resolve_tier("scripts/t.py") == "scripts/"
    assert gs.resolve_tier("README.md") is None


def test_the_root_and_the_tier_map_come_from_the_environment(
    monkeypatch, tmp_path
) -> None:
    """One gate serves any repository, so a CI repository gets one of its own.

    Every path this module touches hangs off `REPO`, which it took from its own location —
    so the gate could only ever guard the repository it was checked out into. The CI
    repositories hold the workflows and scripts every consumer runs and were guarded by
    nothing, and every edit made to them off a search rather than a read was made there.

    Both variables are read at import, so this executes the module afresh rather than
    asserting about the copy the rest of the suite holds. Asserting only that `profile()`
    maps two names left the whole of that change unproven: put the hardcoded root and map
    back and every other test still passed.
    """
    assert gs.profile("skill") is gs.SKILL_TIERS
    assert gs.profile("ci") is gs.CI_TIERS
    with pytest.raises(gs.GateError):
        gs.profile("nonesuch")
    assert gs.TIERS == gs.SKILL_TIERS
    assert pathlib.Path(__file__).resolve().parents[1] == gs.REPO

    monkeypatch.setenv("GOVERNANCE_ROOT", str(tmp_path))
    monkeypatch.setenv("GOVERNANCE_PROFILE", "ci")
    elsewhere = importlib.util.module_from_spec(_SPEC)
    _SPEC.loader.exec_module(elsewhere)
    assert tmp_path.resolve() == elsewhere.REPO
    assert elsewhere.TIERS == elsewhere.CI_TIERS

    # A mistyped profile is a configuration error with no tool call to report it through,
    # so it stops the server with the one line that says what to fix.
    monkeypatch.setenv("GOVERNANCE_PROFILE", "nonesuch")
    with pytest.raises(SystemExit) as exc:
        _SPEC.loader.exec_module(importlib.util.module_from_spec(_SPEC))
    assert "unknown profile" in str(exc.value)

    # A CI repository's README is the source for its workflows, so it governs them — and
    # itself, so that rewriting it kills every outstanding key the way a reference doc does.
    for tier in (".github/workflows/", "scripts/", "tests/", "README.md"):
        assert gs.CI_TIERS[tier] == ("README.md",)


def test_a_ci_repository_root_governs_its_own_files(tmp_path, monkeypatch) -> None:
    """Rooted at a CI repository, the same gate refuses the same way it does here."""
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/pr-checks.yml").write_text("on:\n  workflow_call:\n")
    (tmp_path / "README.md").write_text("# release-flow\n\nthe contract\n")
    monkeypatch.setattr(gs, "REPO", tmp_path)
    monkeypatch.setattr(gs, "TIERS", gs.CI_TIERS)

    assert gs.resolve_tier(".github/workflows/pr-checks.yml") == ".github/workflows/"
    assert gs.resolve_tier("README.md") == "README.md"

    with pytest.raises(gs.GateError):
        gs.patch_file(
            ".github/workflows/pr-checks.yml", "workflow_call:", "push:", None
        )

    docs_key = gs.current_receipt_key(".github/workflows/")
    gs.get_file(".github/workflows/pr-checks.yml", docs_key)
    gs.patch_file(
        ".github/workflows/pr-checks.yml",
        "workflow_call:",
        "workflow_call: {}",
        gs.current_edit_key(".github/workflows/pr-checks.yml"),
    )
    assert (
        "workflow_call: {}"
        in (tmp_path / ".github/workflows/pr-checks.yml").read_text()
    )

    # Rewriting the README kills every key it governs, since it is what they were read against.
    stale = gs.current_receipt_key("scripts/")
    (tmp_path / "README.md").write_text("# release-flow\n\nrewritten\n")
    assert stale not in gs.valid_receipt_keys("scripts/")


def _backlog(repo, monkeypatch):
    """A repo whose backlog is governed, and whose claims are therefore checked."""
    (repo / "docs/backlog.md").write_text("# Backlog\n\n| # | Finding |\n|---|---|\n")
    monkeypatch.setattr(
        gs,
        "TIERS",
        {"scripts/": ("docs/rules.md",), "docs/backlog.md": ("docs/rules.md",)},
    )
    monkeypatch.setattr(gs, "_SERVED", {})
    docs_key = gs.current_receipt_key("docs/backlog.md")
    gs.get_file("docs/backlog.md", docs_key)
    return gs.current_edit_key("docs/backlog.md")


def test_a_backlog_row_naming_an_unread_governed_file_is_refused(repo, monkeypatch):
    """Row 89: the edit key proves the backlog was read, never the file it makes a claim about.

    Row 85 was written under a valid key for the backlog and asserted, wrongly, that two
    reference files contradicted each other. Nothing asked whether either had been opened.
    """
    key = _backlog(repo, monkeypatch)
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file(
            "docs/backlog.md",
            "|---|---|\n",
            "|---|---|\n| 1 | `scripts/t.py` drops the guard |\n",
            key,
        )
    assert "scripts/t.py" in str(excinfo.value)

    # Reading it is the whole requirement; the same patch then lands.
    gs.get_file("scripts/t.py", gs.current_receipt_key("scripts/"))
    gs.patch_file(
        "docs/backlog.md",
        "|---|---|\n",
        "|---|---|\n| 1 | `scripts/t.py` drops the guard |\n",
        gs.current_edit_key("docs/backlog.md"),
    )
    assert "drops the guard" in (repo / "docs/backlog.md").read_text()


def test_a_claim_about_something_ungoverned_or_absent_is_not_checked(repo, monkeypatch):
    """Only a file this gate could have served is demanded.

    Rows name another repository's `scripts/` by bare path, and name files deleted years
    ago on purpose. Neither can be read here, so demanding it would make the register
    unwritable rather than more honest.
    """
    key = _backlog(repo, monkeypatch)
    gs.patch_file(
        "docs/backlog.md",
        "|---|---|\n",
        "|---|---|\n| 1 | `README.md` and `scripts/gone.py` both say so |\n",
        key,
    )
    assert "both say so" in (repo / "docs/backlog.md").read_text()


def test_only_the_backlog_has_its_claims_checked(repo, monkeypatch):
    """A script may name any path in a comment; it is the register that asserts."""
    _backlog(repo, monkeypatch)
    (repo / "scripts/other.py").write_text("x = 1\n")
    gs.get_file("scripts/other.py", gs.current_receipt_key("scripts/"))
    gs.patch_file(
        "scripts/other.py",
        "x = 1",
        "x = 1  # see `scripts/t.py`",
        gs.current_edit_key("scripts/other.py"),
    )
    assert "see `scripts/t.py`" in (repo / "scripts/other.py").read_text()


def test_the_register_and_its_phase_files_are_both_governed() -> None:
    """The register is splitting by phase, so both spellings must be in the real map.

    No tool in the session can serve the register whole any more: the gate refused it
    twice and the file reader caps below its size. A file nothing can read in full is a
    file nothing can honestly claim about, which is how a receipt got harvested from a
    refusal instead of earned.
    """
    assert gs.resolve_tier("docs/backlog.md") is not None
    assert gs.resolve_tier("docs/backlog/2026-09-04-testbed-run.md") is not None


def test_a_phase_file_is_claim_checked_like_the_register(repo, monkeypatch):
    """A row that moves into a phase file keeps the check that row 89 put on it.

    The claim check named one filename. Splitting the register would have taken every row
    that moved out of its reach the moment the new file was created — a guard removed by a
    reorganisation rather than by a decision, which is the worst way to lose one.
    """
    (repo / "docs/backlog").mkdir()
    phase = "docs/backlog/2026-09-04-a-pass.md"
    (repo / phase).write_text("# A pass\n\n| # | Finding |\n|---|---|\n")
    monkeypatch.setattr(
        gs,
        "TIERS",
        {
            "scripts/": ("docs/rules.md",),
            "docs/backlog.md": ("docs/rules.md",),
            "docs/backlog/": ("docs/rules.md",),
        },
    )
    monkeypatch.setattr(gs, "_SERVED", {})
    gs.get_file(phase, gs.current_receipt_key("docs/backlog/"))
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file(
            phase,
            "|---|---|\n",
            "|---|---|\n| 1 | `scripts/t.py` drops the guard |\n",
            gs.current_edit_key(phase),
        )
    assert "scripts/t.py" in str(excinfo.value)


def test_specific_tier_wins_over_general(monkeypatch, repo) -> None:
    """Ordering matters: a file with its own tier must not fall into the broader one."""
    monkeypatch.setattr(
        gs,
        "TIERS",
        {"scripts/special.py": ("docs/rules.md",), "scripts/": ("docs/rules.md",)},
    )
    assert gs.resolve_tier("scripts/special.py") == "scripts/special.py"
    assert gs.resolve_tier("scripts/other.py") == "scripts/"


# ------------------------------------------------- the release window's sources


def _sourced(repo, monkeypatch):
    """A reference tier plus two fetched windows, shaped as `fetch_ha_sources.py` leaves it."""
    (repo / "reference").mkdir()
    (repo / "reference/patterns.md").write_text("# Patterns\n\nold text\n")
    (repo / "docs/ha-release/2026.9").mkdir(parents=True)
    (repo / "docs/ha-release/2026.9/release-notes.md").write_text("the notes\n")
    (repo / "docs/ha-release/2026.9/blog-a.md").write_text("the post\n")
    (repo / "docs/ha-release/2026.8").mkdir(parents=True)
    (repo / "docs/ha-release/2026.8/release-notes.md").write_text("older notes\n")
    (repo / "docs/ha-release/index.md").write_text(
        "| Source | What it is |\n|---|---|\n"
        "| `docs/ha-release/2026.9/release-notes.md` | [notes](u) |\n"
        "| `docs/ha-release/2026.9/blog-a.md` | [post](u) |\n"
        "| `docs/ha-release/2026.8/release-notes.md` | [older](u) |\n"
    )
    monkeypatch.setattr(gs, "REFERENCE_TIER", "reference/")
    monkeypatch.setattr(
        gs,
        "TIERS",
        {
            "reference/": ("docs/rules.md",),
            "docs/ha-release/": ("docs/rules.md",),
            "scripts/": ("docs/rules.md",),
        },
    )
    monkeypatch.setattr(gs, "_SERVED", {})
    gs.get_file("reference/patterns.md", gs.current_receipt_key("reference/"))
    return gs.current_edit_key("reference/patterns.md")


def test_a_release_claim_is_refused_while_the_windows_sources_are_unread(
    repo, monkeypatch
):
    """Row 220: the edit key proves the doc was read, never the sources it is written from.

    The 2026.9 pass wrote rows off a memory of the posts and got eight facts wrong, under a
    key that was valid the whole time. This is the check that makes *Open every source*
    something other than advice.
    """
    key = _sourced(repo, monkeypatch)
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file("reference/patterns.md", "old text", "2026.9 removed it", key)
    assert "docs/ha-release/2026.9/release-notes.md" in str(excinfo.value)
    assert "docs/ha-release/2026.9/blog-a.md" in str(excinfo.value)
    assert (repo / "reference/patterns.md").read_text().endswith("old text\n")


def test_reading_every_source_is_what_lifts_the_refusal(repo, monkeypatch):
    """Every one of them: reading all but one leaves the last one demanded by name."""
    key = _sourced(repo, monkeypatch)
    docs_key = gs.current_receipt_key("docs/ha-release/")
    gs.get_file("docs/ha-release/2026.9/release-notes.md", docs_key)
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file("reference/patterns.md", "old text", "2026.9 removed it", key)
    assert "blog-a.md" in str(excinfo.value)
    assert "release-notes.md" not in str(excinfo.value)

    gs.get_file("docs/ha-release/2026.9/blog-a.md", docs_key)
    gs.patch_file("reference/patterns.md", "old text", "2026.9 removed it", key)
    assert "2026.9 removed it" in (repo / "reference/patterns.md").read_text()


def test_each_release_demands_its_own_sources_and_no_others(repo, monkeypatch):
    """Per release, or an edit about one release pays for the reading of every window.

    A demand for the whole directory also made a window that moved on un-gate every row
    written about the window before it, which is the opposite of what this exists to do.
    """
    key = _sourced(repo, monkeypatch)
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file("reference/patterns.md", "old text", "2026.8 changed it", key)
    assert "docs/ha-release/2026.8/release-notes.md" in str(excinfo.value)
    assert "2026.9" not in str(excinfo.value)

    gs.get_file(
        "docs/ha-release/2026.8/release-notes.md",
        gs.current_receipt_key("docs/ha-release/"),
    )
    gs.patch_file("reference/patterns.md", "old text", "2026.8 changed it", key)
    assert "2026.8 changed it" in (repo / "reference/patterns.md").read_text()


def test_a_claim_about_a_release_with_no_fetched_sources_is_not_gated(
    repo, monkeypatch
):
    """Nothing here could settle it, and a refusal that cannot help gets read as noise.

    `freshness.md` records that inline brand assets have been served since 2026.3, and
    `patterns.md` names 2027.8 as a removal release — one predates the fetch and the other
    cannot be fetched at all. Both must stay writable.
    """
    key = _sourced(repo, monkeypatch)
    gs.patch_file(
        "reference/patterns.md", "old text", "served since 2026.3, gone in 2027.8", key
    )
    assert "2027.8" in (repo / "reference/patterns.md").read_text()


def test_a_patch_naming_no_release_at_all_is_not_gated(repo, monkeypatch):
    """Most reference edits say nothing about a release and must stay cheap."""
    key = _sourced(repo, monkeypatch)
    gs.patch_file("reference/patterns.md", "old text", "a typo fixed", key)
    assert "a typo fixed" in (repo / "reference/patterns.md").read_text()


def test_a_version_that_is_not_a_release_is_not_read_as_one(repo, monkeypatch):
    """A harness pin and a Python floor are versions; neither is a Home Assistant release.

    Asserted against the pattern itself, not only through the gate. Reached only through
    `patch_file` this passed for the wrong reason — a two-digit year yields no folder to
    demand either — and a pattern widened to two loose numbers left the whole suite green.
    """
    assert not gs._RELEASE.findall("pinned at 0.13.365 on 3.14")
    assert gs._RELEASE.findall("2026.9 and v2026.10.2") == [
        ("2026", "9"),
        ("2026", "10"),
    ]
    key = _sourced(repo, monkeypatch)
    gs.patch_file(
        "reference/patterns.md", "old text", "pinned at 0.13.365 on 3.14", key
    )
    assert "0.13.365" in (repo / "reference/patterns.md").read_text()


def test_a_release_written_as_a_tag_is_still_a_release(repo, monkeypatch):
    """`v2026.9` is how a claim about the tag is spelled, and a claim about a tag is a claim."""
    key = _sourced(repo, monkeypatch)
    with pytest.raises(gs.GateError):
        gs.patch_file("reference/patterns.md", "old text", "read at v2026.9", key)


def test_editing_a_row_that_already_names_a_release_demands_its_sources(
    repo, monkeypatch
):
    """Both sides of the patch are checked, or the row is rewritten around the number.

    Checking `new_string` alone left the commonest edit of all ungated: taking an existing
    release row and restating it, from the same memory that got it wrong the first time.
    """
    _sourced(repo, monkeypatch)
    (repo / "reference/patterns.md").write_text("# Patterns\n\n2026.9 removed it\n")
    gs.get_file("reference/patterns.md", gs.current_receipt_key("reference/"))
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file(
            "reference/patterns.md",
            "2026.9 removed it",
            "it was removed",
            gs.current_edit_key("reference/patterns.md"),
        )
    assert "docs/ha-release/2026.9/blog-a.md" in str(excinfo.value)


def test_only_the_reference_tier_has_its_release_claims_checked(repo, monkeypatch):
    """A script may name a release in a comment; it is the guidance that makes the claim."""
    _sourced(repo, monkeypatch)
    gs.get_file("scripts/t.py", gs.current_receipt_key("scripts/"))
    gs.patch_file(
        "scripts/t.py",
        "a = 1",
        "a = 1  # since 2026.9",
        gs.current_edit_key("scripts/t.py"),
    )
    assert "since 2026.9" in (repo / "scripts/t.py").read_text()


def test_emptying_the_index_does_not_disarm_the_check(repo, monkeypatch):
    """The demand comes from the directory, because the index is patchable through the gate.

    Derived from the index, the check was defeated by one `patch_file` that deleted rows
    while every file stayed on disk and all 131 tests passed. Removing a source now means
    removing a file, which a diff shows.
    """
    key = _sourced(repo, monkeypatch)
    (repo / "docs/ha-release/index.md").write_text(
        "| Source | What it is |\n|---|---|\n"
    )
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file("reference/patterns.md", "old text", "2026.9 removed it", key)
    assert "docs/ha-release/2026.9/blog-a.md" in str(excinfo.value)

    (repo / "docs/ha-release/index.md").unlink()
    with pytest.raises(gs.GateError):
        gs.patch_file("reference/patterns.md", "old text", "2026.9 removed it", key)


def test_with_nothing_fetched_the_source_check_is_open(repo, monkeypatch):
    """Fail open, like an unreadable governing doc: a clone that never fetched still works.

    That is also the way out of this check, which is why `tests/test_fetch_ha_sources.py`
    fails when the release `freshness.md` names has no folder — the gate cannot notice its
    own absence.
    """
    key = _sourced(repo, monkeypatch)
    for folder in ("2026.8", "2026.9"):
        for path in (repo / "docs/ha-release" / folder).iterdir():
            path.unlink()
        (repo / "docs/ha-release" / folder).rmdir()
    assert gs.fetched_sources() == {}
    gs.patch_file("reference/patterns.md", "old text", "2026.9 removed it", key)
    assert "2026.9 removed it" in (repo / "reference/patterns.md").read_text()


def test_writing_about_the_next_minor_before_fetching_it_is_refused(repo, monkeypatch):
    """The ordinary case of the whole procedure, and per-release demand had opened it.

    Measured against both versions of the gate: "landing in 2026.10" was refused by the
    release >= oldest rule and allowed by the per-release one. A missing folder for the very
    next minor means the fetch was skipped, which is the one absence that is not innocent.
    """
    key = _sourced(repo, monkeypatch)
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file("reference/patterns.md", "old text", "landing in 2026.10", key)
    assert "fetch_ha_sources.py --release 2026.10" in str(excinfo.value)
    assert "old text" in (repo / "reference/patterns.md").read_text()


def test_a_release_further_ahead_than_the_next_minor_is_still_writable(
    repo, monkeypatch
):
    """`2027.8` is a removal release a year out; no fetch could settle it, ever."""
    key = _sourced(repo, monkeypatch)
    gs.patch_file("reference/patterns.md", "old text", "removed in 2027.8", key)
    assert "2027.8" in (repo / "reference/patterns.md").read_text()


def test_december_rolls_over_when_the_next_minor_is_worked_out(repo, monkeypatch):
    """Home Assistant numbers by calendar month, so the one after 2026.12 is 2027.1."""
    assert gs._next_minor((2026, 12)) == (2027, 1)
    assert gs._next_minor((2026, 9)) == (2026, 10)


def test_a_fetched_source_is_read_through_the_gate_and_never_patched(repo, monkeypatch):
    """The demand list survived a patch; the substance did not.

    Through the live API, `old_string` set to a whole source and `new_string` empty left
    every file present, listed, zero bytes and trivially served, with the suite green. These
    files are generated, so the honest rule is that the gate never writes them.
    """
    _sourced(repo, monkeypatch)
    docs_key = gs.current_receipt_key("docs/ha-release/")
    gs.get_file("docs/ha-release/2026.9/blog-a.md", docs_key)
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file(
            "docs/ha-release/2026.9/blog-a.md",
            "the post\n",
            "",
            gs.current_edit_key("docs/ha-release/2026.9/blog-a.md"),
        )
    assert "generated by scripts/fetch_ha_sources.py" in str(excinfo.value)
    assert (repo / "docs/ha-release/2026.9/blog-a.md").read_text() == "the post\n"


def test_the_real_map_governs_the_fetched_sources_and_names_the_real_tier() -> None:
    """Rebinding both in the fixture would hide a map that governs neither."""
    assert gs.resolve_tier("docs/ha-release/index.md") == "docs/ha-release/"
    assert gs.TIERS["docs/ha-release/"] == (
        "plugins/ha/skills/ha-integration/reference/freshness.md",
    )
    assert gs.REFERENCE_TIER in gs.TIERS
    assert gs.SOURCE_INDEX.startswith(gs.SOURCE_DIR)


def test_the_real_repository_has_the_release_row_covered() -> None:
    """The row the skill claims to be current for must be one the gate can demand for.

    `tests/test_fetch_ha_sources.py` says the same thing from the index's side; this says it
    from the gate's, since it is `fetched_sources()` that decides what is enforced.
    """
    assert (2026, 9) in gs.fetched_sources()


# ------------------------------------------------------------ key derivation


def test_key_is_stable_within_a_window_and_rotates_across(repo) -> None:
    """The clock enters the key by bucket, so it holds for the window and then turns."""
    now = 10_000.0
    assert gs.current_receipt_key("scripts/", now) == gs.current_receipt_key(
        "scripts/", now + 1
    )
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
    """A docs receipt proves the rules were read, not the file; it unlocks no patch."""
    docs_key, _ = _keys()
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/t.py", "a = 1", "a = 9", docs_key)


# ------------------------------------------------------- reading before writing


def test_reading_a_governed_file_requires_the_docs_receipt(repo) -> None:
    """The rules are read before the file, never instead of it."""
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
    """The path is part of the key, so reading one file buys no write to its neighbour."""
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
    gs.patch_file(
        "scripts/new.py", "", "fresh = 1\n", gs.current_edit_key("scripts/new.py")
    )
    assert (repo / "scripts/new.py").read_text() == "fresh = 1\n"


def test_an_empty_old_string_will_not_clobber_an_existing_file(repo) -> None:
    """Creation is the only empty-old_string case; anything else is a whole-file overwrite."""
    _, edit_key = _keys()
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/t.py", "", "clobbered\n", edit_key)
    assert (repo / "scripts/t.py").read_text().startswith("a = 1")


def test_an_absent_old_string_is_refused(repo) -> None:
    """No match means the caller's picture of the file is wrong; nothing is written."""
    _, edit_key = _keys()
    with pytest.raises(gs.GateError):
        gs.patch_file("scripts/t.py", "nowhere", "somewhere", edit_key)


def test_the_report_shows_the_actual_diff(repo) -> None:
    """Counts prove volume, not correctness: the changed lines themselves are the evidence."""
    _, edit_key = _keys()
    out = gs.patch_file("scripts/t.py", "a = 1", "a = 9\nextra = 1", edit_key)
    assert "+2 -1" in out
    assert "-a = 1" in out and "+a = 9" in out and "+extra = 1" in out
    assert "b = 2" in out, (
        "surrounding context must be shown, not just the changed lines"
    )


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
    """Every spelling of an escape resolves outside the repo and is refused."""
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
    """A tier nothing governs has no docs to receipt; asking for one is refused."""
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


def test_every_governing_doc_in_the_real_tier_map_exists() -> None:
    """A tier naming a doc that is gone is silently OPEN; the TIERS comment says why."""
    for tier, docs in gs.TIERS.items():
        for rel in docs:
            path = gs.REPO / rel
            assert path.is_file() and path.read_bytes(), (
                f"{tier} is governed by a missing or empty {rel}"
            )


def test_emitted_docs_carry_the_key_and_the_content(repo) -> None:
    """One reply holds both the receipt and the rules it receipts."""
    out = gs.get_docs("scripts/")
    assert gs.current_receipt_key("scripts/") in out
    assert "the rules" in out


def test_the_old_tool_names_are_gone(repo) -> None:
    """A renamed tool that keeps its old alias is two names for one gate, and docs drift."""
    for old in (
        "get_governing_docs",
        "get_governed_file",
        "governed_edit",
        "patch_twins",
        "twin_of",
        "TWIN_ROOT",
    ):
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


# ------------------------------------------------------------ one function


_MODULE = '''\
"""A file shaped like the audit: independent checks, shared helpers, one registry."""
import re

LIMIT = 3


def _helper(x):
    return x * LIMIT


def check_one(repo):
    """First check."""
    return _helper(repo)


def check_two(repo):
    """Second check."""
    return re.sub("a", "b", repo)


CHECKS = (check_one, check_two)
'''


@pytest.fixture
def module(repo):
    """The audit-shaped module written into the governed tree, as its relative path."""
    (repo / "scripts/mod.py").write_text(_MODULE)
    return "scripts/mod.py"


def test_a_function_read_returns_it_with_everything_it_uses(module) -> None:
    """The server decides what the slice is, from the code, so it is never incomplete.

    Reading one check out of a thousand-line file is the cheap read the whole-file rule was
    written to forbid, because a hand-picked slice omits the context that made the line wrong.
    A slice the parser picks is different: the function, every module-level name it reaches,
    the imports, and the registry that lists it. Nothing the edit can touch is out of view.
    """
    docs_key = gs.current_receipt_key("scripts/")
    out = gs.get_function(module, "check_one", docs_key)
    for needed in (
        "def check_one",
        "def _helper",
        "LIMIT = 3",
        "import re",
        "CHECKS = (",
    ):
        assert needed in out, needed
    assert "def check_two" not in out, (
        "an unrelated function is not part of the closure"
    )
    assert gs.current_function_key(module, "check_one") in out


def test_a_function_key_unlocks_a_patch_inside_it_and_refuses_one_outside(
    module,
) -> None:
    """The key covers exactly the text returned; the rest of the file stays locked."""
    docs_key = gs.current_receipt_key("scripts/")
    gs.get_function(module, "check_one", docs_key)
    key = gs.current_function_key(module, "check_one")
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file(module, 're.sub("a", "b", repo)', "repo", key)
    assert "outside" in str(excinfo.value)
    gs.patch_file(module, "return _helper(repo)", "return _helper(repo) + 1", key)
    assert "return _helper(repo) + 1" in (gs.REPO / module).read_text()


def test_a_function_key_dies_with_its_closure_and_survives_unrelated_edits(
    module,
) -> None:
    """Bound to the closure, not the file: an edit elsewhere must not force a re-read."""
    key = gs.current_function_key(module, "check_one")
    text = (gs.REPO / module).read_text()
    (gs.REPO / module).write_text(text.replace('"b", repo', '"c", repo'))
    assert gs.current_function_key(module, "check_one") == key
    (gs.REPO / module).write_text(text.replace("x * LIMIT", "x + LIMIT"))
    assert gs.current_function_key(module, "check_one") != key


def test_a_patch_with_a_function_key_hands_back_a_function_key(module) -> None:
    """The rolling key keeps the kind it was given: a function read stays function-scoped."""
    docs_key = gs.current_receipt_key("scripts/")
    gs.get_function(module, "check_one", docs_key)
    out = gs.patch_file(
        module,
        "return _helper(repo)",
        "return _helper(repo) + 1",
        gs.current_function_key(module, "check_one"),
    )
    fresh = gs.current_function_key(module, "check_one")
    assert fresh in out
    gs.patch_file(module, "return _helper(repo) + 1", "return _helper(repo) + 2", fresh)


def test_a_fixture_named_as_a_parameter_is_part_of_the_closure(repo) -> None:
    """A test reaches its fixtures by parameter name, never by a call, so names count too."""
    (repo / "scripts/test_x.py").write_text(
        "import pytest\n\n\n"
        "@pytest.fixture\ndef thing():\n    return 1\n\n\n"
        "def test_it(thing):\n    assert thing == 1\n"
    )
    out = gs.get_function(
        "scripts/test_x.py", "test_it", gs.current_receipt_key("scripts/")
    )
    assert "def thing" in out


def test_an_unknown_function_and_an_unparseable_file_are_refused(module) -> None:
    """No closure can be taken from a missing name or a file that does not parse."""
    docs_key = gs.current_receipt_key("scripts/")
    with pytest.raises(gs.GateError):
        gs.get_function(module, "check_nine", docs_key)
    (gs.REPO / module).write_text("def (\n")
    with pytest.raises(gs.GateError) as excinfo:
        gs.get_function(module, "check_one", docs_key)
    assert "get_file" in str(excinfo.value)


# ------------------------------------------------------------------- gate id


def test_every_key_carries_the_gate_id(module) -> None:
    """A restart mints a new salt and a new id together, so the id says which gate spoke.

    Keys minutes old, docs and file unchanged, well inside the grace window, were all refused
    after the harness restarted the server, and the refusal read exactly like a stale read.
    The id in the key is what lets the two be told apart.
    """
    docs_key = gs.current_receipt_key("scripts/")
    _, edit_key = _keys()
    fn_key = gs.current_function_key(module, "check_one")
    for key in (docs_key, edit_key, fn_key):
        assert f"-{gs.GATE_ID}-" in key, key


def test_a_key_from_another_gate_is_refused_and_the_restart_is_named(
    monkeypatch, module
) -> None:
    """All four key checks name the restart when the key's id is not this gate's."""
    docs_key, edit_key = _keys()
    fn_key = gs.current_function_key(module, "check_one")
    born_as = gs.GATE_ID
    monkeypatch.setattr(gs, "GATE_ID", "dead")
    for call in (
        lambda: gs.patch_file("scripts/t.py", "a = 1", "a = 9", edit_key),
        lambda: gs.patch_file(module, "return _helper(repo)", "return 0", fn_key),
        lambda: gs.get_file("scripts/t.py", docs_key),
        lambda: gs.get_function(module, "check_one", docs_key),
    ):
        with pytest.raises(gs.GateError) as excinfo:
            call()
        assert f"minted by gate {born_as}" in str(excinfo.value)
        assert "restarted since" in str(excinfo.value)
    assert (gs.REPO / "scripts/t.py").read_text().startswith("a = 1")
    assert "return _helper(repo)" in (gs.REPO / module).read_text()


def test_a_stale_key_from_this_gate_is_not_blamed_on_a_restart(repo) -> None:
    """The other cause must not be misnamed either: same id means the content moved."""
    _, edit_key = _keys()
    (repo / "scripts/t.py").write_text("moved\n")
    with pytest.raises(gs.GateError) as excinfo:
        gs.patch_file("scripts/t.py", "moved", "back", edit_key)
    assert "has not restarted" in str(excinfo.value)
    assert "restarted since" not in str(excinfo.value)
    assert gs.GATE_ID in str(excinfo.value)


def test_a_missing_key_still_names_the_gate(repo) -> None:
    """Even with nothing to diagnose, the refusal says which gate is speaking."""
    with pytest.raises(gs.GateError) as excinfo:
        gs.get_file("scripts/t.py", None)
    assert gs.GATE_ID in str(excinfo.value)


def test_locate_returns_paths_and_never_a_line(repo) -> None:
    """A locate names the files a pattern occurs in and nothing of their content.

    A search that returns lines gets quoted as evidence; one that returns only paths
    cannot be, so the file has to be read. That is the whole difference between this and
    the shell grep the hook refuses.
    """
    (repo / "docs/other.md").write_text("no match here\n")
    out = gs.locate(r"b = 2")
    assert out == ["scripts/t.py"]
    assert "b = 2" not in "\n".join(out)


def test_locate_skips_scratch_and_git(repo) -> None:
    """`.tmp/`, `.git/` and caches are never candidates."""
    for d in (".tmp", ".git", "__pycache__"):
        (repo / d).mkdir()
        (repo / d / "x.py").write_text("b = 2\n")
    assert gs.locate(r"b = 2") == ["scripts/t.py"]


def test_locate_can_be_narrowed_to_a_prefix(repo) -> None:
    """`under` limits the walk to one subtree, so a broad pattern stays cheap."""
    (repo / "docs/rules.md").write_text("the rules\nb = 2\n")
    assert gs.locate(r"b = 2", under="docs/") == ["docs/rules.md"]


def test_locate_refuses_a_prefix_outside_the_repo(repo) -> None:
    """The walk never leaves the repository, like every other gate operation."""
    with pytest.raises(gs.GateError):
        gs.locate("x", under="../")


def test_find_files_matches_a_glob_by_name(repo) -> None:
    """Name search is the other half of locating: which files exist at all."""
    (repo / "scripts/u.py").write_text("")
    assert gs.find_files("scripts/*.py") == ["scripts/t.py", "scripts/u.py"]
    assert gs.find_files("**/*.md") == ["README.md", "docs/rules.md"]


def test_find_files_refuses_a_glob_that_leaves_the_repo(repo) -> None:
    """`../*` reached the home directory on first review; a glob is a path too."""
    (repo.parent / "outside.md").write_text("")
    with pytest.raises(gs.GateError):
        gs.find_files("../*.md")
    with pytest.raises(gs.GateError):
        gs.find_files("scripts/../../*.md")


def test_every_skipped_directory_is_skipped_by_both_tools(repo) -> None:
    """All six never-candidate directories, for the name search and the content search."""
    for d in sorted(gs._SKIPPED_DIRS):
        (repo / d).mkdir()
        (repo / d / "x.py").write_text("b = 2\n")
    assert gs.locate(r"b = 2") == ["scripts/t.py"]
    assert gs.find_files("**/*.py") == ["scripts/t.py"]
