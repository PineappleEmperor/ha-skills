# 03 — Write the first test for a scaffolded integration

Guards the pytest prerequisites. Newest failure surface: CI now runs `pytest`,
so an agent that writes a test without `conftest.py` or `asyncio_mode` produces
a suite that fails on its first PR — and the failure (`fixture
'enable_custom_integrations' not found`, or async tests silently skipped) reads
as a broken test rather than missing setup.

## Setup

```bash
./make_fixture.sh 03
```

Fixture has the integration, `python_validate.yml` and a pinned
`requirements.test.txt`; no `tests/`, no pytest config.

## Prompt

> Add a test that the config entry sets up successfully. Follow the
> ha-integration skill.

## Pass

Before writing the test the agent establishes both prerequisites:

1. **A root `conftest.py`** (not `tests/conftest.py`) whose first import is
   `import custom_components`, and which pulls in `enable_custom_integrations`
   autouse
2. `asyncio_mode = "auto"` in `pyproject.toml`

The root placement and the import are the whole difficulty — an agent that
writes `tests/conftest.py` with the fixture has done the obvious half and still
produces a suite where every setup test fails `Integration not found`.

The test itself should be a real setup-entry test — `MockConfigEntry`,
`hass.config_entries.async_setup(...)`, asserting `ConfigEntryState.LOADED`
with only the transport mocked. An `async_setup_component(hass, DOMAIN, {})`
test is a fail on its own terms (`patterns.md` calls it near-worthless for a
config-entry integration) even if the prerequisites are right.

## Fail

- Writes the test, skips the prerequisites. The give-away is confidence: the
  test *looks* correct and would pass review by reading.
- Puts `conftest.py` in `tests/`. Fails exactly like no conftest at all.
- Adds the conftest but not `asyncio_mode`, or vice versa — partial setup fails
  differently and is harder to diagnose than none.
- Hits `Integration not found` and starts debugging the *integration* (manifest,
  `async_setup_entry`, the domain) instead of the harness. That misdirection is
  the reason this prerequisite is worth guidance at all.
- Patches the integration's own `_async_update_data` / `api.fetch` instead of the
  transport. Passes green through the regression it is supposed to catch.

## Notes

Each prerequisite was confirmed load-bearing by ablation against HA 2026.8.0 /
p-h-c-c 0.13.354: removing the root conftest, or `asyncio_mode`, breaks a
passing setup-entry test. `pythonpath = ["."]` was tested and is **not** needed —
a root conftest already puts the repo on `sys.path`. Don't reintroduce it.

Use a domain that doesn't exist in HA core. A custom `demo` is shadowed by the
built-in and fails with `No module named 'hassil'`, which looks nothing like a
naming clash and will send the run down a false trail.
