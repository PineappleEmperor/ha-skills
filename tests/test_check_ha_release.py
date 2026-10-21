"""Tests for the release-freshness check.

The fetch is injected in every test, so none of these touch the network. The real
`freshness.md` is read once, deliberately: a check whose parser silently stops matching the
file it parses is the failure mode worth guarding, and that only shows up against the real
bytes.
"""

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import check_ha_release as chr_

ROW = (
    "| HA release the skill is current for | `2026.9` | 2026-09-19 | cmd | consumers |"
)
TABLE = f"""# Cached facts

| Cached fact | Value | Captured | Re-derive with | Consumers |
|---|---|---|---|---|
{ROW}
| HA minimum Python | `3.14` | 2026-09-12 | a page | a workflow |
"""


def pypi(version: str):
    """A fake fetch returning PyPI's payload shape for one version."""
    return lambda _url: json.dumps({"info": {"version": version}})


def boom(_url: str) -> str:
    """A fake fetch that fails the way a network outage does."""
    raise OSError("network is unreachable")


def test_captured_minor_reads_the_named_row() -> None:
    """The row is found by its exact first cell."""
    assert chr_.captured_minor(TABLE) == (2026, 9)


def test_captured_minor_ignores_other_rows() -> None:
    """A version-shaped value in another row is not mistaken for it."""
    assert chr_.captured_minor(TABLE.replace("3.14", "2027.1")) == (2026, 9)


def test_captured_minor_rejects_a_missing_row() -> None:
    """A renamed row fails loudly rather than passing."""
    with pytest.raises(ValueError, match="no row named"):
        chr_.captured_minor("| Something else | `2026.9` |")


def test_captured_minor_rejects_an_unparseable_value() -> None:
    """A value that is not a version fails loudly."""
    with pytest.raises(ValueError, match="not a YYYY.M version"):
        chr_.captured_minor(ROW.replace("`2026.9`", "`soon`"))


def test_latest_minor_drops_the_patch() -> None:
    """A patch release is the same guidance window."""
    assert chr_.latest_minor(pypi("2026.9.2")) == (2026, 9)


def test_current_exits_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Captured equal to PyPI is current."""
    f = tmp_path / "freshness.md"
    f.write_text(TABLE, encoding="utf-8")
    assert chr_.main(["--file", str(f)], fetch=pypi("2026.9.2")) == 0
    assert "current for HA 2026.9" in capsys.readouterr().out


def test_behind_exits_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Captured behind PyPI fails, naming both minors."""
    f = tmp_path / "freshness.md"
    f.write_text(TABLE, encoding="utf-8")
    assert chr_.main(["--file", str(f)], fetch=pypi("2026.10.0")) == 1
    assert "PyPI has 2026.10" in capsys.readouterr().err


def test_ahead_of_pypi_is_not_a_failure(tmp_path: Path) -> None:
    """A beta captured before the final ships must not fail the build."""
    f = tmp_path / "freshness.md"
    f.write_text(TABLE.replace("`2026.9`", "`2026.10`"), encoding="utf-8")
    assert chr_.main(["--file", str(f)], fetch=pypi("2026.9.2")) == 0


def test_a_new_year_compares_correctly(tmp_path: Path) -> None:
    """2027.1 is ahead of 2026.12 — a plain numeric compare on the minor would miss it."""
    f = tmp_path / "freshness.md"
    f.write_text(TABLE.replace("`2026.9`", "`2026.12`"), encoding="utf-8")
    assert chr_.main(["--file", str(f)], fetch=pypi("2027.1.0")) == 1


def test_unreadable_file_exits_two(capsys: pytest.CaptureFixture[str]) -> None:
    """A missing file is 'cannot tell', not 'behind'."""
    missing = "/nonexistent/freshness.md"
    assert chr_.main(["--file", missing], fetch=pypi("2026.9.2")) == 2
    assert "cannot read the captured release" in capsys.readouterr().err


def test_file_flag_without_a_path_exits_two(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A truncated argument must not fall through to the 'behind' exit code."""
    assert chr_.main(["--file"], fetch=pypi("2026.9.2")) == 2
    assert "--file needs a path" in capsys.readouterr().err


def test_unreachable_pypi_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An outage must not read as 'behind' and turn the build red for the wrong reason."""
    f = tmp_path / "freshness.md"
    f.write_text(TABLE, encoding="utf-8")
    assert chr_.main(["--file", str(f)], fetch=boom) == 2
    assert "cannot read the latest release" in capsys.readouterr().err


def test_the_real_freshness_table_still_parses() -> None:
    """The parser and the file it parses must not drift apart silently."""
    real = Path(__file__).resolve().parents[1] / chr_.DEFAULT_FILE
    year, minor = chr_.captured_minor(real.read_text(encoding="utf-8"))
    assert year >= 2026
    assert 1 <= minor <= 12
