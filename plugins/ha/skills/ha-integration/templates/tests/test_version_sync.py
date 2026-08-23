"""Unit tests for scripts/version_sync.py.

Load the standalone script by path; it is not an importable package.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location("version_sync", _SCRIPTS / "version_sync.py")
vs = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(vs)


def _repo(tmp_path, *, workflow="3.14", ruff="py314", pyright="3.14", pin=True):
    """A repo declaring the python version in each of the places that carry it."""
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/python_validate.yml").write_text(
        f'jobs:\n  lint:\n    steps:\n      - with:\n          python-version: "{workflow}"\n')
    (tmp_path / "pyproject.toml").write_text(f'[tool.ruff]\ntarget-version = "{ruff}"\n')
    (tmp_path / "pyrightconfig.json").write_text(json.dumps({"pythonVersion": pyright}))
    (tmp_path / "requirements.test.txt").write_text(
        "pytest-homeassistant-custom-component==0.13.354\n" if pin
        else "pytest-homeassistant-custom-component\n")
    return tmp_path


def test_agreeing_versions_pass(tmp_path) -> None:
    """The ordinary case: one version, written four times, all the same."""
    assert vs.problems(_repo(tmp_path)) == []


def test_a_bump_left_behind_is_caught(tmp_path) -> None:
    """The failure this exists for: the workflow moved, the linters did not.

    CI stays green either way — ruff and pyright simply check against a version
    nobody runs — so only a comparison catches it.
    """
    found = vs.problems(_repo(tmp_path, workflow="3.15"))
    assert len(found) == 1
    assert "python version disagrees" in found[0]
    assert "python_validate.yml=3.15" in found[0]


def test_unpinned_test_harness_is_caught(tmp_path) -> None:
    """An unpinned harness follows whatever HA published today."""
    found = vs.problems(_repo(tmp_path, pin=False))
    assert any("does not pin pytest-homeassistant-custom-component" in f for f in found)


def test_absent_files_are_not_a_disagreement(tmp_path) -> None:
    """A repo that declares the version once has nothing to disagree with."""
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/python_validate.yml").write_text(
        'jobs:\n  lint:\n    steps:\n      - with:\n          python-version: "3.14"\n')
    assert vs.problems(tmp_path) == []


def test_a_single_declaration_warns_rather_than_passing_silently(tmp_path) -> None:
    """One value cannot disagree with anything; a green tick there is work not done.

    This repo printed "declared python versions agree" while declaring exactly one
    version, having neither pyproject.toml nor pyrightconfig.json.
    """
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/python_validate.yml").write_text(
        "jobs:\n  t:\n    steps:\n      - uses: actions/setup-python@v6\n"
        "        with:\n          python-version: '3.14'\n")
    assert vs.problems(tmp_path) == []
    warns = vs.thin(tmp_path)
    assert len(warns) == 1 and "nothing to compare" in warns[0]
    assert "pyrightconfig.json" in warns[0]


def test_two_declarations_are_compared_not_warned(tmp_path) -> None:
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/python_validate.yml").write_text(
        "jobs:\n  t:\n    steps:\n      - uses: actions/setup-python@v6\n"
        "        with:\n          python-version: '3.14'\n")
    (tmp_path / "pyrightconfig.json").write_text('{"pythonVersion": "3.13"}\n')
    assert vs.thin(tmp_path) == []
    assert any("disagrees" in p for p in vs.problems(tmp_path))
