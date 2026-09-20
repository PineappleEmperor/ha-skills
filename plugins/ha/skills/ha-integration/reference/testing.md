# Testing an integration

Read this when writing or fixing an integration's tests. The code patterns being tested are
`reference/patterns.md`.

**Each prerequisite below fails the *whole* suite rather than one test.**

## Contents

1. Testing — prerequisites before any of the rules below apply
2. Step 1: Put a `conftest.py` at the repo root
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
13. The integration allows multiple devices — mocking Step 2
14. A question a mock cannot answer — mocking Step 1
15. A fixture payload whose dates must be upcoming — mocking Step 2
16. Entities still read defaults after `async_block_till_done` — mocking Step 2
17. Ruff or pyright flags a file under `tests/` or `scripts/` — mocking Step 4

## Testing — prerequisites before any of the rules below apply

`pytest-homeassistant-custom-component` does not work out of the box.

> **Note:** re-derive against the pinned harness version in `reference/freshness.md` if
> these stop matching what you see.

### Step 1: Put a `conftest.py` at the repo root

Not in `tests/`. Copy `templates/conftest.py`. It claims the name `custom_components` for
this repo, and pulls in `enable_custom_integrations` autouse (required >= 2021.6.0b0).

**Symptom:** every setup test fails with `Setup failed for '<domain>': Integration not
found` — which reads as a broken test, not as missing wiring.

- A `custom_components/__init__.py` does not fix this; neither does `pythonpath`.
- No `pythonpath` entry is needed: a root conftest already puts the repo root on
  `sys.path`, so `pytest` works from any directory.
- Fixtures that must initialise *before* `enable_custom_integrations` — `recorder_mock` is
  the known one — have to be requested ahead of it in the same signature.

### Step 2: Set `asyncio_mode = "auto"` in `pyproject.toml`

The shipped `templates/pyproject.toml` carries that table alongside the ruff rules; copy
the file rather than the block.

**Symptom:** pytest-asyncio never runs the async tests — they error at collection.

### Step 3: Ship a `config_flow.py` that imports

Whenever `manifest.json` sets `"config_flow": true`. HA imports the flow module *during
entry setup*, not only when a user opens the flow.

**Symptom:** the setup test fails with `Error importing platform config_flow from
integration <domain>` — which reads as a test problem and is a wiring problem.

### Step 4: Keep the harness pin and the Python floor in lockstep

The pinned `pytest-homeassistant-custom-component` in `requirements.test.txt` hard-pins
`homeassistant==<matching release>`, so **that pin decides which HA the suite runs
against**. Keep it in lockstep with the Python floor the CI declares; the audit compares the
two (ha-integration-ci's README, *What the audit checks now*).

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
- Pass config as explicit constructor args, so pyright catches a missing field instead of a
  helper reaching into `self.<attr>` set elsewhere.

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

### Step 3: Unit-test the pure logic directly

Regex parsers, date/format extraction and data transforms (`order_parse`, `voucher_parse`,
`sort_orders`, …) take a string or object and return a value, with no HA and no mocks.

### Step 4: Minimum coverage before claiming a tier

Cover all of: config-flow (happy path + each error + reauth/reconfigure), a real setup-entry
`LOADED` test (plus a **two-entry parallel `LOADED`** test if multiple devices are allowed),
coordinator success + auth-failure + the credential-read path against a mocked transport,
unload, and a unit test per parser.

**Timing:** wire the regression test *first* on any bug fix — confirm it fails on the
unpatched code, then fix.

Which rules demand a behavioural test before you may mark them `done`, and what each test
must prove, is `reference/quality-scale.md`.

## Cases

### The domain already exists in HA core — prerequisites Step 1

A custom `demo`, `sun`, `light`… is shadowed by the built-in.

**Symptom:** core's dependencies fail to import (`No module named 'hassil'` for `demo`),
which looks nothing like a naming clash.

**Fix:** check `homeassistant/components/` before fixing the domain.

**Timing:** the domain cannot change later.

### The integration allows multiple devices — mocking Step 2

Add a test that `add_to_hass`es two `MockConfigEntry`s and
`await asyncio.gather(hass.config_entries.async_setup(e1.entry_id), …(e2.entry_id))`, then
asserts **both** `state is ConfigEntryState.LOADED`. A single-entry `LOADED` test can't
catch integration-global registration done per-entry (static paths, websocket commands, the
panel).

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
  `addopts = "-m 'not live'"` in `pyproject.toml` over `-m 'not live'` on the command line;
  pytest options are a sanctioned adaptation of that file, per *Sanctioned adaptations — the
  complete list* in `reference/github-actions.md`.
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

**Symptom:** freezing the clock stops the debouncer `reference/patterns.md` describes under
`update_before_add`, so the entity never populates (state stays `unknown`), *and* it leaves
a timer scheduled at the frozen wall-clock time that fails teardown.

### Entities still read defaults after `async_block_till_done` — mocking Step 2

In a setup test, the on-add refresh is debounced and won't fire within `block_till_done`.

**Fix:** call `coordinator.async_update_listeners()` to notify entities from the
**already-loaded** `coordinator.data` synchronously — unlike `async_refresh()` it schedules
no new timer, so teardown stays clean.

> **Note:** the fix for production is the `async_added_to_hass` initial-state population
> `reference/patterns.md` gives under *Entity platform files*; the test then needs no nudge
> at all.

### Ruff or pyright flags a file under `tests/` or `scripts/` — mocking Step 4

The shipped `pyproject.toml` already exempts `scripts/*` and `tests/**` from the rules its
per-file-ignores table names.

`result["type"]` → `result.get("type")` in tests, and the same for `["errors"]` and
`["reason"]`: on a flow `ConfigFlowResult` they are `reportTypedDictNotRequiredAccess` under
pyright.
