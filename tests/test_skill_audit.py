"""Unit tests for scripts/skill_audit.py.

The shell version could only be tested by running the whole script against a fixture
repo and grepping its output, which is why several of its checks silently did nothing
for weeks. Each check here is a function, so each gets its own case.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location("skill_audit", _SCRIPTS / "skill_audit.py")
audit = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(audit)


@pytest.fixture
def repo(tmp_path):
    """A repo with the workflow directory present and nothing else."""
    (tmp_path / ".github/workflows").mkdir(parents=True)
    return tmp_path


def _wf(repo, name, body):
    (repo / ".github/workflows" / name).write_text(body)


def test_missing_canonical_workflows_are_listed(repo) -> None:
    fails, _ = audit.check_canonical_files(audit.Repo(repo))
    assert any("pr-checks.yml" in f for f in fails)
    assert any(".gitignore" in f for f in fails)


def test_bare_tag_pins_fail(repo) -> None:
    """A tag can be repointed at new code that runs with the workflow's token."""
    _wf(repo, "a.yml", "jobs:\n  x:\n    steps:\n      - uses: actions/checkout@v7\n")
    fails, _ = audit.check_action_pins(audit.Repo(repo))
    assert len(fails) == 1 and "not pinned to a commit SHA" in fails[0]


def test_sha_without_a_version_comment_fails(repo) -> None:
    """A 40-character hex string tells a reader nothing on its own."""
    _wf(repo, "a.yml", f"jobs:\n  x:\n    steps:\n      - uses: actions/checkout@{'a' * 40}\n")
    fails, _ = audit.check_action_pins(audit.Repo(repo))
    assert len(fails) == 1 and "no version comment" in fails[0]


def test_documented_mutable_refs_are_exempt(repo) -> None:
    """hacs and hassfest each document a mutable ref; pinning stops tracking them."""
    _wf(repo, "a.yml", "jobs:\n  x:\n    steps:\n      - uses: hacs/action@main\n"
                       "      - uses: home-assistant/actions/hassfest@master\n")
    assert audit.check_action_pins(audit.Repo(repo)) == ([], [])


def test_two_release_body_writers_fail(repo) -> None:
    """Two writers race, and the loser's output is what users read."""
    _wf(repo, "a.yml", 'jobs:\n  x:\n    steps:\n      - run: gh release edit v1 --notes-file n.md\n')
    _wf(repo, "b.yml", 'jobs:\n  y:\n    steps:\n      - uses: softprops/action-gh-release@v3\n'
                       '        with:\n          generate_release_notes: true\n')
    fails, _ = audit.check_single_body_writer(audit.Repo(repo))
    assert len(fails) == 1 and "more than one workflow step writes the release body" in fails[0]


def test_v6_drafter_categories_fail(repo) -> None:
    """The v6 shape parses, matches nothing, and resolves every release as a patch."""
    (repo / ".github/release-drafter.yml").write_text(
        "categories:\n  - title: Features\n    semver-increment: minor\n    labels:\n      - feature\n")
    fails, _ = audit.check_drafter_categories(audit.Repo(repo))
    assert len(fails) == 1 and "v6 top-level" in fails[0]


def test_when_shaped_categories_pass(repo) -> None:
    (repo / ".github/release-drafter.yml").write_text(
        "categories:\n  - title: Features\n    semver-increment: minor\n    when:\n"
        "      labels:\n        - feature\n")
    assert audit.check_drafter_categories(audit.Repo(repo)) == ([], [])


def test_pr_opener_must_be_draft_and_actor_gated(repo) -> None:
    """A PR opened with a shared token otherwise appears to be written by its owner."""
    _wf(repo, "auto_draft_pr.yml", "jobs:\n  draft:\n    steps:\n      - run: gh pr create --title x\n")
    fails, _ = audit.check_pr_openers(audit.Repo(repo))
    assert any("gate on the actor" in f for f in fails)
    assert any("must open the PR as a draft" in f for f in fails)


def test_multiline_docstrings_in_integration_code_fail(tmp_path) -> None:
    """Module docstrings are exempt; functions and classes are not."""
    cc = tmp_path / "custom_components/demo"
    cc.mkdir(parents=True)
    (cc / "__init__.py").write_text(
        '"""Module docstring.\n\nStill fine, multiple lines.\n"""\n\n\n'
        'def f():\n    """One line."""\n\n\n'
        'def g():\n    """First.\n\n    Second.\n    """\n')
    fails, _ = audit.check_docstrings(audit.Repo(tmp_path))
    assert len(fails) == 1 and "g" in fails[0]


def test_done_rules_without_tests_fail(tmp_path) -> None:
    """A `done` with no test is a claim, not evidence."""
    cc = tmp_path / "custom_components/demo"
    cc.mkdir(parents=True)
    (cc / "quality_scale.yaml").write_text("rules:\n  config-flow: done\n  diagnostics: todo\n")
    fails, _ = audit.check_claims_have_tests(audit.Repo(tmp_path))
    assert any("no tests/ directory" in f for f in fails)


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


def test_hook_without_the_subject_guards_fails(tmp_path) -> None:
    """A hook that only measures length lets a well-formed empty subject through."""
    hooks = tmp_path / ".githooks"
    hooks.mkdir()
    hook = hooks / "commit-msg"
    hook.write_text("#!/usr/bin/env bash\n[ ${#1} -gt 72 ] && exit 1\nexit 0\n")
    hook.chmod(0o755)

    fails, _ = audit.check_commit_hook(audit.Repo(tmp_path))
    assert any("Conventional Commit subject shape" in f for f in fails)
    assert any("editorialising" in f for f in fails)

    hook.write_text("case x in feat|fix|docs) ;; esac\n# editorialising subjects rejected\n")
    hook.chmod(0o755)
    fails, _ = audit.check_commit_hook(audit.Repo(tmp_path))
    assert fails == []


def _skill(root, name, frontmatter, body="body\n"):
    d = root / "plugins/ha/skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n{body}")


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


def test_list_mode_names_every_check(capsys) -> None:
    """The skill points readers at --list instead of enumerating rules that go stale."""
    assert audit.main(["--list"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert len(out) == len(audit.CHECKS)
    assert all(line.split()[0] for line in out)


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


def test_a_third_pr_opener_is_still_refused(repo) -> None:
    """The sanctioned list is short on purpose: a workflow opening a PR acts as an author."""
    _wf(repo, "helpful.yml", "jobs:\n  x:\n    steps:\n      - run: gh pr create --title hi\n")
    fails, _ = audit.check_pr_openers(audit.Repo(repo))
    assert any("helpful.yml opens PRs" in f for f in fails)


def test_the_version_sync_may_open_its_own_pr(repo) -> None:
    """It proposes a change to a protected branch; the alternative is standing write access."""
    _wf(repo, "sync_plugin_version.yml", "jobs:\n  x:\n    steps:\n      - run: gh pr create --title v\n")
    fails, _ = audit.check_pr_openers(audit.Repo(repo))
    assert not any("sync_plugin_version.yml" in f for f in fails)
