"""Unit tests for scripts/skill_audit.py.

The shell version could only be tested by running the whole script against a fixture
repo and grepping its output, which is why several of its checks silently did nothing
for weeks. Each check here is a function, so each gets its own case.
"""

from __future__ import annotations

import importlib.util
import json
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


def test_shipped_scripts_must_match_the_ones_this_repo_runs(tmp_path) -> None:
    """The shipped copy is what integrations get, and it drifted from the repo's own.

    Two fixes landed in `scripts/` and never reached `templates/scripts/`, while the docs
    described the fixed behaviour. Nothing compared them: `check_self_diff` walks workflows
    only. A silent no-op here would restore exactly that blind spot, so assert both that it
    catches a difference and that it clears once the copies agree.
    """
    tmpl = tmp_path / "plugins/ha/skills/demo/templates"
    (tmpl / "scripts").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmpl / "scripts/tool.py").write_text("VALUE = 1\n")
    (tmp_path / "scripts/tool.py").write_text("VALUE = 2\n")

    fails, _ = audit.check_template_scripts_match(audit.Repo(tmp_path))
    assert any("scripts/tool.py" in f for f in fails)

    (tmp_path / "scripts/tool.py").write_text("VALUE = 1\n")
    assert audit.check_template_scripts_match(audit.Repo(tmp_path)) == ([], [])


def test_shipped_script_absent_from_this_repo_is_not_drift(tmp_path) -> None:
    """Not every shipped file is one the skill repo runs; a missing counterpart is fine."""
    tmpl = tmp_path / "plugins/ha/skills/demo/templates"
    (tmpl / "scripts").mkdir(parents=True)
    (tmpl / "scripts/only_shipped.py").write_text("VALUE = 1\n")
    assert audit.check_template_scripts_match(audit.Repo(tmp_path)) == ([], [])


def test_list_mode_names_every_check(capsys) -> None:
    """The skill points readers at --list instead of enumerating rules that go stale."""
    assert audit.main(["--list"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert len(out) == len(audit.CHECKS)
    assert all(line.split()[0] for line in out)


def test_a_third_pr_opener_is_still_refused(repo) -> None:
    """The sanctioned list is short on purpose: a workflow opening a PR acts as an author."""
    _wf(repo, "helpful.yml", "jobs:\n  x:\n    steps:\n      - run: gh pr create --title hi\n")
    fails, _ = audit.check_pr_openers(audit.Repo(repo))
    assert any("helpful.yml opens PRs" in f for f in fails)


def test_a_marked_opener_states_its_own_reason(repo) -> None:
    """A repo with a different delivery model declares its exception in its own file.

    The shipped audit should not carry the filenames of repos it never runs in.
    """
    _wf(repo, "sync_plugin_version.yml",
        "# skill-audit: sanctioned-opener — the version lives in a committed file\n"
        "jobs:\n  x:\n    steps:\n      - run: gh pr create --title v\n")
    fails, _ = audit.check_pr_openers(audit.Repo(repo))
    assert fails == []


def test_unverifiable_checks_warn_rather_than_passing(repo, monkeypatch) -> None:
    """A check that cannot run must say NOT CHECKED, not stay silent.

    Observed on a live run: `Skill Audit` passed in CI while the same script failed
    locally, because CI could not query GitHub and the check returned nothing. A check
    that only fails where nobody looks is worse than no check.
    """
    class _Missing:
        def __call__(self, *a, **k):
            raise OSError("gh not found")
    monkeypatch.setattr(audit.subprocess, "run", _Missing())

    _, warns = audit.check_required_status_checks(audit.Repo(repo))
    assert any("NOT CHECKED" in w for w in warns)

    _wf(repo, "dependency_review.yml", "jobs:\n  review:\n    steps: []\n")
    _, warns = audit.check_dependency_graph(audit.Repo(repo))
    assert any("NOT CHECKED" in w for w in warns)


def test_dependency_graph_off_is_a_failure(repo, monkeypatch) -> None:
    """Seven workflows green and Dependency review red alone — the observed failure."""
    _wf(repo, "dependency_review.yml", "jobs:\n  review:\n    steps: []\n")

    class _Fake:
        def __init__(self, out, rc=0): self.stdout, self.returncode = out, rc
    calls = []

    def fake_run(cmd, **k):
        calls.append(cmd)
        if "repo" in cmd and "view" in cmd:
            return _Fake("owner/repo\n")
        return _Fake("", 1)          # sbom probe fails: graph disabled
    monkeypatch.setattr(audit.subprocess, "run", fake_run)

    fails, _ = audit.check_dependency_graph(audit.Repo(repo))
    assert any("dependency graph is off" in f for f in fails)


def test_no_dependency_review_workflow_means_nothing_to_check(repo, monkeypatch) -> None:
    """A repo that does not ship the workflow has no prerequisite to satisfy."""
    monkeypatch.setattr(audit.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not query")))
    assert audit.check_dependency_graph(audit.Repo(repo)) == ([], [])


def test_platforms_naming_a_missing_module_fails(repo) -> None:
    """The live defect: PLATFORMS = ["sensor"] with no sensor.py, inert until forwarded."""
    pkg = repo / "custom_components/acmedev"
    pkg.mkdir(parents=True)
    (pkg / "manifest.json").write_text('{"domain": "acmedev"}')
    (pkg / "const.py").write_text('DOMAIN = "acmedev"\nPLATFORMS = ["sensor", "notify"]\n')
    (pkg / "notify.py").write_text("")
    fails, _ = audit.check_platforms_have_modules(audit.Repo(repo))
    assert len(fails) == 1 and "sensor" in fails[0] and "notify" not in fails[0]


def test_platform_enum_form_is_understood(repo) -> None:
    """Both spellings appear in real integrations."""
    pkg = repo / "custom_components/acmedev"
    pkg.mkdir(parents=True)
    (pkg / "manifest.json").write_text('{"domain": "acmedev"}')
    (pkg / "const.py").write_text("PLATFORMS = [Platform.SENSOR, Platform.NOTIFY]\n")
    (pkg / "sensor.py").write_text("")
    fails, _ = audit.check_platforms_have_modules(audit.Repo(repo))
    assert len(fails) == 1 and "notify" in fails[0]


def test_matching_platforms_pass(repo) -> None:
    pkg = repo / "custom_components/acmedev"
    pkg.mkdir(parents=True)
    (pkg / "manifest.json").write_text('{"domain": "acmedev"}')
    (pkg / "const.py").write_text('PLATFORMS = ["notify"]\n')
    (pkg / "notify.py").write_text("")
    assert audit.check_platforms_have_modules(audit.Repo(repo)) == ([], [])


def _ruleset(repo, *contexts) -> None:
    (repo / "ruleset.json").write_text(json.dumps(
        {"rules": [{"type": "required_status_checks",
                    "parameters": {"required_status_checks":
                                   [{"context": c} for c in contexts]}}]}))


def test_a_required_context_no_job_produces_fails(repo) -> None:
    """The observed defect, twice: a ruleset requiring a check nothing reports.

    Checking that workflow FILES exist cannot catch this — the failure is a name in the
    ruleset with no job on the other end. Every other check goes green and the PR is
    unmergeable with nothing to point at.
    """
    _wf(repo, "pr-checks.yml", "jobs:\n  label:\n    name: CC labelling\n    steps: []\n")
    _ruleset(repo, "CC labelling", "Version validation")
    fails, _ = audit.check_required_contexts_have_producers(audit.Repo(repo))
    assert len(fails) == 1 and "Version validation" in fails[0]


def test_every_required_context_produced_passes(repo) -> None:
    _wf(repo, "pr-checks.yml", "jobs:\n  label:\n    name: CC labelling\n    steps: []\n")
    _ruleset(repo, "CC labelling")
    assert audit.check_required_contexts_have_producers(audit.Repo(repo)) == ([], [])


def test_a_job_without_a_name_is_known_by_its_id(repo) -> None:
    """GitHub names the check-run for the job id when the job declares no name."""
    _wf(repo, "a.yml", "jobs:\n  review:\n    steps: []\n")
    _ruleset(repo, "review")
    assert audit.check_required_contexts_have_producers(audit.Repo(repo)) == ([], [])


def test_the_shipped_ruleset_is_checked_against_the_shipped_workflows(tmp_path) -> None:
    """What ships is what scaffolds; an orphan here bricks every repo built from it."""
    tmpl = tmp_path / "plugins/ha/skills/demo/templates"
    (tmpl / ".github/workflows").mkdir(parents=True)
    (tmpl / ".github/workflows/a.yml").write_text("jobs:\n  x:\n    name: Real\n    steps: []\n")
    (tmpl / "ruleset.json").write_text(json.dumps(
        {"rules": [{"type": "required_status_checks",
                    "parameters": {"required_status_checks": [{"context": "Imaginary"}]}}]}))
    fails, _ = audit.check_required_contexts_have_producers(audit.Repo(tmp_path))
    assert len(fails) == 1 and "Imaginary" in fails[0]


def test_live_required_contexts_warn_when_gh_is_missing(repo, monkeypatch) -> None:
    """Unverifiable must say NOT CHECKED; a silent pass is how this survived before."""
    class _Missing:
        def __call__(self, *a, **k):
            raise OSError("gh not found")
    monkeypatch.setattr(audit.subprocess, "run", _Missing())
    _, warns = audit.check_live_required_contexts(audit.Repo(repo))
    assert any("NOT CHECKED" in w for w in warns)


def test_live_ruleset_orphan_fails(repo, monkeypatch) -> None:
    """A repo protected from the GitHub UI has no ruleset.json to compare against."""
    _wf(repo, "pr-checks.yml", "jobs:\n  label:\n    name: CC labelling\n    steps: []\n")

    class _Fake:
        def __init__(self, out, rc=0): self.stdout, self.returncode = out, rc

    def fake_run(cmd, **k):
        if "view" in cmd:
            return _Fake("owner/repo\n")
        if cmd[-1] == ".default_branch":
            return _Fake("main\n")
        return _Fake('["CC labelling","Version validation"]')
    monkeypatch.setattr(audit.subprocess, "run", fake_run)

    fails, _ = audit.check_live_required_contexts(audit.Repo(repo))
    assert len(fails) == 1 and "Version validation" in fails[0]
