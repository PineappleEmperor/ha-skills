# Skill Refresh to 2026.9 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the ha-integration skill's guidance to Home Assistant 2026.9 and leave a
check that goes red the week the next release lands.

**Architecture:** Reference-file edits through the governance gate, grouped by file, one
commit each; a new `freshness.md` row and procedure; a small tracked script with a test,
run by this repository's own `ci.yml`, that compares the captured release with PyPI.

**Tech Stack:** the governance MCP gate (`mcp__governance__get_docs` → `get_file` →
`patch_file`), Python 3.14, pytest, `urllib`, ha-skills `ci.yml`.

**Spec:** `docs/superpowers/specs/2026-09-15-five-repo-sweep-design.md`, sections *Step 0*
and *Monthly release mechanism*. Findings: `.tmp/plan/step0-findings.md` for the 2026.6–2026.9
changes, `.tmp/plan/decisions.md` for the maintainer's decisions (Tasks 7 and 8 below come from
its items 22–30 and 33; item 32 was withdrawn on the evidence, and Task 7 records why; item 31, the brand-dimension check, is a `ha-integration-ci`
change and belongs to the spec's *What must change in the CI repositories first*, not
here).

## Global Constraints

- Nothing is committed or pushed until the maintainer says go. Steps below say "commit"
  for the executor's sequence; the actual commits wait for that go.
- `reference/`, `templates/`, `scripts/`, `tests/`, `.github/workflows/` and
  `docs/backlog.md` are written only through the gate. This repository's `README.md` is
  not governed and is edited directly. Editing a governing doc rotates the keys of the
  tiers it governs, so re-read rather than resend.
- Prose has one source: a fact owned by a CI README or another reference file is pointed
  at, not restated. A pointer names the file and the heading.
- No AI-attribution anywhere. Commit subjects: one imperative, `docs:`/`feat:`/`test:`/
  `ci:`, lowercase after the colon, no period, no `and`.
- The reviewer agent runs on the branch before the push is handed over; the branch
  touches `ci.yml`, so the push is the maintainer's over SSH.
- Branch name: `feat/refresh-2026-9`.

---

### Task 1: `patterns.md` — the 2026.6–2026.9 changes

**Files:**
- Modify: `plugins/ha/skills/ha-integration/reference/patterns.md` — the contents list, *`config_flow.py`*, *Entity platform files*, *Custom services*, and a new section *What changed in recent releases* before *File structure conventions*

**Interfaces:**
- Produces: the heading *What changed in recent releases*, pointed at by Task 3's freshness row and Task 2's panels section.

- [ ] **Step 1: Read the file through the gate**

`mcp__governance__get_docs(tier="plugins/ha/skills/ha-integration/reference/")`, then
`get_file` on `patterns.md`. Read the whole file.

- [ ] **Step 2: Patch `config_flow.py`** — after the `OptionsFlow` bullet insert:

```
- An update listener (`entry.async_on_unload(entry.add_update_listener(...))`) and a flow
  that reloads on its own (`async_update_reload_and_abort()`, or
  `_abort_if_unique_id_configured(reload_on_update=True)`) must not be combined: HA
  2026.6 deprecates the pair, since the entry reloads twice, and *What changed in recent
  releases* below says when it becomes an error. Keep the listener and call
  `async_update_and_abort()`, or drop the listener.
- Advanced mode is gone from flows: `context["show_advanced_options"]` no longer exists
  and the `show_advanced_options` property returns `True` unconditionally until its
  removal (the table below); an option that used to hide behind advanced mode goes in a
  `section` of the schema instead.
```

- [ ] **Step 3: Patch *Entity platform files*** — add, after the `DeviceInfo` bullet and
its snippet:

```
- A device belongs to one config entry, since HA 2026.8. `DeviceInfo` no longer accepts
  `via_device`, `default_manufacturer`, `default_model` or `default_name`: link a parent
  with `via_device_id=dr.async_get_device_id_by_identifier(hass, (DOMAIN, parent_id),
  config_entry_id=entry.entry_id)`, and name things with `manufacturer`, `model`, `name`.
  Look a device up with `registry.async_get_device_by_identifier((DOMAIN, id),
  entry.entry_id)` or `registry.async_get(device_id)`, never `registry.devices.get(...)`
  or `async_get_device(identifiers=...)`; the old spellings warn now and go on the dates
  the table below gives. An entity that attaches a device carries both a `unique_id`
  and a config entry, or setup raises from the same removal.
- Units: `UnitOfDensity` (`g/m³`, `mg/m³`, `μg/m³`, `μg/ft³`) and `UnitOfRatio` (`ppm`,
  `ppb`, `%` as `UnitOfRatio.PERCENTAGE`) replace the `CONCENTRATION_*` constants since
  2026.7 (`CONCENTRATION_PARTS_PER_CUBIC_METER` is deprecated with no replacement), and
  the bare `PERCENTAGE` is deprecated as a unit of measurement though the constant itself
  stays; a sensor's `native_unit_of_measurement` takes the enum member.
```

- [ ] **Step 4: Patch *Custom services*** — replace the sentence
"then resolve the HA device → config entry in the handler via
`device_registry.async_get(hass).async_get(id)`." (the period included) with:

```
then resolve the device and its config entry in the handler with
`dr.async_get_device_and_config_entry_for_domain(hass, device_id, domain=DOMAIN)`, which
returns `(DeviceEntry | None, ConfigEntry | None)`; reading
`device.config_entries` or `device.primary_config_entry` has been deprecated since
2026.8 and warns at runtime from 2026.10 (its removal is in *What changed in recent
releases*).
```

The replacement carries its own final period.

- [ ] **Step 5: Add the section** *What changed in recent releases*, immediately before
`### File structure conventions`; in the contents list at the top of the file add the
line `- What changed in recent releases` directly after `- Config entry migration`:

```
### What changed in recent releases

The changes since the skill's last capture that a custom integration can meet, oldest
first; the release the skill is current for is the row in `reference/freshness.md`, and
the monthly procedure there is what extends this table. Each item is applied above where
it belongs; this table is the index and the deadline.

| Release | Change | Old → new | Gone in | Post |
|---|---|---|---|---|
| 2026.6 | update listener with a reloading flow method | keep one of the two, or `async_update_and_abort()` | error from 2026.12 | 2026-05-07 |
| 2026.6 | advanced mode in flows | `show_advanced_options` (deprecated, always `True`) and its context key → a schema `section` | 2027.6 | 2026-05-26 |
| 2026.6 | `BrowseMediaSource.domain` required | `domain=None` → the integration's domain; root listings are `RootBrowseMediaSource` | hard change | 2026-05-20 |
| 2026.6 | conditions and scripts are objects with a lifecycle | call `condition.async_check(...)`, then `async_unload()`; `await script.async_unload()` | 2027.1 | 2026-05-13 |
| 2026.6 | MQTT `publish` typed arguments | `qos=None`/`retain=None` → `int`/`bool`; optional `message_expiry_interval=` | 2027.6 | 2026-05-11 |
| 2026.7 | device tracker entities | `battery_level`, `location_name` → a battery sensor, `in_zones` | 2027.7 | 2026-06-15 |
| 2026.7 | unit enums | `CONCENTRATION_*` → `UnitOfDensity`, `UnitOfRatio`; `PERCENTAGE` deprecated as a unit of measurement | 2027.8, per `DeprecatedConstantEnum` in `homeassistant/const.py` (the post gives none) | 2026-06-30 |
| 2026.7 | `async_initialize_triggers(home_assistant_start=)` | drop the argument; `hass.async_add_startup_job` for startup work | 2027.8 | 2026-06-30 |
| 2026.8 | one config entry per device | see *Entity platform files* and *Custom services* above | 2027.8 / 2027.9 | 2026-07-21, 2026-08-24 |
| 2026.8 | custom panels padded for the safe area | `config={"handle_safe_area": True}` to draw the edges yourself; see `reference/panels.md` | — | 2026-07-31 |
| 2026.8 | media sources can be searched | optional `async_search_media` | — | 2026-07-03 |
| 2026.8 | button event entities | custom event strings → the `ButtonEventType` members; optional, nothing deprecated | — | 2026-07-22 |
| 2026.8 / 2026.9 | device-registry WebSocket API: `config_entry_id` per device (2026.8), `remove` replaces `remove_config_entry` and child devices (2026.9) | see `reference/panels.md` | 2027.8 / 2027.9 | 2026-08-19 |
| 2026.9 | `configurator` | migrate to a config flow | 2027.10 | 2026-08-31 |
| 2026.9 | `VacuumEntity.battery_level` | a battery sensor | removed | release notes 2026-09-02 |
| 2026.9 / 2026.10 | device- and state-class pickers | `SelectSelector` → `DeviceClassSelector` (in 2026.9), `StateClassSelector` (2026.10) | — | 2026-09-04 |
| 2026.10 | `DeviceEntry.config_entries`, `primary_config_entry` | `config_entry_id`, `config_subentry_id` | 2027.10 | 2026-09-15 |
| 2026.10 | `modbus.get_hub` | `async_get_unit(hass, entry, connection_params, unit_id)`; the flow collects the connection itself | 2027.10 | 2026-09-02 |
| 2026.10 | OAuth2 helper errors | the helper's exceptions are `ConfigEntryNotReady`/`ConfigEntryAuthFailed` already; delete re-raise wrappers and the `oauth2_implementation_unavailable` string | — | 2026-09-07 |
| 2026.10 | lawn mower | `LawnMowerEntityFeature.STOP`, `LawnMowerActivity.IDLE` | — | 2026-09-11 |

The *Post* column is the date of the source: the developer-blog post at
https://developers.home-assistant.io/blog/, or, where it says so, the release notes;
*Gone in* is the removal the source states, or the code's own deprecation where the
source gives none.
```

Every row's *Post* date must be opened and read before the row is written. The table was
drafted offline from `.tmp/plan/step0-findings.md`, and four rows — `BrowseMediaSource.domain`,
the conditions/scripts lifecycle, MQTT `publish` typed arguments, and button event
entities — have no numbered finding behind them, so their API names and removal releases
are the draft's and nothing else. A row whose source will not confirm it comes out of the
table rather than shipping unverified; the same goes for `async_update_and_abort()`,
`UnitOfRatio.PERCENTAGE` and the safe-area spelling wherever they appear in this plan.

- [ ] **Step 5b: Reconcile the `vol.Schema` bullet with the fence rule Task 7 adds.**
`patterns.md`'s `config_flow.py` section says a schema is written "exactly as `ruff
format` leaves it (the shipped format check rejects hand-aligned columns)" — stated
without qualification, which Task 7's fence rule contradicts. The parenthesis becomes
"(the shipped format check collapses hand-aligned columns; `# fmt: off` is how a table
worth aligning survives it — see *Code style* in `reference/scaffold.md`)". The advice
itself stands: a config-flow schema is a list of entries, not a table, so it is left to
the formatter. Say that rather than implying the formatter always wins.

- [ ] **Step 6: Re-read the whole file** (`get_file` again) and check every pointer it
carries still names a heading that exists. Commit:
`docs: bring patterns up to 2026.9`.

---

### Task 2: `panels.md` — safe area and the device WebSocket API

**Files:**
- Modify: `plugins/ha/skills/ha-integration/reference/panels.md` — the registration snippet and *Registration has two traps*

- [ ] **Step 1: Patch the snippet's `async_register_panel` call** to add, after
`require_admin=True,`:

```
              config={"handle_safe_area": True},  # 2026.8: True means the panel handles the safe area itself; omitted, HA pads it
```

and change *Registration has two traps* to *Registration has three traps*, adding:

```
Third: since HA 2026.8 the frontend pads a custom panel for the device's safe area
unless the panel's `config` carries `"handle_safe_area": True`, in which case the panel
is handed the full viewport and lays itself out (the `--safe-area-inset-*` variables the
post mentions are forwarded to iframe panels only); say which in the registration, so
the choice is visible rather than a default nobody chose.
```

**Before writing either**, confirm the spelling against the frontend source rather than
against this plan: `handle_safe_area` is read by the panel element, and whether it is a
key inside `config` or a keyword of `async_register_panel` decides both edits.
`.tmp/plan/step0-findings.md` records the `config` form and this step follows it; if the
source says otherwise, both blocks change together and the disagreement is a friction
line against the findings file.

- [ ] **Step 2: Add, after *Testability is a design property, not a tooling one*, before the closing note:**

```
### A panel that reads devices reads them by config entry

The device-registry WebSocket API changed with HA 2026.8 and 2026.9: every device now
carries `config_entry_id` and `config_subentry_id`, the old `config_entries`,
`config_entries_subentries` and `primary_config_entry` are deprecated, and
`config/device_registry/remove_config_entry` is `config/device_registry/remove` (the old
command warns). A panel built against the old shape keeps working until the removals in
the 2026-08-19 row of *What changed in recent releases* in `reference/patterns.md`, and
then stops.
```

- [ ] **Step 3: The counts.** Line 11 `Five things are non-obvious here, and each fails
silently.` becomes `Six things are non-obvious here, and each fails silently.`; in
*Register the static path and the panel in `async_setup`* the clause `the snippet
carries both traps the section below names` becomes `the snippet carries all three
traps the section below names`; under *Registration has three traps* the opening `Both
are in the snippet above, marked by their comments:` becomes `All three are in the
snippet above, marked by their comments:`; in the contents list `- Registration has two
traps` becomes `- Registration has three traps` (this repository's `skill_meta_audit.py`
fails an index that disagrees with the headings, and `ci.yml` runs it), and add
`- A panel that reads devices reads them by config entry` after
`- Testability is a design property, not a tooling one`.

- [ ] **Step 4: Re-read. Commit:** `docs: say what 2026.8 changed for a panel`.

---

### Task 3: `freshness.md` — the release row and the procedure

**Files:**
- Modify: `plugins/ha/skills/ha-integration/reference/freshness.md` — the table and a new paragraph beneath it

**Interfaces:**
- Produces: the row whose first cell is exactly `HA release the skill is current for` and whose value cell is a backticked minor `` `2026.9` ``; Task 6's script parses this row by that first cell.

- [ ] **Step 1: Add the row** as the first row of the table:

```
| HA release the skill is current for | `2026.9` | 2026-09-15 | `curl -s https://pypi.org/pypi/homeassistant/json \| jq -r .info.version`; then the developer blog posts for that release and the release notes' developer section | *What changed in recent releases* in `reference/patterns.md` · the safe-area sentence in `reference/panels.md` · the panel-design row below, whose re-derive names the frontend-component posts · the skill repository's own CI, which reads this cell and fails when PyPI's minor is ahead of it |
```

- [ ] **Step 2: Fix the quality-scale row's re-derive cell**: replace
`developers.home-assistant.io/docs/core/integration-quality-scale/ — or, as data,` with
`developers.home-assistant.io/docs/core/integration-quality-scale/checklist (the index page lists tiers only) — or, as data,`.

- [ ] **Step 3: Extend the harness row's consumer cell** with:

````
 · a panel repo's home-assistant-frontend pin, per *`home-assistant-frontend` must be pinned in `requirements.test.txt`* in `reference/panels.md`
````

- [ ] **Step 4: Extend the panel-design row's re-derive cell** with:
`· the developer blog's *Frontend component updates* post for each release, which names the components and tokens that moved`.

- [ ] **Step 5: Re-derive every other row with its own command, and move each *Captured*
date to today where the value held.** Python floor: the development-environment page
(3.14.2+ on 2026-09-15; unchanged). Quality-scale rules: the checklist page (54;
unchanged). Action versions: for each of `actions/checkout`, `actions/dependency-review-action`,
`actions/stale`, `gh api repos/<o>/<r>/releases/latest --jq .tag_name` then
`gh api repos/<o>/<r>/git/ref/tags/<tag>` — on 2026-09-15 they were `v7.0.1`/`3d3c42e`,
`v5.0.0`/`a1d282b`, `v11.0.0`/`4391f3d`, equal to the template pins, so no template
pin moves; say so in the row's *Captured* cell. Harness: PyPI (`0.13.365` → `2026.9.2`;
unchanged). Brand assets: `gh api repos/hacs/integration/issues/5171 --jq .state` and
the same for `5223`; if either has closed with the dashboard reading the proxy, the
row's value and the *Brand assets are served from the integration's own `brand/`
folder* note in `reference/scaffold.md` change together, otherwise only the *Captured*
date moves. Panel-design sources: `gh api repos/home-assistant/frontend/contents/src/resources/theme --jq '.[].name'`
(unchanged on 2026-09-12). Write the result of each into the row.

- [ ] **Step 6: Add the procedure paragraph** after the table, before the `version_sync.py`
paragraph:

```
**When the release row goes red.** The skill repository's own CI fails once PyPI's
`homeassistant` minor is ahead of the row above. The pass that
clears it: read that release's posts on the developer blog and the developer section of
its release notes; for each change a custom integration can meet, add a row to *What
changed in recent releases* in `reference/patterns.md` and apply it in the section that
owns the topic; re-derive every other row here; move the release cell; one PR. The first
such pass was 2026.6 to 2026.9, done in one go on 2026-09-15.
```

- [ ] **Step 7: Re-read the whole file. Commit:** `docs: add the release row to the freshness table`.

---

### Task 4: `quality-scale.md` and `scaffold.md` — two lines

**Files:**
- Modify: `plugins/ha/skills/ha-integration/reference/quality-scale.md` — the bold run-in paragraph beginning `Canonical rule set — a snapshot` under *Prove the rule, don't just claim it — hassfest checks structure, not behaviour*
- Modify: `plugins/ha/skills/ha-integration/reference/scaffold.md` — the manifest example

- [ ] **Step 1: quality-scale.md** — in "Each rule is documented at
`developers.home-assistant.io/docs/core/integration-quality-scale/rules/<rule-name>/`",
append: `, and the checklist page beside it is the one list, which is what the
freshness row re-derives from`.

- [ ] **Step 2: scaffold.md** — in the manifest example, after `"requirements": [],`
insert `"single_config_entry": true,` and after the code block add the sentence:
`` `single_config_entry` is right for a cloud account or a single hub; omit it when a user may add several devices, and then implement the `unique-config-entry` rule with a unique id instead. ``

- [ ] **Step 3: Commit each:** `docs: name the quality-scale checklist page`,
`docs: show single_config_entry in the manifest example`.

---

### Task 5: `SKILL.md` — the procedure

**Files:**
- Modify: `plugins/ha/skills/ha-integration/SKILL.md` — *Invariants — true in every mode*

- [ ] **Step 1:** Leave *Always fetch before coding* as it is. This overrides finding 18
in `.tmp/plan/step0-findings.md`, which proposed adding the developer blog to that
invariant: the blog is read by the monthly procedure, not by every coding session, since
the procedure's job is to have incorporated it already. The override is deliberate and is
recorded here so the findings file is not silently contradicted.

- [ ] **Step 2:** Replace the *Cached facts go stale silently* invariant's text with:

````
**Cached facts go stale silently.** Anything captured more than ~3 months ago gets re-derived before it is trusted, and the skill is current for one HA release at a time — the table, its re-derivation commands and the monthly procedure are in `reference/freshness.md`.
````

- [ ] **Step 3: Commit:** `docs: name the monthly procedure in the invariant`.

---

### Task 6: `scripts/check_ha_release.py` with its test

**Files:**
- Create: `scripts/check_ha_release.py`
- Create: `tests/test_check_ha_release.py`
- Modify: `.github/workflows/ci.yml` — one step after *Skill authoring audit*
- Modify: `README.md` (not governed; edit directly) — the sentence under *Development* that reads `its own tooling has unit tests that run on every PR`

**Interfaces:**
- Consumes: the `freshness.md` row from Task 3, first cell `HA release the skill is current for`.
- Produces: `captured_minor(text: str) -> tuple[int, int]`, `latest_minor(fetch: Callable[[str], str]) -> tuple[int, int]`, `main(argv: list[str] | None = None, fetch: Callable[[str], str] = _fetch) -> int` returning 0 when captured ≥ latest, 1 when behind, 2 when the row or PyPI cannot be read; the tests pass a fake `fetch`.

- [ ] **Step 1: Write the failing test** (through the gate, `tests/` tier) (`tests/test_check_ha_release.py`):

```python
"""Unit tests for scripts/check_ha_release.py, the nudge that goes red on a new HA minor."""

import importlib.util
import json
import pathlib

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "check_ha_release",
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "check_ha_release.py",
)
chr_ = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(chr_)

ROW = "| HA release the skill is current for | `2026.9` | 2026-09-15 | x | y |\n"
TABLE = "| a | b |\n|---|---|\n" + ROW + "| other | `1.0` | z | x | y |\n"


def test_captured_minor_reads_the_row() -> None:
    """The backticked value of the named row, as (year, month)."""
    assert chr_.captured_minor(TABLE) == (2026, 9)


def test_captured_minor_ignores_other_rows() -> None:
    """A different row's backticked value is not the answer."""
    assert chr_.captured_minor("| other | `2030.1` | z |\n" + ROW) == (2026, 9)


def test_captured_minor_missing_row_raises() -> None:
    """No row means the table was edited out from under the check."""
    with pytest.raises(ValueError, match="no row"):
        chr_.captured_minor("| other | `1.0` |\n")


@pytest.mark.parametrize(
    ("version", "expected"),
    [("2026.9.2", (2026, 9)), ("2026.10.0", (2026, 10)), ("2027.1.0b3", (2027, 1))],
)
def test_latest_minor_from_pypi(version: str, expected: tuple[int, int]) -> None:
    """PyPI's info.version, truncated to its minor."""
    body = json.dumps({"info": {"version": version}})
    assert chr_.latest_minor(lambda _url: body) == expected


def test_main_passes_when_current(tmp_path: pathlib.Path, capsys) -> None:
    """Captured minor equal to PyPI's is green."""
    f = tmp_path / "freshness.md"
    f.write_text(TABLE)
    body = json.dumps({"info": {"version": "2026.9.2"}})
    assert chr_.main(["--file", str(f)], fetch=lambda _u: body) == 0
    assert "2026.9" in capsys.readouterr().out


def test_main_fails_when_behind(tmp_path: pathlib.Path, capsys) -> None:
    """A newer minor on PyPI is the red the procedure clears."""
    f = tmp_path / "freshness.md"
    f.write_text(TABLE)
    body = json.dumps({"info": {"version": "2026.10.0"}})
    assert chr_.main(["--file", str(f)], fetch=lambda _u: body) == 1
    assert "2026.10" in capsys.readouterr().err


def test_main_reports_an_unreadable_source(tmp_path: pathlib.Path) -> None:
    """A missing row or a PyPI failure is 2, not a quiet pass."""
    f = tmp_path / "freshness.md"
    f.write_text("| nothing |\n")
    assert chr_.main(["--file", str(f)], fetch=lambda _u: "{}") == 2

    def boom(_url: str) -> str:
        raise OSError("offline")

    f.write_text(TABLE)
    assert chr_.main(["--file", str(f)], fetch=boom) == 2
```

- [ ] **Step 2: Run it, expect failure**

```bash
cd /home/juicebox/claude-skills && UV_CACHE_DIR=.tmp/uv-cache uv run -q --no-project --with pytest --python 3.14 python -m pytest tests/test_check_ha_release.py -q
```

Expected: collection error, `No such file … scripts/check_ha_release.py`.

- [ ] **Step 3: Write the script** (through the gate, `scripts/` tier, empty `old_string`):

```python
#!/usr/bin/env python3
"""Fail when Home Assistant has a newer minor than the skill says it is current for.

The row is the first cell of `reference/freshness.md`'s table that reads
`HA release the skill is current for`; PyPI's `homeassistant` is the release. Red here
is the signal for the monthly procedure that table describes; nothing is updated by this
script.
"""

import argparse
from collections.abc import Callable
import json
from pathlib import Path
import re
import sys
import urllib.request

ROW_NAME = "HA release the skill is current for"
PYPI = "https://pypi.org/pypi/homeassistant/json"
DEFAULT_FILE = (
    Path(__file__).resolve().parents[1]
    / "plugins/ha/skills/ha-integration/reference/freshness.md"
)
_MINOR = re.compile(r"^(\d{4})\.(\d{1,2})")


def _minor(version: str) -> tuple[int, int]:
    """The (year, month) minor of an HA version string; raises on any other shape."""
    m = _MINOR.match(version.strip())
    if not m:
        raise ValueError(f"not an HA version: {version!r}")
    return int(m[1]), int(m[2])


def captured_minor(text: str) -> tuple[int, int]:
    """The minor in the named row's value cell, which is a backticked `YYYY.M`."""
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == ROW_NAME:
            if len(cells) < 2:
                raise ValueError(f"no value cell in the {ROW_NAME!r} row")
            return _minor(cells[1].strip("`"))
    raise ValueError(f"no row named {ROW_NAME!r}")


def _fetch(url: str) -> str:
    """The body at url; kept separate so tests pass a fake."""
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode()


def latest_minor(fetch: Callable[[str], str] = _fetch) -> tuple[int, int]:
    """PyPI's current homeassistant version, as a minor."""
    return _minor(json.loads(fetch(PYPI))["info"]["version"])


def main(argv: list[str] | None = None, fetch: Callable[[str], str] = _fetch) -> int:
    """0 when the skill is current, 1 when behind, 2 when either side cannot be read."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", type=Path, default=DEFAULT_FILE)
    args = ap.parse_args(argv)
    try:
        captured = captured_minor(args.file.read_text(encoding="utf-8"))
        latest = latest_minor(fetch)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as err:
        print(f"check_ha_release: cannot decide: {err}", file=sys.stderr)
        return 2
    cap, lat = f"{captured[0]}.{captured[1]}", f"{latest[0]}.{latest[1]}"
    if captured >= latest:
        print(f"skill is current for HA {cap}; PyPI has {lat}")
        return 0
    print(
        f"skill is current for HA {cap} but PyPI has {lat}: run the procedure under "
        "the table in reference/freshness.md",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test, expect pass; run ruff**

```bash
cd /home/juicebox/claude-skills && UV_CACHE_DIR=.tmp/uv-cache uv run -q --no-project --with pytest --with ruff --python 3.14 sh -c 'python -m pytest tests/test_check_ha_release.py -q && ruff check scripts/check_ha_release.py tests/test_check_ha_release.py && ruff format --check scripts/check_ha_release.py tests/test_check_ha_release.py'
```

Expected: `9 passed`, ruff clean. The import block above is already in the order
`force-sort-within-sections = true` in `pyproject.toml` wants (modules and `from`
imports sorted together by module name); if ruff still reports `I001`, apply
`ruff check --fix` on the script and re-read it.

- [ ] **Step 5: Run it for real against the Task 3 row**

```bash
cd /home/juicebox/claude-skills && python3 scripts/check_ha_release.py; echo "exit $?"
```

Expected: `skill is current for HA 2026.9; PyPI has 2026.9`, `exit 0`.

- [ ] **Step 6: Add the CI step** (gate, `.github/workflows/` tier), after
*Skill authoring audit*:

```yaml
      - name: The skill is current for the latest HA minor
        run: python3 scripts/check_ha_release.py
```

- [ ] **Step 7: README** — read `README.md` in full (not governed; edit directly). Under
*Development*, replace this sentence:

````
The skills are treated as code: this repo is a consumer of release-flow like any
integration, and its own tooling has unit tests that run on every PR.
````

with this one, keeping the file's ~80-column wrap:

````
The skills are treated as code: this repo is a consumer of release-flow like any
integration, its own tooling has unit tests that run on every PR, and that run fails
once PyPI carries a newer Home Assistant minor than the release row in the skill's
`reference/freshness.md` names — the nudge for the monthly procedure written under
that table.
````

- [ ] **Step 8: Commit, three:** `feat: fail ci when a newer ha minor is out`
(script + test), `ci: run the release check` (workflow), `docs: name the release check in
the readme`.

---

### Task 7: `scaffold.md` — deliberate alignment is fenced, not surrendered

**Files:**
- Modify: `plugins/ha/skills/ha-integration/reference/scaffold.md` — *Code style*

**Interfaces:**
- Consumes: decisions 22–28 (Step 1, the fence rule) and 33 (Step 2, what an exclusion
  hides), and the evidence from settleup-ha `95ed0db` and ha-pimoroni-unicorn `7e29ce6`.
- Decision 32, which would have added a `[tool.ruff.format] exclude` for verbatim template
  copies, is withdrawn: `templates/` ships one Python file, `conftest.py`, and it is
  already format-clean, so the exclusion has nothing to cover once a migration deletes the
  copied scripts. No adaptation-table row and no `ha-integration-ci` README change follow
  from this task.

- [ ] **Step 1: Add to *Code style*, after the inline-comments bullet** (the block below
is delimited with four backticks because the text itself contains a three-backtick
fence; paste its contents, not the delimiters):

````
- **Alignment a human chose is kept, not collapsed.** `ruff format` reduces every run of
  spaces to one, which destroys a table someone aligned so that it could be read as a
  table. Fence those with `# fmt: off` / `# fmt: on` rather than surrendering them or
  turning the formatter off:

  ```python
  # fmt: off
  CONF_EMAIL         = "email"
  CONF_API_KEY       = "api_key"
  CONF_REFRESH_TOKEN = "refresh_token"
  # fmt: on
  ```

  **The fence is statement-level.** One inside a dict or call literal does nothing — ruff
  ignores it and collapses the entries anyway; it must wrap the whole enclosing statement,
  at that statement's indent. So an aligned keyword-argument call is fenced around the
  whole call, and a `# fmt: on` may not sit at a different indent from its `# fmt: off`.

  What earns a fence, from applying this to two repositories: padding before `=` or `:`;
  padding after them, where the values form the column; padding after `,`; and **one row
  or record per source line even where nothing is padded** — glyph rasters, icon bitmaps,
  colour palettes, layout tables, field-descriptor lists. That last case is the one that
  bites: `ruff format` turned a 13-line font bitmask table into 1,194 lines, one pixel per
  line, and the digit shape a reader could see in the source was gone. A flat wrapped list
  of strings is not a table and is left to the formatter.

  **A generator that emits a fenced table emits the fence too**, or the next regeneration
  drops it.
````

- [ ] **Step 2: Add to *Code style*, after the bullet Step 1 wrote** (decision 33):

```
- **An exclusion hides drift until the day it is removed.** The stack lints and formats the
  whole tree — the `python-validate.yml` bullet under *Implementation notes* in
  `ha-integration-ci`'s README says why —
  and the template `pyproject.toml` excludes nothing, so whatever a repository has been
  keeping out of ruff's sight becomes visible the moment it adopts that file. The three
  repositories migrated in 2026-09 showed all three shapes of this. Two whose CI checked
  `custom_components/` alone arrived with `ruff format --check` reporting 21 and 112 files.
  One of those also kept three generated trees out of ruff entirely, so its formatting
  commit touched 210 files where `--check` had reported 112. The third looked clean only
  because eight files sat under `[tool.ruff.format] exclude`. Before a migration, drop the
  exclusions and format what they were hiding, as its own commit: a migration diff is no
  place to meet a hundred files for the first time.
```

- [ ] **Step 3: Re-read the file; commit:** `docs: say how deliberate alignment survives
the formatter`. One commit for both steps: they are one topic, code style where the
formatter is involved.

---

### Task 8: `testing.md` — the tests that deliberately do not mock

**Files:**
- Modify: `plugins/ha/skills/ha-integration/reference/testing.md` — a new section after *Unit-test the pure logic directly*, and its entry in the contents list

**Interfaces:**
- Consumes: decision 29 and ha-lego's `live_api_tests.yml`, which is the worked example.

- [ ] **Step 1: Add the section:**

```
### Contract tests against the real API

Everything above says mock the boundary. The exception is a test whose whole purpose is to
check what the vendor actually returns, because a fixture only ever confirms what you
already believed — it cannot catch a payload changing shape. Keep a handful, and make them
safe:

- **Manual only.** `workflow_dispatch`, never `pull_request`, and never
  `pull_request_target`: a fork PR gets no secrets by design, and running PR-authored code
  with a live key in reach is how the key leaves.
- **Behind an environment with required reviewers**, so the run pauses for a human and the
  key stays unreadable to every other workflow in the repository.
- **Marked and excluded from the default run** — `pytest.mark.live` with
  `addopts = "-m 'not live'"` in the pytest table, so a normal suite never spends a call.
- **A dedicated account**, never a personal one, and nothing in the repository naming it.
- **Say what a failure means.** The common one is a credential that expired rather than a
  payload that moved; a job that prints which it is saves the next reader an hour.
- **Count the calls.** A billed API makes the test's cost part of its design.
```

- [ ] **Step 2: Add `- Contract tests against the real API` to the contents list after
`- Unit-test the pure logic directly`. Re-read the file; commit:**
`docs: say how to test against a real api safely`.

---

### Task 9: Register, review, hand over

**Files:**
- Modify: `docs/backlog.md` — one new section, rows for: (a) the 2026.6–2026.9 guidance gap as one row with the findings file's list as evidence (row 215), (b) the alignment-fence standard and the live-contract-test gap, both found by using the skill on real repositories rather than reading it, with `.tmp/plan/decisions.md` items 22–30 and 33 as evidence, written by Tasks 7 and 8 (row 216), (c) row 177's table gaining a mechanical nudge, closing the "table nothing runs" half of 177, with the script and CI step as evidence (row 217); the header's live-rows line

- [ ] **Step 1: Rows.** A new section `### From the 2026.9 refresh (<date>)` with an
intro line `The first run of the monthly procedure, four releases at once; the findings
file it worked from is not in the repository.` and three rows, hashes filled from the
commits above:

```
| 215 | **The skill's guidance stopped at HA 2026.5 while 2026.6 to 2026.9 changed the device registry, the config-flow reload rules, the unit constants and a panel's default padding.** `patterns.md` still resolved a service's device with `device_registry.async_get(hass).async_get(id)` and showed no `via_device_id`; nothing named the 2026.6 listener-plus-reload deprecation (an error from 2026.12) or the 2026.7 `UnitOfDensity`/`UnitOfRatio` enums; `panels.md` did not know HA pads a custom panel since 2026.8. Found by reading every developer-blog post from 2026-05-01 against every reference file | Applied per section in `patterns.md` and `panels.md`, indexed by the new *What changed in recent releases* table with each change's removal release; `freshness.md` gains the row that says which release the skill is current for | `<patterns hash>`, `<panels hash>`, `<freshness hash>` |
| 216 | **Two standards the skill needed were found by using it on real repositories, not by reading it.** `scaffold.md` said nothing about keeping deliberate alignment through `ruff format` — a formatter run turned a 13-line font bitmask table into 1,194 lines before anyone noticed — nor that ruff's `# fmt: off` is statement-level, so a fence inside a dict literal is silently ignored; `testing.md` said nothing about a test that deliberately does not mock its boundary, though ha-lego has carried a `workflow_dispatch` job against the real Brickset API, behind an environment with required reviewers, since its CI was written — and has never once run it, which is its own argument for writing the shape down | `scaffold.md` gains the fence rule with its four shapes and the statement-level trap, and the rule that an exclusion only hides drift until a migration adopts the template `pyproject.toml` and reveals it; `testing.md` gains *Contract tests against the real API* with the four conditions that make one safe (manual dispatch, an environment with required reviewers, a marker outside the default run, a dedicated account) | `<scaffold hash>`, `<testing hash>` |
| 217 | **Row 177's table was a rule nothing ran: no check noticed when a Home Assistant release landed.** The freshness table said re-derive rows older than ~3 months, and nothing measured it | `scripts/check_ha_release.py`, run by `ci.yml`, fails once PyPI's `homeassistant` minor is ahead of the release row; the procedure that clears it is written under the table. Closes the enforcement half of row 177; the row's own text stands | `<script hash>`, `<ci hash>` |
```

The header's live-rows line drops 177 and adds nothing: 215, 216 and 217 all close in
this PR. Commit: `docs: record the 2026.9 refresh`.

- [ ] **Step 2: Reviewer** on the branch (`git diff origin/main..HEAD`), brief
`docs/review.md`, kind diff review. Fix; repeat until a pass returns nothing.

- [ ] **Step 3: Hand over the push** (touches `ci.yml`):

```bash
git -C /home/juicebox/claude-skills push git@github.com:PineappleEmperor/ha-skills.git feat/refresh-2026-9
```

- [ ] **Step 4: After merge**, the `ci.yml` run on `main` shows the new step green with
`skill is current for HA 2026.9`. Record the run id in the register row.
