# Scaffolding an integration

Scope: starting a new integration repository — what to ask, and what to write. The code that
goes inside the generated files is `reference/patterns.md`.

**Core rule:** every file is generated from the Step 1 answers or copied from `templates/`.
Nothing here is authored from memory.

## Contents

1. The scaffold
2. Step 1: Gather the requirements
3. Step 2: Generate the integration package
4. Step 3: Generate the repo root
5. Step 4: Copy the CI stack
6. Step 5: Ship the brand assets
7. Step 6: Order `manifest.json`
8. Step 7: Pass HACS validation
9. Cases
10. Alignment a human chose meets `ruff format` — Step 2
11. A repository adopting the stack carries ruff exclusions — Step 3
12. Reference

## The scaffold

### Step 1: Gather the requirements

Ask all nine at once.

| # | Requirement | Answer | Default |
|---|---|---|---|
| 1 | domain | snake_case, e.g. `my_device` | — |
| 2 | friendly name | e.g. `My Device` | — |
| 3 | description | one sentence | — |
| 4 | IoT class | one of the `iot_class` values in Step 6 | — |
| 5 | data model | polling, via `DataUpdateCoordinator` · push, via a subscription | — |
| 6 | auth model | none · API key · OAuth · username and password | — |
| 7 | platforms | any of button, sensor, binary_sensor, switch, light, number, select, text, notify, cover, climate, fan, lock, media_player, vacuum | — |
| 8 | licence | the full text goes in `LICENSE` | MIT |
| 9 | version | — | `0.1.0` |

**Timing:** the domain is fixed once the repository exists — it is the folder name, the
manifest key, the brand folder and every entity id. Settle it before Step 2.

**Symptom:** a missing or paraphrased licence fails HACS validation with `The repository
license could not be identified (SPDX: NOASSERTION)`; HACS asks for one GitHub can identify
by SPDX, so only the licence's real text resolves it.

### Step 2: Generate the integration package

Under `custom_components/<domain>/`. What goes inside each file is `reference/patterns.md`.

| File | Holds | When |
|---|---|---|
| `__init__.py` | entry setup and unload | always |
| `config_flow.py` | the config flow | always |
| `const.py` | the domain and the constants | always |
| `manifest.json` | the manifest — key order is Step 6 | always |
| `strings.json` | the flow and entity strings | always |
| `translations/en.json` | the English translation | always |
| `quality_scale.yaml` | the tier ledger — `reference/quality-scale.md` | always |
| `diagnostics.py` | the `diagnostics` rule | always |
| `<platform>.py` | one per platform chosen in Step 1 | always |
| `brand/` | the brand images — Step 5 | always |
| `icons.json` | action icons, `{"services": {"my_action": {"service": "mdi:icon"}}}` | the integration registers an action |
| `services.yaml` | the action descriptions | a custom action is genuinely needed — prefer a standard one |
| `api.py`, `coordinator.py`, `models.py`, `entity.py`, `helpers.py` | as `reference/patterns.md` splits them | the module earns its own file |

**Docstrings and comments in every generated module**

| Rule | Value |
|---|---|
| module docstring | on every file, the only one that may run to several lines, and where a file-level constraint is explained rather than in a comment |
| public function and class docstrings | short, single-line; what the audit checks and what it leaves to you is *What the audit checks now* in ha-integration-ci's README |
| inline comments | only where the WHY is genuinely non-obvious |
| the bar | clean under the *Lint & quality check* commands in `SKILL.md` |

### Step 3: Generate the repo root

| File | Holds | Taken from |
|---|---|---|
| `CLAUDE.md` | the per-repo rule that a session invokes this skill before touching integration code | the snippet below |
| `hacs.json` | the HACS manifest | the shape below |
| `pyproject.toml` | HA core's ruff rule set adapted for a custom integration — `google` docstrings, HA's Python floor, no `from __future__ import annotations` — and the `asyncio_mode = "auto"` without which no async test runs | `templates/pyproject.toml`, verbatim |
| `mypy.ini` | the general section of HA core's mypy config — keep `python_version` in `[mypy]`, since it is what the audit's version comparison reads from this file — *What the audit checks now* in ha-integration-ci's README | `templates/mypy.ini`, verbatim |
| `requirements.test.txt` | the pinned test harness — why the pin matters is `reference/testing.md` | `templates/requirements.test.txt` |
| `tests/conftest.py`, `tests/__init__.py` | the harness setup — `reference/testing.md` | `templates/tests/` |
| `tests/` | one test file per module under test | `reference/testing.md` |
| `README.md` | the project readme, carrying the AI-assistance note below | — |
| `LICENSE` | the full text of the Step 1 licence | the licence's own text |
| `.gitignore` | `__pycache__/`, caches, venvs, HA dev artefacts (`.storage/`, `home-assistant.log*`, the `_v2.db`) and `device_map.md`, a note of a home's devices and addresses kept beside its logs | `templates/.gitignore` |
| `ruleset.json` | the branch ruleset — what it requires is `reference/github-setup.md` | `templates/ruleset.json` |
| `.githooks/commit-msg` | the Conventional Commit check — `reference/commits.md` | release-flow's copy, `chmod +x` |
| `.pre-commit-config.yaml` | the local hooks: ruff, codespell, `check-json`, a guard on `main`, yamllint and prettier | `templates/.pre-commit-config.yaml`, verbatim |
| `.yamllint`, `.prettierrc.js`, `.prettierignore` | the configs yamllint and prettier read | the files of those names in `templates/`, verbatim |
| `.githooks/pre-commit` | the wrapper that runs the local hooks on commit | the snippet below, `chmod +x` |

| Rule | Value |
|---|---|
| a copy that relaxes `pyproject.toml`'s ruff or pytest tables | drift |
| enabling the commit hook | `git config core.hooksPath .githooks`, once per clone, documented in `CLAUDE.md` |
| enabling the local hooks | install `pre-commit`; the same `core.hooksPath` setting runs the wrapper, and `pre-commit install` refuses to run while that setting is in place |
| what prettier leaves alone | Markdown, as core leaves it; and `.github/`, `ruleset.json` and a built panel bundle, so a copied or built file stays identical to its source |
| omitting `.gitignore` | a local `pytest` plus a `git add -A` tracks `.pyc` files, which *What the audit checks now* in ha-integration-ci's README fails a repository for |
| where the skill-invocation rule lives | the repository's own `CLAUDE.md`, never a user's global config |

**`CLAUDE.md` — the AI-session rule**

```markdown
## AI sessions
Before writing or modifying integration code (config flow, platforms, manifest,
websocket, services…), invoke the `ha-integration` skill. Re-invoke it after any
`/compact`, since compaction can drop the skill's guidance from context.
```

**`.githooks/pre-commit`**

```sh
#!/bin/sh
if ! command -v pre-commit >/dev/null 2>&1; then
  echo "pre-commit is not installed: pip install pre-commit" >&2
  exit 1
fi
exec pre-commit run
```

**`README.md` — the AI-assistance note**, as a GitHub `> [!NOTE]` admonition, the skill name
linked to its public repository:

```markdown
> [!NOTE]
> **AI assistance:** I'm a programmer; this project is built with AI (Claude, via Claude Code) for implementation, code review, and QA — under human direction, guided by my [`ha-integration`](https://github.com/PineappleEmperor/ha-skills) skill. Architecture and final review are mine; every change is human-reviewed before it merges.
```

**`hacs.json`**

```json
{"name": "My Integration", "content_in_root": false, "zip_release": true, "filename": "<domain>.zip"}
```

| Rule | Value |
|---|---|
| `name` | the only key HACS strictly requires |
| `homeassistant` | the oldest HA you actually test, never a floor copied from an example |
| `zip_release` | makes HACS download a release **asset** rather than the tag's source archive, so it requires the `release.yml` caller |
| `filename` | the name `release.yml` attaches — *The three workflows* in ha-integration-ci's README |
| dropping `zip_release` and `filename` | only to have HACS pull the whole tagged repository archive instead |

**Symptom:** a `zip_release` repository whose release carries no attached zip fails HACS
install with `Could not download`.

> **Note:** the tag is the version, not the committed manifest — `reference/versioning.md`.
> What patches the manifest is `release.yml` under *Implementation notes* in
> ha-integration-ci's README.

### Step 4: Copy the CI stack

| Rule | Value |
|---|---|
| authored or copied | copied, never authored — `reference/github-actions.md` |
| which files, and where each comes from | the table in `reference/github-actions.md` |
| a caller block | the CI repository's README block with its `{{sha}} # {{tag}}` tokens resolved |
| `panel-bundle.yml` and `frontend/` | only an integration that serves a panel — `reference/panels.md` |
| leaving it to last | not optional: every missing file is its own audit failure on the first run |

### Step 5: Ship the brand assets

Into `custom_components/<domain>/brand/`. Which revision of the spec these rules were read
from is the brand row of `reference/freshness.md`.

**Ship `icon.png`.** It is the only file HACS gates on; the serving layer falls back for the
rest.

| Rule | Value |
|---|---|
| served by | the Brands Proxy API, from HA 2026.3.0 |
| `home-assistant/brands` `custom_integrations/` | legacy; a PR adding one is auto-closed |
| a local `brand/` file | takes precedence over the same file in the brands repository |
| contributing the integration to core | delete `brand/` and open a brands-repository PR instead |

**Which files to ship**

| File | Holds | When |
|---|---|---|
| `icon.png` | exactly 256×256 | always |
| `icon@2x.png` | exactly 512×512 | always |
| `logo.png` | shortest side 128–256, 256 preferred | the logo is a different image from the icon |
| `logo@2x.png` | shortest side 256–512, 512 preferred | as `logo.png` |
| `dark_icon.png`, `dark_icon@2x.png` | as the icons | the icon is unreadable on a dark ground |
| `dark_logo.png`, `dark_logo@2x.png` | as the logos | the logo is unreadable on a dark ground |

**What an absent file serves instead**

- absent `logo.png` → `icon.png`
- absent `@2x` → its 1×
- absent `dark_` file → its unprefixed match
- absent `icon.png`, requested with `?placeholder=no` → 404
- absent `icon.png`, requested without it → a generic placeholder

**Rules every file must meet**

- PNG; compressed and optimised, lossless preferred, interlaced preferred, transparent preferred.
- The unprefixed file is the one optimised for a white ground; the dark-optimised one takes the `dark_` prefix.
- Trimmed to the subject — no border, no transparent padding.
- Icons are 1:1 at exactly 256 and 512, not a range.
- Logos respect the brand's own aspect ratio; landscape is preferred, the shortest-side band is the only hard rule.
- A brand's marks are its owner's, used for identification only and implying no endorsement.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| duplicating the icon at `logo.png` | ship only the icons | `icon.png` already serves that slot | Step 5 |
| padding a mark into a landscape canvas | trim, and ship it square | no rule requires a logo aspect ratio | Step 5 |
| honouring a brand's clear-space guideline inside the PNG | trim, and let Home Assistant space it | that guideline governs placement in a UI, not the asset | Step 5 |
| omitting `icon@2x.png` because the 1× is served | ship it | a HiDPI client renders 256px where it asked for 512 | Step 5 |
| dressing an integration up as an official one | your own mark | it is what the no-HA-branding rule protects against | Step 5 |
| deriving a new mark from a brand's artwork | reproduce theirs, and meet any published usage terms | identification is the only permitted use | Step 5 |
| PR-ing `home-assistant/brands` to fix a blank HACS tile | nothing — it is a HACS-side gap | `custom_integrations/*` PRs are auto-closed | the HACS dashboard row of `reference/freshness.md` |

> **Note:** the HACS store dashboard reads the legacy CDN, not the inline `brand/` folder, so
> an integration with no legacy brands entry renders blank there while Home Assistant's own UI
> shows the icon. Nothing to fix in the repository.

**Where the images come from.** Every size is scaled *down* from one master, so the set is
consistent and nothing is upscaled.

1. The brand's own vector — a press kit's EPS/PDF/SVG.
2. Their largest raster, composed from the crispest part: a 256×256 icon scaled down beats the same mark cropped out of a 512×157 lockup.
3. Generated.

| Rule | Value |
|---|---|
| rasterising a vector | `cairosvg`, or `convert -background none -density 144 in.svg out.png` — ImageMagick's MSVG renderer botches text |
| anything generated | drawn from named constants in a committed script, never hand-edited, with a `docs/brand.md` saying what the constants mean, so the set regenerates at a new size or colour |
| a brand with no usable artwork | a generated mark in the brand's sampled colours, replaced when the vendor supplies one |
| a pixel-display device render | a nearest-neighbour upscale of the byte-faithful preview (`render_layout_png(..., scale=N)`), never a photo |
| a device screenshot's black ground | the device, not a missing alpha channel — and not the padding the trim rule forbids |

| Scenario | Choice |
|---|---|
| the `logo`, which renders large — the integration page, HACS | a busy or detailed screen, which reads well at that size |
| the `icon`, which renders small — ~48px in the integrations list | a simple, low-detail screen; fine detail turns to mush |

### Step 6: Order `manifest.json`

`domain` first, `name` second, then every remaining key alphabetically — hassfest fails any
other order.

```json
{
  "domain": "my_device",
  "name": "My Device",
  "codeowners": ["@username"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/username/repo",
  "integration_type": "device",
  "iot_class": "local_push",
  "issue_tracker": "https://github.com/username/repo/issues",
  "requirements": [],
  "version": "0.1.0"
}
```

| Rule | Value |
|---|---|
| where each rule below was read | https://developers.home-assistant.io/docs/creating_integration_manifest/; beyond the page, `script/hassfest/manifest.py` in core at the `.0` tag of the release row's value and `custom_components/hacs/utils/validate.py` in hacs/integration at the HACS validation row's revision, both rows in `reference/freshness.md` |
| `domain`, `name` | required; the domain is the directory name and never changes |
| `version` | required for a custom integration — hassfest and HACS both fail its absence; a version AwesomeVersion reads as CalVer, SemVer, SimpleVer, BuildVer or PEP 440, the five forms hassfest's `verify_version` accepts; what sets it at release is `reference/versioning.md` |
| `documentation` | required; `https`, and not under `www.home-assistant.io/integrations/`, which hassfest reserves for core |
| `codeowners` | required by hassfest and HACS — at least your own GitHub username |
| `issue_tracker` | required by HACS's `integration_manifest` check |
| `iot_class` | required — `assumed_state` · `calculated` · `cloud_polling` · `cloud_push` · `local_polling` · `local_push` |
| `integration_type` | `device` · `hub` · `service` · `entity` · `hardware` · `helper` · `system`; absent means `hub`, so set it; `virtual` is core-only |
| `config_flow` | `true`, and `config_flow.py` must exist |
| `single_config_entry` | `true` when the integration supports one config entry only; otherwise omit it and meet the `unique-config-entry` rule, `reference/quality-scale.md` |
| `requirements` | pip requirement strings, `aiohue==1.9.1`; only libraries core's own `requirements.txt` does not already carry |
| `loggers` | the names the requirements pass to `getLogger` |
| `dependencies` | integrations that must be set up before this one, built-in or custom — `mqtt` goes here when the integration needs the client |
| `after_dependencies` | integrations set up first only when they are configured; their requirements are installed either way |
| `quality_scale` | *Step 4: Claim the tier in the manifest only once it is fully met* in `reference/quality-scale.md` |
| `zeroconf`, `ssdp`, `bluetooth`, `dhcp`, `usb` | a list of discovery matchers, whose shapes are on the manifest page under each key; the config flow gains the step of that name |
| `homekit` | `{"models": [...]}`, the model-name prefixes to match; the flow gains a `homekit` step |
| `mqtt` | the discovery topics to subscribe to; the flow gains an `mqtt` step |

### Step 7: Pass HACS validation

Each `hacs/action` check below is ignorable via its `ignore:` input; the scaffold never uses
it, and `reference/github-actions.md` has the workflow contract. Listing in `hacs/default`
requires the action to pass with no errors **and no ignores**, so every row is required.

| Check | What's needed | Where to fix |
|---|---|---|
| `archived` | the repository is not archived | GitHub repo settings |
| `brands` | `brand/icon.png` present, else the domain listed in `home-assistant/brands` | a file in the repo |
| `description` | the repository has a description | GitHub repo settings → About |
| `hacsjson` | `hacs.json` exists, carries `name`, and names a `filename` whenever `zip_release` is set | a file in the repo |
| `images` | the README carries at least one image | add a screenshot to the README |
| `information` | `README.md` exists | a file in the repo |
| `integration_manifest` | `manifest.json` carrying `domain`, `name`, `version`, `documentation`, `issue_tracker` and `codeowners` — Step 6 | a file in the repo |
| `issues` | the Issues tab is enabled | GitHub repo settings → Features |
| `topics` | the repository has at least one topic | GitHub repo settings → About |
| `license` | a `LICENSE`, per Step 1 | a file in the repo |

**Timing:** fix every row at scaffold time. `description`, `issues`, `topics` and `license`
are GitHub settings rather than files, so they fail silently until the first
`hacs-validate` run.

## Cases

### Alignment a human chose meets `ruff format` — Step 2

`ruff format` reduces every run of spaces to one, which destroys a table someone aligned so
it could be read as a table. Fence it rather than surrendering it or turning the formatter
off:

```python
# fmt: off
CONF_EMAIL         = "email"
CONF_API_KEY       = "api_key"
CONF_REFRESH_TOKEN = "refresh_token"
# fmt: on
```

| Rule | Value |
|---|---|
| what the fence stops | the formatter only — `ruff check` still runs inside it, so line length, import order and unused names are all still caught |
| what you give up | whitespace normalisation, which is what you are overriding |
| scope | statement-level: one inside a dict or call literal does nothing, so it wraps the whole enclosing statement at that statement's indent |
| `# fmt: on` | never at a different indent from its `# fmt: off` |
| which statement | the smallest one containing the table, never a class body and never a file |
| the column | one per block, set one space past the longest key, spaces only and never tabs; a new block restarts it |
| an entry too long for the column | re-pad the whole block, in the same commit |
| a generator that emits a fenced table | emits the fence too, or the next regeneration drops it |

**What earns a fence**

- Padding before `=` or `:`.
- Padding after them, where the values form the column.
- Padding after `,`.
- One row or record per source line, even where nothing is padded — glyph rasters, icon bitmaps, colour palettes, layout tables, field-descriptor lists.
- Not a flat wrapped list of strings, which is not a table; leave that to the formatter.

**Symptom:** an unfenced raster or bitmap table comes back one element per line, and the
shape a reader could see in the source is gone.

### A repository adopting the stack carries ruff exclusions — Step 3

The stack lints and formats the whole tree — why is the `python-validate.yml` bullet under
*Implementation notes* in ha-integration-ci's README — and `templates/pyproject.toml`
excludes nothing, so anything kept out of ruff's sight becomes visible the moment the
repository adopts that file.

**Fix:** drop the exclusions and format what they were hiding as its own `style:` commit,
before the migration.

**Timing:** before the migration, so its diff carries no reformatting.

## Reference

| file | when to read |
|---|---|
| `reference/patterns.md` | writing the code inside any generated file — setup and unload, coordinator, entity, notify, `entry.runtime_data`, `DeviceInfo`, typing, the file splits |
| `reference/testing.md` | writing the tests, and the harness prerequisites behind `tests/conftest.py` and `requirements.test.txt` |
| `reference/quality-scale.md` | filling in `quality_scale.yaml` |
| `reference/commits.md` | writing the first commit |
| `reference/versioning.md` | where the version comes from, and how an rc and a final are published |
| `reference/github-actions.md` | what the CI stack carries, and each workflow's contract |
| `reference/github-setup.md` | the GitHub side — token, required checks, ruleset |
