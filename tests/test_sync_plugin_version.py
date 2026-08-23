"""Unit tests for scripts/sync_plugin_version.py.

The workflow that calls this runs once per release, so a bug in it is discovered by
publishing — the most expensive place to find one. Everything except the git push is
therefore decided here.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location("sync", _SCRIPTS / "sync_plugin_version.py")
sync = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(sync)


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "plugins/ha/.claude-plugin").mkdir(parents=True)
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / "plugins/ha/.claude-plugin/plugin.json").write_text(
        json.dumps({"name": "ha", "version": "1.0.0"}, indent=2) + "\n")
    (tmp_path / ".claude-plugin/marketplace.json").write_text(
        json.dumps({"plugins": [{"name": "ha", "version": "1.0.0"}]}, indent=2) + "\n")
    return tmp_path


def _versions(repo):
    a = json.loads((repo / "plugins/ha/.claude-plugin/plugin.json").read_text())["version"]
    b = json.loads((repo / ".claude-plugin/marketplace.json").read_text())["plugins"][0]["version"]
    return a, b


def test_both_manifests_take_the_tag_version(repo) -> None:
    """One tag, two files — a sync that updates only one is the drift it exists to stop."""
    changed = sync.patch(repo, "2.1.0", "ha")
    assert _versions(repo) == ("2.1.0", "2.1.0")
    assert len(changed) == 2


def test_rerunning_changes_nothing(repo) -> None:
    """The workflow can re-run on a re-published release; a no-op must stay a no-op."""
    sync.patch(repo, "2.1.0", "ha")
    assert sync.patch(repo, "2.1.0", "ha") == []


def test_json_shape_survives(repo) -> None:
    """Other keys and the trailing newline are what the next diff is measured against."""
    sync.patch(repo, "2.1.0", "ha")
    text = (repo / "plugins/ha/.claude-plugin/plugin.json").read_text()
    assert text.endswith("}\n")
    assert json.loads(text)["name"] == "ha"


def test_prerelease_versions_are_accepted(repo) -> None:
    """An rc tag is a legitimate override; the marketplace repo just doesn't cut them itself."""
    assert sync.main(["--version", "v2.0.0rc1", "--root", str(repo)]) == 0
    assert _versions(repo) == ("2.0.0rc1", "2.0.0rc1")


def test_a_tag_that_is_not_a_version_is_refused(repo) -> None:
    """`release.yml` proved this matters: a crafted tag reaches the shell otherwise."""
    with pytest.raises(SystemExit):
        sync.main(["--version", "latest", "--root", str(repo)])


def test_check_mode_reports_drift_without_writing(repo) -> None:
    assert sync.main(["--version", "9.9.9", "--root", str(repo), "--check"]) == 1
    assert _versions(repo) == ("1.0.0", "1.0.0")


def test_unknown_plugin_name_fails_loudly(repo) -> None:
    """A renamed plugin must not silently sync nothing."""
    with pytest.raises(SystemExit):
        sync.patch(repo, "2.0.0", "not-a-plugin")
