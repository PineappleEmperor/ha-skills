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

Fixture has the integration, the seven caller workflows and a pinned
`requirements.test.txt`; no `tests/`, no pytest config. `python-validate.yml` is
the caller that will run the suite once one exists.

## Prompt

> Add a test that the config entry sets up successfully. Follow the
> ha-integration skill.

## Pass

Before writing the test the agent establishes the prerequisites
`reference/testing.md` names: a **root** `conftest.py` (not `tests/conftest.py`)
copied from the template, and `asyncio_mode = "auto"` in `pyproject.toml`. The
root placement is the whole difficulty — an agent that writes `tests/conftest.py`
with the fixture has done the obvious half and still gets the failure
`testing.md` describes.

The test itself should be the real setup-entry test `testing.md` specifies, with
only the transport mocked. An `async_setup_component(hass, DOMAIN, {})` test is a
fail on its own terms (`testing.md` calls it near-worthless for a config-entry
integration) even if the prerequisites are right.

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

The ablation that confirmed each prerequisite load-bearing was run against HA
2026.8.0 / p-h-c-c 0.13.354 (`results/03-post-split.md`); `testing.md` carries
the conclusions, including why `pythonpath` is not needed.

Use a domain that doesn't exist in HA core — `testing.md` says what a clash
looks like, and it will send the run down a false trail.
