# Testing an integration

Read this when writing or fixing an integration's tests.

**Each prerequisite below fails the *whole* suite rather than one test.**

## Contents

1. Testing — prerequisites before any of the rules below apply
2. Step 1: Copy `templates/tests/`
3. Step 2: Set `asyncio_mode = "auto"` in `pyproject.toml`
4. Step 3: Ship a `config_flow.py` that imports
5. Step 4: Keep the harness pin and the Python floor in lockstep
6. Testing — mock at the boundary, not your own code
7. Step 1: Mock only at the external boundary
8. Step 2: Make `test-before-setup` a real config-entry setup
9. Step 3: Unit-test the pure logic directly
10. Step 4: Minimum coverage before claiming a tier
11. Cases
12. The domain already exists in HA core — prerequisites Step 1
13. Moving from `pytest-homeassistant-custom-component` — prerequisites Step 4
14. The integration allows multiple devices — mocking Step 2
15. A question a mock cannot answer — mocking Step 1
16. A fixture payload whose dates must be upcoming — mocking Step 2
17. Entities still read defaults after `async_block_till_done` — mocking Step 2
18. Ruff flags a file under `tests/` or `scripts/` — mocking Step 4

## Testing — prerequisites before any of the rules below apply

The harness is core's `pytest-homeassistant`, and it does not work out of the box.

> **Note:** re-derive against the harness row of `reference/freshness.md` if these stop
> matching what you see.

### Step 1: Copy `templates/tests/`

| Rule | Value |
|---|---|
| `tests/__init__.py` | required: `validate / Python validation` fails a `tests/` without one, and a directory on the path to a test file without one — the `python-validate.yml` row of *The three workflows* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| `tests/conftest.py` | `import custom_components`, and no fixture that requests `enable_custom_integrations`: the `hass` fixture enables custom integrations itself — `custom_integrations_enabled` and `hass` in core's `packages/pytest-homeassistant/pytest_homeassistant/plugins.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `recorder_mock` | requested ahead of `hass` in the same signature: `recorder_db_url`, which it depends on, asserts that `hass` is not set up yet — `recorder_db_url` in the same file |

### Step 2: Set `asyncio_mode = "auto"` in `pyproject.toml`

The shipped `templates/pyproject.toml` carries the pytest table alongside the ruff rules;
copy the file rather than the block.

| Rule | Value |
|---|---|
| where each row was read | *Writing tests* in core's `packages/pytest-homeassistant/README.md`, `pytest_homeassistant/__init__.py` and `bootstrap.py` beside it, and `httpx2.alias_httpx()` in core's `homeassistant/__init__.py`, at the `.0` tag of the release row in `reference/freshness.md`; `respx_mock` in respx's `respx/plugin.py`, and its `pytest11` entry point, at the version core's harness pins; that CI requires `-p no:respx`, *What the audit checks now* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| `asyncio_mode = "auto"` | without it pytest-asyncio never runs the async tests — they error at collection |
| `addopts = "-p no:respx"` | required from HA 2026.11.0: importing `homeassistant` aliases `httpx` to `httpx2`, which must come before any `import httpx`; core's plugin imports `homeassistant` through its package `__init__.py` as pytest loads the `pytest_homeassistant.bootstrap` entry point, and respx's pytest plugin imports `httpx`; which of the two loads first follows entry-point discovery and site-packages order, so it differs between machines |
| respx in a test | `import respx` and `respx.mock` still work; only respx's pytest plugin is off, and its `respx_mock` fixture with it |
| a second pytest option | in the same string, `addopts = "-p no:respx -m 'not live'"`, never a second `addopts` key |
| `pythonpath = ["."]` | kept as core's README lists it; with `tests/__init__.py` present, pytest already puts the repository root on `sys.path` |

**Symptom:** without `-p no:respx` the whole run stops at startup with a `RuntimeError`
beginning `httpx was already imported` on one machine and runs on another, which reads as
a broken environment rather than a missing option.

### Step 3: Ship a `config_flow.py` that imports

Whenever `manifest.json` sets `"config_flow": true`. HA imports the flow module *during
entry setup*, not only when a user opens the flow.

**Symptom:** the setup test fails with `Error importing platform config_flow from
integration <domain>` — which reads as a test problem and is a wiring problem.

### Step 4: Keep the harness pin and the Python floor in lockstep

`requirements.test.txt` pins core's `pytest-homeassistant`, and its version is the
Home Assistant release it hard-pins — `pytest-homeassistant==<version>` brings
`homeassistant==<version>` — so **that pin decides which HA the suite runs against**. Keep
it in lockstep with the Python floor the CI declares.

| Rule | Value |
|---|---|
| where each row was read | *Installation and compatibility* in core's `packages/pytest-homeassistant/README.md`, at the `.0` tag of the release row in `reference/freshness.md`; what CI accepts, *What the audit checks now* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| the pin | `==` one release, never a range or a bare name: PyPI also carries an unrelated `pytest-homeassistant` 0.1.x from 2020 by another author, which those can resolve to, and CI fails them |
| `pytest-homeassistant-custom-component` | never in the same environment as core's harness: each pins a different exact `homeassistant`, and core's README says not to install the two together |
| a repository still on ha-integration-ci v4 that must test HA 2026.10 or older | keeps `pytest-homeassistant-custom-component` for that run, in an environment of its own; core publishes its harness from 2026.11.0; on v5 the repository claims nothing below the compatibility floor of the return row of *Step 3: Wire the entry setup and unload* in `reference/patterns.md` |

**Timing:** by hand, since nothing compares the pair — the gate cell of the harness row in
`reference/freshness.md` says so.

**Symptom:** a mismatch fails at import, not at test time.

## Testing — mock at the boundary, not your own code

**A test that patches the integration's own functions passes while the integration is
broken.**

### Step 1: Mock only at the external boundary

Mock the third-party client, socket, or library (`imaplib.IMAP4_SSL`, `aiohttp` via
`aioclient_mock`, the vendored device lib, `serial`) and nothing inside the integration.

- **Never patch your own `_async_update_data`, `email_triage`, `api.fetch`, etc.**
- The integration's *own* wiring then runs: reading `entry.data`/`entry.options` into
  attributes, building requests, parsing responses, populating the coordinator.
- Pass config as explicit constructor args, so mypy catches a missing field instead of a
  helper reaching into `self.<attr>` set elsewhere.
- Patch an object where the integration looks it up, not where it is defined —
  `custom_components.my_device.coordinator.MyClient` for the client `coordinator.py`
  imports, never `my_lib.MyClient` — `.claude/skills/ha-integration-knowledge/SKILL.md` in
  core, at the `.0` tag of the release row in `reference/freshness.md`.

### Step 2: Make `test-before-setup` a real config-entry setup

Add a `MockConfigEntry`, call `hass.config_entries.async_setup(entry.entry_id)`, and assert
`entry.state is ConfigEntryState.LOADED` plus that entities exist — with only the transport
mocked.

- It exercises `async_setup_entry` end to end: credential reads,
  `async_config_entry_first_refresh`, `runtime_data`, platform forward, entity creation.
- A `async_setup_component(hass, DOMAIN, {})` test only proves the (unused) YAML path
  returns `True`.
- **If you scaffold an `init_integration` fixture, actually use it** — an unused setup
  fixture is a tell that the highest-value test was skipped.

**The fixtures the tests share, and what a test asserts:**

| Rule | Value |
|---|---|
| where each row was read | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, and `get_fixture_path` and `load_json_object_fixture` in core's `packages/pytest-homeassistant/pytest_homeassistant/common.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| shared mocks | fixtures in `tests/conftest.py`, so every platform test reuses them — a `mock_config_entry` among them, with a `unique_id` when the integration's config entries have one |
| mock API data that is substantial or reused | a JSON file in `tests/fixtures/`, loaded with `load_json_object_fixture` or `load_json_array_fixture` from `pytest_homeassistant.common`, or their `async_` variants, never built inline with `json.dumps()` |
| different mock data for one test | `pytest.mark.parametrize` on the fixture that provides it, with `indirect=True` when the fixture reads `request.param`, never a second patch inside the test |
| a value a snapshot test already covers | no assertion of its own beside the snapshot |
| a value that has a `Platform` member or an `ATTR_*` constant | the constant, `Platform.SENSOR` or `ATTR_TEMPERATURE`, never the string |

The first two fixtures go in `tests/conftest.py`:

```python
@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the config entry the tests set up."""
    return MockConfigEntry(
        domain=DOMAIN, unique_id="aa:bb:cc:dd:ee:ff", data={CONF_HOST: "192.0.2.10"}
    )


@pytest.fixture
def mock_client(request: pytest.FixtureRequest) -> Generator[AsyncMock]:
    """Patch the client where the coordinator uses it, replying from a fixture file."""
    reply = load_json_object_fixture(getattr(request, "param", "device.json"))
    with patch(
        "custom_components.my_device.coordinator.MyClient", autospec=True
    ) as client_class:
        client_class.return_value.async_get_data.return_value = reply
        yield client_class.return_value


@pytest.mark.parametrize("mock_client", ["device_low_battery.json"], indirect=True)
@pytest.mark.usefixtures("mock_client")
async def test_low_battery(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Turn the battery sensor on when the reply reports a low battery."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert hass.states.get("binary_sensor.my_device_battery").state == STATE_ON
```

### Step 3: Unit-test the pure logic directly

Regex parsers, date/format extraction and data transforms (`order_parse`, `voucher_parse`,
`sort_orders`, …) take a string or object and return a value, with no HA and no mocks.

### Step 4: Minimum coverage before claiming a tier

| Rule | Value |
|---|---|
| the config flow | the happy path, each error, and reauth or reconfigure where either exists |
| entry setup | a real `LOADED` test, plus a two-entry parallel one where several devices are allowed |
| the coordinator | success, auth failure, and the credential-read path, against a mocked transport |
| the coordinator's next poll, in a test | `freezer.tick(SCAN_INTERVAL)`, `async_fire_time_changed(hass)`, then `await hass.async_block_till_done(wait_background_tasks=True)`, never a call to `async_refresh()`, `async_request_refresh()` or `_async_refresh()`, so the coordinator's own schedule runs; ha-integration-ci v5 fails the call (W7439) — `checkers/tests/coordinator_async_refresh.py` in core's `packages/pylint-home-assistant/pylint_home_assistant/`, at the `.0` tag of the release row in `reference/freshness.md`, and *v5.0.0's edits* under *The version model* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| unload | a test of its own |
| each parser | a unit test of its own |

**A config-flow test, as ha-integration-ci v5 lints it:**

| Rule | Value |
|---|---|
| where each row was read | `checkers/tests/config_flow_unique_id.py`, `checkers/tests/config_flow_error_recovery.py`, `checkers/tests/user_flow_no_data.py` and `checkers/flow_start_helpers.py` in core's `packages/pylint-home-assistant/pylint_home_assistant/`, at the `.0` tag of the release row in `reference/freshness.md`; that CI runs them on `tests/`, *v5.0.0's edits* under *The version model* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| a test in `tests/test_config_flow.py` that asserts `CREATE_ENTRY`, where `config_flow.py` calls `async_set_unique_id` | also asserts the entry's unique ID, `assert result["result"].unique_id == "aa:bb:cc:dd:ee:ff"`, or matches a `snapshot` (W7440); a test that injects an error, or starts an options or subentry flow, is exempt |
| a test in `tests/test_config_flow.py` that asserts an error, `assert result["errors"] == {"base": "cannot_connect"}` say | then clears the cause, submits the same flow again and asserts `CREATE_ENTRY`, or an abort whose reason ends `_successful` for reauth and reconfigure (W7441); each error needs its own finish after it, and a finish after a new `async_init` does not count |
| starting the user step | `hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})` with no `data=`, then `async_configure` with the input (R7405): only a discovery flow starts with data |
| starting a reauth or reconfigure flow | `await mock_config_entry.start_reauth_flow(hass)` or `await mock_config_entry.start_reconfigure_flow(hass)`, never `flow.async_init` with that source (W7445): the helpers build the context Home Assistant builds |

**Timing:** wire the regression test *first* on any bug fix — confirm it fails on the
unpatched code, then fix.

Which rules demand a behavioural test before you may mark them `done`, and what each test
must prove, is *Step 3: Prove every `done`* in `reference/quality-scale.md`.

## Cases

### The domain already exists in HA core — prerequisites Step 1

A custom `demo`, `sun`, `light`… is shadowed by the built-in.

**Symptom:** core's dependencies fail to import (`No module named 'hassil'` for `demo`),
which looks nothing like a naming clash.

**Fix:** check `homeassistant/components/` before fixing the domain.

**Timing:** the domain cannot change later.

### Moving from `pytest-homeassistant-custom-component` — prerequisites Step 4

| Rule | Value |
|---|---|
| where each row was read | *Migrating from pytest-homeassistant-custom-component* in core's `packages/pytest-homeassistant/README.md`, and `_serializable_device_id` and `_serializable_subentry_id` in `pytest_homeassistant/syrupy.py` beside it, at the `.0` tag of the release row in `reference/freshness.md` |
| `requirements.test.txt` | `pytest-homeassistant-custom-component==…` → `pytest-homeassistant==<the HA release under test>`, as Step 4 pins it |
| imports | `pytest_homeassistant_custom_component.common` → `pytest_homeassistant.common`, and so for every module of the package; `hass`, `enable_custom_integrations` and the registry, HTTP, recorder and snapshot fixtures keep their names |
| `tests/conftest.py` | the template's, Step 1: the fixture that requests `enable_custom_integrations` goes, with the `import pytest` only it used |
| `pyproject.toml` | the template's pytest table, Step 2 |
| an `.ambr` snapshot holding a device id — an entity's `device_id`, a device's `via_device_id` or `parent_device_id` — or a `config_subentry_id` | regenerate it with `pytest --snapshot-update`, and read the diff before committing it: core's harness writes each as a reference to the device, by its identifiers, or to the subentry, by its type and title, where the community package wrote `ANY` |

### The integration allows multiple devices — mocking Step 2

Add a test that `add_to_hass`es two `MockConfigEntry`s, calls
`await hass.config_entries.async_setup(e1.entry_id)` once, and asserts **both**
`state is ConfigEntryState.LOADED`: setting up the domain sets up all its entries at once
(`_async_setup_component` in `homeassistant/setup.py`), and a second call races that.

**Timing:** a single-entry `LOADED` test cannot catch integration-global registration done
per-entry — static paths, websocket commands, the panel.

**Symptom:** on the buggy per-entry code the second entry goes `SETUP_ERROR` with aiohttp
`RuntimeError: Added route ... already registered`; it passes once the registration moves to
`async_setup`.

**Fix:** unload both entries at the end, and if a fixture starts a self-rescheduling timer
(e.g. `mqtt_mock`'s periodic loop) override the `expected_lingering_timers` fixture to
`True` **in that module only**.

### A question a mock cannot answer — mocking Step 1

A **contract test** calls the vendor's real API: has the response shape changed, is the key
still valid, does the rate limit behave as documented. Four conditions make one safe, and
all four are needed:

- **Manual dispatch only.** `on: workflow_dispatch` — never `pull_request`, and never
  `pull_request_target`, which would hand a fork's code the credentials.
- **Credentials behind an environment with required reviewers.** Repository secrets bound
  to a GitHub environment, so a human approves each run.
- **A marker excluded from the default run**, e.g. `@pytest.mark.live`. Prefer
  `-m 'not live'` in the `addopts` of `pyproject.toml`, beside `-p no:respx` as
  prerequisites Step 2 gives, over the same option on the command line;
  pytest options are a sanctioned adaptation of that file, per *Step 4: Apply only the
  sanctioned adaptations* in `reference/github-actions.md`.
- **A dedicated account, and no account identifier in the test.** The data the test reads
  should be a fixture account's, not a real user's, and the assertions name shapes and
  types rather than values that would leak whose account it is.

**Fix:** treat its result as information, not a gate, and keep it out of the required
contexts.

### A fixture payload whose dates must be upcoming — mocking Step 2

An end-to-end test that feeds a real captured payload (e.g. an `.eml`) through the mocked
transport and asserts a sensor populates.

**Fix:** **shift the fixture's dates forward at runtime** (parse + rewrite, or template)
rather than `freeze_time(...)`.

**Symptom:** a frozen clock stops the debouncer *Step 1: Write the entity platform files* in
`reference/entities.md` describes, so the entity stays `unknown` and a timer sits at the
frozen wall-clock time, failing teardown.

### Entities still read defaults after `async_block_till_done` — mocking Step 2

In a setup test, the on-add refresh is debounced and won't fire within `block_till_done`.

**Fix:** call `coordinator.async_update_listeners()` to notify entities from the
**already-loaded** `coordinator.data` synchronously — unlike `async_refresh()` it schedules
no new timer, so teardown stays clean.

> **Note:** the fix for production is the `async_added_to_hass` initial-state population
> that *Step 1: Write the entity platform files* in `reference/entities.md` gives; the test
> then needs no nudge at all.

### Ruff flags a file under `tests/` or `scripts/` — mocking Step 4

Tests are linted under `tests/ruff.toml`, core's own. It extends `pyproject.toml`, keeping
that file's `PTH` exemption for `tests/**`, then ignores the rules it lists and sets its own
banned APIs and isort sections. The rest applies: `tests/` and every sub-directory of it holding
tests carries an `__init__.py` (`INP001`) with a module docstring (`D104`).

`scripts/*` is exempted from `T20` and `INP001`, the rules a standalone tool cannot meet.
