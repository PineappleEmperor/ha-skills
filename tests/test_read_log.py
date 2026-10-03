"""Unit tests for scripts/read_log.py, the hook that records what was actually read.

Load the standalone script by path; it is not an importable package.
"""

import hashlib
import importlib.util
import io
import json
import pathlib

import pytest

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"
_SPEC = importlib.util.spec_from_file_location("read_log", _SCRIPTS / "read_log.py")
rl = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(rl)


def _file(tmp_path: pathlib.Path, lines: int) -> pathlib.Path:
    path = tmp_path / "doc.md"
    path.write_text("".join(f"line {n}\n" for n in range(lines)))
    return path


def _read(path: pathlib.Path, **args: object) -> dict:
    return {
        "session_id": "s1",
        "tool_name": "Read",
        "tool_input": {"file_path": str(path), **args},
    }


def test_a_whole_read_is_recorded_with_its_hash(tmp_path) -> None:
    """The hash binds the read to the content that was on disk when it happened."""
    path = _file(tmp_path, 10)
    entry = rl.record(_read(path))
    assert entry == {
        "session": "s1",
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "full": True,
    }


@pytest.mark.parametrize(
    ("args", "full"),
    [
        ({"offset": 1}, True),
        ({"offset": 5}, False),
        ({"limit": 3}, False),
        ({"limit": 10}, True),
        ({"offset": 1, "limit": 50}, True),
    ],
)
def test_a_slice_is_not_a_whole_read(tmp_path, args, full) -> None:
    """Only a read that covers every line counts as reading the file."""
    assert rl.record(_read(_file(tmp_path, 10), **args))["full"] is full


def test_a_file_past_the_default_limit_is_not_read_whole(tmp_path) -> None:
    """Read stops at 2000 lines without a limit, so a longer file is only partly seen."""
    assert rl.record(_read(_file(tmp_path, rl.DEFAULT_LIMIT + 1)))["full"] is False


def test_a_governance_get_file_is_a_whole_read(tmp_path, monkeypatch) -> None:
    """get_file emits the whole file, resolved against the repository its gate governs."""
    path = _file(tmp_path, 3000)
    monkeypatch.setitem(rl.GATE_ROOTS, "mcp__governance-x__", tmp_path)
    payload = {
        "session_id": "s1",
        "tool_name": "mcp__governance-x__get_file",
        "tool_input": {"path": "doc.md"},
    }
    entry = rl.record(payload)
    assert entry is not None
    assert entry["full"] is True
    assert entry["path"] == str(path.resolve())


def test_other_tools_and_missing_files_are_not_recorded(tmp_path) -> None:
    """Only a read of a file that exists is a read."""
    assert rl.record({"tool_name": "Bash", "tool_input": {"command": "ls"}}) is None
    assert rl.record(_read(tmp_path / "gone.md")) is None


def test_the_hook_appends_one_line_and_prints_nothing(
    tmp_path, monkeypatch, capsys
) -> None:
    """The log is append-only JSON lines; the hook never speaks on the happy path."""
    log = tmp_path / "reads.jsonl"
    monkeypatch.setattr(rl, "LOG", log)
    path = _file(tmp_path, 2)
    for _ in range(2):
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(_read(path))))
        assert rl.main() == 0
    assert capsys.readouterr().out == ""
    assert [json.loads(line)["path"] for line in log.read_text().splitlines()] == [
        str(path.resolve())
    ] * 2


def test_unparseable_input_is_ignored(monkeypatch) -> None:
    """A payload the hook cannot read records nothing and blocks nothing."""
    monkeypatch.setattr("sys.stdin", io.StringIO("not json"))
    assert rl.main() == 0
