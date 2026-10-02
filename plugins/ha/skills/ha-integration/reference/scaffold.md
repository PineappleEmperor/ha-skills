# Scaffolding an integration

Scope: a new integration repository, from the first question to its GitHub settings, and `manifest.json`.

**Core rule:** every file is copied from its source or written from the Step 1 answers — never
from memory.

## Contents

1. The scaffold
2. Step 1: Ask the user the ten questions below
3. Step 2: Put the folder under git and on GitHub
4. Step 3: Write the integration package
5. Step 4: Write `manifest.json`
6. Step 5: Add the brand images to `brand/`
7. Step 6: Copy the config and CI files
8. Step 7: Write the files no template carries
9. Step 8: Run the checks and fix the code
10. Step 9: Commit and push `main`
11. Step 10: Apply the GitHub settings
12. Cases
13. Alignment a human chose meets `ruff format` — Step 3
14. A repository adopting the stack carries ruff exclusions — Step 6
15. `HACS validation` is red — Step 9
16. Reference

## The scaffold

### Step 1: Ask the user the ten questions below

All at once, before anything is written.

| # | Requirement | Answer | Default |
|---|---|---|---|
| 1 | domain | snake_case, e.g. `my_device` | — |
| 2 | friendly name | e.g. `My Device` | — |
| 3 | description | one sentence | — |
| 4 | IoT class | one of the `iot_class` values in Step 4 | — |
| 5 | data model | polling, via `DataUpdateCoordinator` · push, via a subscription | — |
| 6 | auth model | none · API key · OAuth · username and password | — |
| 7 | platforms | the entity platforms it provides — sensor, switch, light, button, notify, … | — |
| 8 | licence | the full text goes in `LICENSE` | MIT |
| 9 | version | — | `0.1.0` |
| 10 | repository | its name on GitHub; an existing folder is renamed to match | the existing folder's name |

**Timing:** settle the domain before Step 2. It names the `custom_components/<domain>/`
folder and the manifest's `domain` key, and every config entry is stored under it.

### Step 2: Put the folder under git and on GitHub

| Scenario | Choice |
|---|---|
| the user already has a folder | work in it, renamed to the Step 1 repository name if the two differ; `git init` if it is not a repository yet |
| no folder yet | `mkdir <repository>`, then `git init` inside it |
| no GitHub repository yet | `gh repo create <repository> --public --description "<the Step 1 description>" --source . --remote origin`, from inside the folder |
| an empty GitHub repository already exists, with no ruleset on `main` | `git remote add origin <its URL>` |

### Step 3: Write the integration package

Under `custom_components/<domain>/`. What goes inside each file is `reference/patterns.md`.

| File | Holds | When |
|---|---|---|
| `__init__.py` | entry setup and unload | always |
| `config_flow.py` | the config flow | always |
| `const.py` | the domain and the constants | always |
| `manifest.json` | the manifest — Step 4 | always |
| `strings.json` | the flow and entity strings | always |
| `translations/en.json` | the English translation | always |
| `quality_scale.yaml` | the tier ledger — `reference/quality-scale.md` | always |
| `diagnostics.py` | the diagnostics download — *Diagnostics platform — Step 1* in `reference/patterns.md` | always |
| `<platform>.py` | one per platform chosen in Step 1 | always |
| `brand/` | the brand images — Step 5 | always |
| `icons.json` | action icons, `{"services": {"my_action": {"service": "mdi:icon"}}}` | the integration registers an action |
| `services.yaml` | each action's fields — *`services.yaml` + `strings.json` (hassfest rules) — Step 1* in `reference/patterns.md` | the integration registers its own action, where no standard one fits |
| `api.py`, `coordinator.py`, `models.py`, `entity.py`, `helpers.py` | what *Step 1: Lay out the files by responsibility* in `reference/patterns.md` gives each | as that step says |

**Docstrings and comments in every generated module**

| Rule | Value |
|---|---|
| module docstring | on every file; the only docstring that may run to several lines, and the place a file-level constraint is explained |
| public function and class docstrings | one line; what the audit checks and what it leaves to you is *What the audit checks now* in ha-integration-ci's README |
| inline comments | only where the code does not show why |

### Step 4: Write `manifest.json`

The key order is item 5 of *Lint & quality check* in `SKILL.md`.

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

### Step 5: Add the brand images to `brand/`

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

**What an absent file serves instead**, tried in order — `IMAGE_FALLBACKS` in core's `homeassistant/components/brands/const.py`, at the `.0` tag of the release row's value:

- `logo.png` → `icon.png`
- `icon@2x.png` → `icon.png`
- `logo@2x.png` → `logo.png` → `icon.png`
- `dark_icon.png` → `icon.png`
- `dark_logo.png` → `dark_icon.png` → `logo.png` → `icon.png`
- `dark_icon@2x.png` → `icon@2x.png` → `icon.png`
- `dark_logo@2x.png` → `dark_icon@2x.png` → `logo@2x.png` → `logo.png` → `icon.png`
- nothing in the chain → the brands CDN's copy; with none there, a 404 when requested with `?placeholder=no`, a generic placeholder otherwise

**Rules every file must meet**

- PNG; compressed and optimised, lossless preferred, interlaced preferred, transparent preferred.
- The unprefixed file is the one optimised for a white ground; the dark-optimised one takes the `dark_` prefix.
- Trimmed to the subject — no border, no transparent padding.
- Icons are 1:1 at exactly 256 and 512, not a range.
- Logos respect the brand's own aspect ratio; landscape is preferred, the shortest-side band is the only hard rule.
- A brand's marks are its owner's, used for identification only and implying no endorsement.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| duplicating the icon at `logo.png` | ship only the icons | `icon.png` already serves that slot | *Using the same image for logo & icon* in the brands README |
| padding a mark into a landscape canvas | trim, and ship it square | no rule requires a logo aspect ratio | *Image specification* and *Logo image requirements* in the brands README |
| honouring a brand's clear-space guideline inside the PNG | trim, and let Home Assistant space it | that guideline governs placement in a UI, not the asset | *Image specification* in the brands README |
| omitting `icon@2x.png` because the 1× is served | ship it | a HiDPI client renders 256px where it asked for 512 | `IMAGE_FALLBACKS` in core's `homeassistant/components/brands/const.py`, and *Icon image requirements* in the brands README |
| dressing an integration up as an official one | your own mark | it is what the no-HA-branding rule protects against | *Image specification* in the brands README |
| deriving a new mark from a brand's artwork | reproduce theirs, and meet any published usage terms | identification is the only permitted use | *Trademark Legal Notices* in the brands README |
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

### Step 6: Copy the config and CI files

Copy every file in the table under *Step 2: Take each file from its source* in
`reference/github-actions.md`, except `CLAUDE.md`, which is Step 7. Resolve each caller's pin
as *Step 3: Resolve each caller's pin* in `reference/github-actions.md` says. The root files
among them:

| File | Holds | Taken from |
|---|---|---|
| `pyproject.toml` | HA core's ruff rule set adapted for a custom integration — `google` docstrings, HA's Python floor, no `from __future__ import annotations` — and the `asyncio_mode = "auto"` without which no async test runs | `templates/pyproject.toml`, verbatim |
| `mypy.ini` | the general section of HA core's mypy config — keep `python_version` in `[mypy]`, since it is what the audit's version comparison reads from this file — *What the audit checks now* in ha-integration-ci's README | `templates/mypy.ini`, verbatim |
| `requirements.test.txt` | the pinned test harness — why the pin matters is `reference/testing.md` | `templates/requirements.test.txt` |
| `tests/conftest.py`, `tests/__init__.py`, `tests/ruff.toml` | the harness setup and core's ruff rules for tests — `reference/testing.md` | `templates/tests/` |
| `.gitignore` | the paths git must never track | `templates/.gitignore` |
| `ruleset.json` | the branch ruleset — what it requires is `reference/github-setup.md` | `templates/ruleset.json` |
| `.githooks/commit-msg` | the Conventional Commit check — `reference/commits.md` | release-flow's copy, `chmod +x` |
| `.pre-commit-config.yaml` | the local hooks: ruff, codespell, `check-json`, a guard on `main`, yamllint and prettier | `templates/.pre-commit-config.yaml`, verbatim |
| `.yamllint`, `.prettierrc.js`, `.prettierignore` | the configs yamllint and prettier read | the files of those names in `templates/`, verbatim |
| `.githooks/pre-commit` | the wrapper that runs the local hooks on commit | the snippet below, `chmod +x` |

| Rule | Value |
|---|---|
| what a new repository changes in a copy | nothing, except the fixtures `tests/conftest.py` gains as the tests are written, and in a panel repository the `frontend/package.json` and `requirements.test.txt` rows of *Step 4: Apply only the sanctioned adaptations* in `reference/github-actions.md` |
| `.github/dependabot.yml` | copied unchanged; GitHub needs nothing switched on for it |
| a copy that relaxes `pyproject.toml`'s ruff or pytest tables | drift |
| enabling the commit hook | the `CLAUDE.md` snippet in Step 7; in this clone `bootstrap_repo.sh` sets it at Step 10, after the first commit, which the guard on `main` would otherwise refuse |
| enabling the local hooks | install `pre-commit`; the same `core.hooksPath` setting runs the wrapper, and `pre-commit install` refuses to run while that setting is in place |
| what prettier leaves alone | Markdown, as core leaves it; and `.github/`, `ruleset.json` and a built panel bundle, so a copied or built file stays identical to its source |
| omitting `.gitignore` | a local `pytest` plus a `git add -A` tracks `.pyc` files, which *What the audit checks now* in ha-integration-ci's README fails a repository for |
| `panel-bundle.yml` and `frontend/` | only an integration that serves a panel — `reference/panels.md` |
| a file left out | its own audit failure on the first CI run |

**`.githooks/pre-commit`**

```sh
#!/bin/sh
if ! command -v pre-commit >/dev/null 2>&1; then
  echo "pre-commit is not installed: pip install pre-commit" >&2
  exit 1
fi
exec pre-commit run
```

### Step 7: Write the files no template carries

| File | Holds | Taken from |
|---|---|---|
| `CLAUDE.md` | the per-repo rule that a session invokes this skill before touching integration code, and the hooks setting | the snippet below |
| `hacs.json` | the HACS manifest | the shape below |
| `README.md` | the project readme, with at least one image, carrying the AI-assistance note below | — |
| `LICENSE` | the full text of the Step 1 licence | the licence's own text |
| `tests/` | one test file per module under test | `reference/testing.md` |

| Rule | Value |
|---|---|
| where the skill-invocation rule lives | the repository's own `CLAUDE.md`, never a user's global config |

**Symptom:** a missing or paraphrased licence fails HACS validation with `The repository
license could not be identified (SPDX: NOASSERTION)`; HACS asks for one GitHub can identify
by SPDX, so only the licence's real text resolves it.

**`CLAUDE.md` — the AI-session rule and the hooks setting**

```markdown
## AI sessions
Before writing or modifying integration code (config flow, platforms, manifest,
websocket, services…), invoke the `ha-integration` skill. Re-invoke it after any
`/compact`, since compaction can drop the skill's guidance from context.

## Git hooks
Run `git config core.hooksPath .githooks` once in every clone.
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
| `name` | required in every `hacs.json` |
| `homeassistant` | the oldest HA you actually test, never a floor copied from an example |
| `zip_release` | makes HACS download a release **asset** rather than the tag's source archive, so it requires the `release.yml` caller |
| `filename` | the name `release.yml` attaches — *The three workflows* in ha-integration-ci's README |
| dropping `zip_release` and `filename` | only to have HACS pull the whole tagged repository archive instead |

**Symptom:** a `zip_release` repository whose release carries no attached zip fails HACS
install with `Could not download`.

> **Note:** the tag is the version, not the committed manifest — `reference/versioning.md`.
> What patches the manifest is `release.yml` under *Implementation notes* in
> ha-integration-ci's README.

### Step 8: Run the checks and fix the code

Run *Lint & quality check* in `SKILL.md`, before the first commit.

| Rule | Value |
|---|---|
| a finding | fixed in the code, to the rule `reference/patterns.md` gives for it, or `reference/testing.md` for a test |
| relaxing a copied config to get past a finding | drift — Step 6 |

### Step 9: Commit and push `main`

Commit everything, with a subject in the form *Step 2: Write the subject in the Conventional
Commits form* in `reference/commits.md` gives, then `git push -u origin main`.

### Step 10: Apply the GitHub settings

1. Create the release token, as *Step 1: Generate a fine-grained PAT* in `reference/github-setup.md` says.
2. From the repo root, run `bash scripts/bootstrap_repo.sh "<the Step 1 description>"`, and paste the token when it asks.
3. Fix anything it reports as missing or not done, then run it again.
4. Re-run the `HACS Validation` workflow from the Actions tab: the Step 9 push ran it before these settings existed.

**Timing:** after Step 9 — the ruleset's required checks apply even to the push that creates
`main`, so applied first it refuses that push.

## Cases

### Alignment a human chose meets `ruff format` — Step 3

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

### A repository adopting the stack carries ruff exclusions — Step 6

The stack lints and formats the whole tree, for the reason the `python-validate.yml` bullet
under *Implementation notes* in ha-integration-ci's README gives, and
`templates/pyproject.toml` excludes nothing. Anything kept out of ruff's sight is linted once
the repository adopts that file.

**Fix:** drop the exclusions and format what they were hiding as its own `style:` commit,
before the migration.

**Timing:** before the migration, so its diff carries no reformatting.

### `HACS validation` is red — Step 9

Each `hacs/action` check below is ignorable via its `ignore:` input; how the scaffold's
workflow sets it is the `hacs-validate.yml` row under *Step 2: Take each file from its
source* in `reference/github-actions.md`. Listing in `hacs/default`
requires the action to pass with no errors **and no ignores**, so every row is required.

| Check | What's needed | Where to fix |
|---|---|---|
| `archived` | the repository is not archived | GitHub repo settings |
| `brands` | `brand/icon.png` present, else the domain listed in `home-assistant/brands` | Step 5 |
| `description` | the repository has a description | Step 10, or GitHub repo settings → About |
| `hacsjson` | `hacs.json` exists, carries `name`, and names a `filename` whenever `zip_release` is set | Step 7 |
| `images` | the README carries at least one image | Step 7 |
| `information` | `README.md` exists | Step 7 |
| `integration_manifest` | `manifest.json` carrying `domain`, `name`, `version`, `documentation`, `issue_tracker` and `codeowners` | Step 4 |
| `issues` | the Issues tab is enabled | Step 10, or GitHub repo settings → Features |
| `topics` | the repository has at least one topic | Step 10, or GitHub repo settings → About |
| `license` | a `LICENSE`, per Step 1 | Step 7 |

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
