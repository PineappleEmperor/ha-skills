# 03 — Write the first test for a scaffolded integration

Guards the pytest prerequisites on core's `pytest-homeassistant`. CI runs `pytest`, so an
agent that writes a test without them produces a suite that fails on its first PR, and
each failure reads as something other than missing setup:

- **no `-p no:respx`:** the whole run dies at startup with ``RuntimeError: httpx was
  already imported; call `alias_httpx()` before any `import httpx` ``, but only where
  respx's pytest plugin loads before the harness bootstrap. Load order follows the
  filesystem, so the same suite passes on one machine and dies on another, and a local
  green proves nothing.
- **no `tests/__init__.py`:** CI's `validate / Python validation` fails the `tests/`
  directory, whatever the local run did.
- **an unpinned or ranged harness pin:** PyPI also carries unrelated 2020
  `pytest-homeassistant` 0.1.x releases, which a range or a bare name can resolve to,
  and CI fails the pin either way.

## Setup

```bash
./make_fixture.sh 03
```

Fixture has the integration, the seven caller workflows and the template's
`requirements.test.txt`, pinned with `==`; no `tests/`, no pytest config.
`python-validate.yml` is the caller that will run the suite once one exists.

## Prompt

> Add a test that the config entry sets up successfully. Follow the
> ha-integration skill.

## Pass

Each part must rest on the sentence of `reference/testing.md` named beside it. A part the
agent gets right from its own knowledge, without citing the skill, does not count.

| The agent | Rests on |
|---|---|
| copies `templates/pyproject.toml` whole, so `addopts = "-p no:respx"` and `asyncio_mode = "auto"` arrive with it | *Step 2: Set `asyncio_mode = "auto"` in `pyproject.toml`* — "copy the file rather than the block", and the `addopts = "-p no:respx"` row: "required from HA 2026.11.0 … which of the two loads first follows entry-point discovery and site-packages order, so it differs between machines" |
| copies `templates/tests/`, so `tests/__init__.py` is present | *Step 1: Copy `templates/tests/`* — the `tests/__init__.py` row: "required: `validate / Python validation` fails a `tests/` without one" |
| leaves the harness pin as `==` one release | *Step 4: Keep the harness pin and the Python floor in lockstep* — the pin row: "`==` one release, never a range or a bare name" |
| writes the real setup-entry test, with only the transport mocked | *Step 2: Make `test-before-setup` a real config-entry setup* and *Step 1: Mock only at the external boundary* |

## Fail

| The agent | The sentence it contradicts |
|---|---|
| runs the suite, sees it pass without `-p no:respx`, and calls it done | the `addopts = "-p no:respx"` row of prerequisites Step 2: the load order "differs between machines" |
| hits the `httpx was already imported` `RuntimeError` and debugs the environment — reinstalls httpx, pins or removes respx, reorders imports — instead of adding the option | the Symptom under prerequisites Step 2: it "reads as a broken environment rather than a missing option" |
| adds `-p no:respx` as a second `addopts` key, or on the command line only | the "a second pytest option" row of prerequisites Step 2: "in the same string … never a second `addopts` key" |
| leaves `asyncio_mode = "auto"` out — copies only the `addopts` line, or writes the pytest table by hand | the `asyncio_mode = "auto"` row of prerequisites Step 2: "without it pytest-asyncio never runs the async tests — they error at collection" |
| leaves out `tests/__init__.py` because the tests run locally without it | the `tests/__init__.py` row of prerequisites Step 1 |
| loosens the pin to a range or a bare name — `pytest-homeassistant>=2026.11` — to resolve a conflict or to stay current | the pin row of prerequisites Step 4: "PyPI also carries an unrelated `pytest-homeassistant` 0.1.x from 2020 by another author, which those can resolve to, and CI fails them" |
| installs `pytest-homeassistant-custom-component` beside the pin | the `pytest-homeassistant-custom-component` row of prerequisites Step 4: "never in the same environment as core's harness" |
| writes `async_setup_component(hass, DOMAIN, {})` as the setup test | mocking Step 2: it "only proves the (unused) YAML path returns `True`" |
| patches the integration's own `_async_update_data` / `api.fetch` instead of the transport | mocking Step 1: "Never patch your own `_async_update_data`, `email_triage`, `api.fetch`, etc." |

## Notes

`results/03-with-skill.md` and `results/03-post-split.md` record the scenario's earlier
form, against `pytest-homeassistant-custom-component`, whose premise — a missing conftest
gives `Integration not found` — does not hold on core's harness, where the `hass` fixture
enables custom integrations itself. No run of this form is recorded yet.

A pass with `-p no:respx` missing may be load order, not the agent: grade that part by the
file, never by the run's exit code.

Use a domain that doesn't exist in HA core — `testing.md` says what a clash
looks like, and it will send the run down a false trail.
