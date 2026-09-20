# Scaffolding an integration

What to ask, what to generate, and the conventions the generated code follows. Read with `reference/patterns.md` open — the code patterns live there.

- Gather requirements (ask all at once)
- Files to generate
- Brand assets
- Brand asset sources
- manifest.json key order
- Implementation patterns, file structure, typing & testing
- Code style
- Commit conventions, versioning & CI gating

## Gather requirements (ask all at once)

1. **Domain** — snake_case, e.g. `my_device`. Must be stable; can't change later.
2. **Friendly name** — e.g. "My Device"
3. **Description** — one sentence
4. **IoT class** — `local_polling` / `local_push` / `cloud_polling` / `cloud_push` / `calculated`
5. **Data model** — polling (use `DataUpdateCoordinator`) or push (subscription)
6. **Auth model** — none / API key / OAuth / username+password
7. **Platforms** — button, sensor, binary_sensor, switch, light, number, select, text, notify, cover, climate, fan, lock, media_player, vacuum (pick any)
8. **MicroPython firmware?** (yes/no) — adds `firmware/` exclusion to pyrightconfig.json
9. **Licence** — default **MIT**. HACS validates that the repo has one GitHub can identify
   by SPDX, so a missing or bespoke licence fails `HACS validation` on the first PR with
   `The repository license could not be identified (SPDX: NOASSERTION)`. Write the real
   text of the chosen licence to `LICENSE`; a paraphrase does not resolve.
10. **Version** — default `0.1.0`

## Files to generate

**Integration package** (`custom_components/{domain}/`):
- `__init__.py`
- `config_flow.py`
- `const.py`
- `manifest.json`
- `strings.json`
- `translations/en.json`
- `services.yaml` (only if custom services are genuinely needed; prefer standard services first)
- `icons.json` (action/service icons for UI display — `{"services": {"my_action": {"service": "mdi:icon"}}}`)
- `quality_scale.yaml`
- `diagnostics.py` (the `diagnostics` rule — see `reference/patterns.md`)
- One file per selected platform (e.g. `button.py`, `sensor.py`)
- Additional files as needed: `api.py`, `coordinator.py`, `models.py`, `entity.py`, `helpers.py` (see `reference/patterns.md`)

**Repo root:**
- `CLAUDE.md` — project instructions. **Always include a rule telling future AI sessions to invoke this `ha-integration` skill before writing/modifying integration code, and to re-invoke after `/compact`** (compaction drops the skill's guidance). Keep this enforcement **per-repo, not global** — a project file is the right scope; do not push a user's global config on others. Suggested snippet:
  ```markdown
  ## AI sessions
  Before writing or modifying integration code (config flow, platforms, manifest,
  websocket, services…), invoke the `ha-integration` skill. Re-invoke it after any
  `/compact`, since compaction can drop the skill's guidance from context.
  ```
  (`templates/hooks/` holds optional per-turn reminders for a user's own `~/.claude`; the canonical, shareable enforcement is this `CLAUDE.md` rule, which ships with the repo.)
- `hacs.json` — `name` is the only strict requirement, but the canonical setup ships a **zip release**: `{"name": "My Integration", "content_in_root": false, "zip_release": true, "filename": "<domain>.zip"}` (add `"homeassistant": "<oldest HA you actually test>"`, never a floor copied from an example). `zip_release` makes HACS download a release **asset** instead of the tag source archive — so it **requires** the scaffold's `release.yml` caller, and `filename` must be the name that workflow attaches, per *The three workflows* in ha-integration-ci's README. **Without that workflow, HACS install fails with `Could not download`** (the symptom of a `zip_release` repo whose release has no attached zip). Drop `zip_release`/`filename` only if you deliberately want HACS to pull the whole tagged repo archive instead.

  > **The tag is the version, not the committed manifest** — how that works, and why no PR
  > carries a bump, is `reference/versioning.md`. What matters here: the `release.yml` caller must
  > point at ha-integration-ci's workflow; why that is what patches the manifest is
  > `release.yml` under *Implementation notes* in its README.
- `pyproject.toml` — copy `templates/pyproject.toml` verbatim. Its `[tool.ruff]` tables are
  Home Assistant core's own rule set adapted for a custom integration (`google` docstrings,
  HA's Python floor, no `from __future__ import annotations`), and its pytest table carries
  the `asyncio_mode = "auto"` without which the async tests never run. A copy that relaxes
  those tables is drift.
- `pyrightconfig.json` — the snippet under *MicroPython firmware files* in
  `reference/patterns.md`, with or without the `exclude`.
- `requirements.test.txt` — **required**; copy `templates/requirements.test.txt`. Why the pin matters, and what breaks without it: `reference/testing.md`.
- `conftest.py` — **required, at the repo root, not in `tests/`**; copy `templates/conftest.py`. Why it must be at the root: `reference/testing.md`.
- `tests/` — one file per module under test. Testing rules are `reference/testing.md`.

- `README.md` — **include the AI-assistance disclaimer** as a GitHub `> [!NOTE]` admonition box. Link the skill name to its public repo. Template:
  ```markdown
  > [!NOTE]
  > **AI assistance:** I'm a programmer; this project is built with AI (Claude, via Claude Code) for implementation, code review, and QA — under human direction, guided by my [`ha-integration`](https://github.com/PineappleEmperor/ha-skills) skill. Architecture and final review are mine; every change is human-reviewed before it merges.
  ```
- `LICENSE` — the full text of the chosen licence, per requirement 9 above.
- `.gitignore` — copy `templates/.gitignore`. Covers `__pycache__/`, caches, venvs, HA dev artefacts (`.storage/`, `home-assistant.log*`, the `_v2.db`), and `device_map.md` (the `ha-triage` skill's device map, which that skill says must never be committed). **Not optional:** without it a local `pytest` run plus a `git add -A` tracks `.pyc` files; what that costs is *What the audit checks now* in ha-integration-ci's README.
- `ruleset.json` — copy `templates/ruleset.json` to the repo root; what it requires and why is `reference/github-setup.md`.
- `.githooks/commit-msg` — release-flow's, per `reference/commits.md`; `chmod +x`. **Enable once per clone: `git config core.hooksPath .githooks`** — an unenabled hook is a file, not a guard. Document that line in `CLAUDE.md`.
- `custom_components/{domain}/brand/` — which files to ship and the rules each must meet are
  *Brand assets* below.

**The CI stack** is copied, never authored — the invariant in `SKILL.md`. Missing files here
are separate audit failures on the first run, so this is not an optional last step. The table in
`reference/github-actions.md` says which files the scaffold carries and where each is
copied from; the caller blocks come from the CI repositories' READMEs with their
`{{sha}} # {{tag}}` tokens resolved, and `panel-bundle.yml` with `frontend/` belongs only
to an integration that serves a panel, per `reference/panels.md`.

### Brand assets

Scope: the images a scaffold ships in `custom_components/<domain>/brand/`, and the rules
each must meet. Which revision of the spec these rules were read from is the brand row of
`reference/freshness.md`.

**Core rule:** ship `icon.png`. It is the only file anything gates on; the rest is quality,
and the serving layer falls back.

| Rule | Value |
|---|---|
| served by | the Brands Proxy API, from HA 2026.3.0 |
| `home-assistant/brands` `custom_integrations/` | legacy; a PR adding one is auto-closed |
| a local `brand/` file | takes precedence over the same file in the brands repository |
| contributing the integration to core | delete `brand/` and open a brands-repository PR instead |

**Which files to ship**

| File | Size | Ship it when |
|---|---|---|
| `icon.png` | exactly 256×256 | always |
| `icon@2x.png` | exactly 512×512 | always |
| `logo.png` | shortest side 128–256, 256 preferred | the logo is a different image from the icon |
| `logo@2x.png` | shortest side 256–512, 512 preferred | as `logo.png` |
| `dark_icon.png`, `dark_icon@2x.png` | as the icons | the icon is unreadable on a dark ground |
| `dark_logo.png`, `dark_logo@2x.png` | as the logos | the logo is unreadable on a dark ground |

**What an absent file serves instead**

| Absent | Served |
|---|---|
| `logo.png` | `icon.png` |
| any `@2x` | its 1× |
| any `dark_` file | its unprefixed match |
| `icon.png`, with `?placeholder=no` | 404 |
| `icon.png`, without it | a generic placeholder |

**Rules every file must meet**

- PNG; compressed and optimised, lossless preferred, interlaced preferred, transparent preferred.
- The unprefixed file is the one optimised for a white ground; the dark-optimised one takes the `dark_` prefix.
- Trimmed to the subject — no border, no transparent padding.
- Icons are 1:1 at exactly 256 and 512, not a range.
- Logos respect the brand's own aspect ratio; landscape is preferred, the shortest-side band is the only hard rule.
- A brand's marks are its owner's, used for identification only and implying no endorsement.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| duplicating the icon at `logo.png` | ship only the icons | `icon.png` already serves that slot | *What an absent file serves instead* |
| padding a mark into a landscape canvas | trim, and ship it square | no rule requires a logo aspect ratio | *Rules every file must meet* |
| honouring a brand's clear-space guideline inside the PNG | trim, and let Home Assistant space it | that guideline governs placement in a UI, not the asset | *Rules every file must meet* |
| omitting `icon@2x.png` because the 1× is served | ship it | a HiDPI client renders 256px where it asked for 512 | *Which files to ship* |
| dressing an integration up as an official one | your own mark | it is what the no-HA-branding rule protects against | *Rules every file must meet* |
| deriving a new mark from a brand's artwork | reproduce theirs, and meet any published usage terms | identification is the only permitted use | *Rules every file must meet* |
| PR-ing `home-assistant/brands` to fix a blank HACS tile | nothing — it is a HACS-side gap | `custom_integrations/*` PRs are auto-closed | the HACS dashboard row of `reference/freshness.md` |

> **Note:** the HACS store dashboard reads the legacy CDN, not the inline `brand/` folder, so
> an integration with no legacy brands entry renders blank there while Home Assistant's own UI
> shows the icon. Nothing to fix in the repository.

### Brand asset sources

Scope: where the images come from. **Core rule:** every size is scaled *down* from one
master, so the set is consistent and nothing is upscaled.

| Preference | Source |
|---|---|
| 1 | the brand's own vector — a press kit's EPS/PDF/SVG |
| 2 | their largest raster; compose from the crispest part, so a 256×256 icon scaled down beats the same mark cropped out of a 512×157 lockup |
| 3 | generated |

| Rule | Value |
|---|---|
| rasterising a vector | `cairosvg`, or `convert -background none -density 144 in.svg out.png` — ImageMagick's MSVG renderer botches text |
| anything generated | drawn from named constants in a committed script, never hand-edited, with a `docs/brand.md` saying what the constants mean, so the set regenerates at a new size or colour |
| a brand with no usable artwork | a generated mark in the brand's sampled colours, replaced when the vendor supplies one |
| a pixel-display device render | a nearest-neighbour upscale of the byte-faithful preview (`render_layout_png(..., scale=N)`), never a photo |
| a device screenshot's black ground | the device, not a missing alpha channel — and not the padding the trim rule forbids |

| Target | Renders at | So pick |
|---|---|---|
| `logo` | large — integration page, HACS | a busy or detailed screen, which reads well |
| `icon` | small — ~48px in the integrations list | a simple, low-detail screen; fine detail turns to mush |

**HACS validation**

The `hacs/action` checks below are each ignorable via its `ignore:` input; the scaffold never
uses it, and `reference/github-actions.md` has the workflow contract. Listing in `hacs/default`
requires the action to pass with no errors **and no ignores**, so treat every row as required.
Fix them at scaffold time, since each maps to a file or a GitHub setting:

| Check | What's needed | Where to fix |
|-------|--------------|--------------|
| `archived` | Repo not archived | GitHub repo settings |
| `brands` | `brand/icon.png` present, else the domain listed in `home-assistant/brands` | File in repo |
| `description` | Repo has a description | GitHub repo settings → About |
| `hacsjson` | `hacs.json` exists | File in repo |
| `images` | README contains at least one image | Add screenshot to README |
| `information` | README.md exists | File in repo |
| `issues` | Issues tab enabled | GitHub repo settings → Features |
| `topics` | Repo has at least one topic | GitHub repo settings → About |
| `license` | A `LICENSE` per requirement 9 above | File in repo |

The `description`, `issues`, `topics` and `license` checks fail silently until the first `hacs-validate` run — they're GitHub settings, not files.

## manifest.json key order

Always `domain` first, `name` second, then remaining keys alphabetically:
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
  "single_config_entry": true,
  "version": "0.1.0"
}
```

`single_config_entry` is right for a cloud account or a single hub; omit it when a user may add several devices, and then implement the `unique-config-entry` rule with a unique id instead.

`integration_type` is **required** — choose: `device` / `hub` / `service` / `entity` / `hardware` / `helper` / `system` / `virtual`.

`issue_tracker` is **required by HACS validation** — omitting it fails the `integration_manifest` check.

---

## Implementation patterns, file structure, typing & testing

See **`reference/patterns.md`** — `__init__`/coordinator/entity/notify patterns, `entry.runtime_data`, `DeviceInfo`, the modern `NotifyEntity` path, the typing rules (no `from __future__ import annotations`, typed `ConfigEntry`), the file-split conventions, with the **mock-the-boundary** testing rules in `reference/testing.md`.

---

## Code style

Typing, file structure and the code patterns themselves are `reference/patterns.md`. What a
scaffold must set up:

- Module docstring on every file. **This one may be multi-line** — a file-level explanation of a load-bearing constraint belongs here, not demoted to a comment.
- Short **single-line** docstrings on all public functions and classes. What the audit checks about docstrings, and what it leaves to you, is *What the audit checks now* in ha-integration-ci's README.
- No inline comments unless the WHY is genuinely non-obvious
- Clean under the *Lint & quality check* commands in `SKILL.md`; pyright standard mode

**Alignment a human chose is kept, not collapsed.** `ruff format` reduces every run of
spaces to one, which destroys a table someone aligned so it could be read as a table. Fence
those rather than surrendering them or turning the formatter off:

```python
# fmt: off
CONF_EMAIL         = "email"
CONF_API_KEY       = "api_key"
CONF_REFRESH_TOKEN = "refresh_token"
# fmt: on
```

The fence stops the **formatter only** — `ruff check` still runs inside it, so line length,
import order and unused names are all still caught. What you give up is whitespace
normalisation, which is exactly what you are overriding.

**The fence is statement-level.** One inside a dict or call literal does nothing: ruff
ignores it and collapses the entries anyway. It must wrap the whole enclosing statement, at
that statement's indent, so an aligned keyword-argument call is fenced around the entire
call and a `# fmt: on` never sits at a different indent from its `# fmt: off`.

What earns a fence: padding before `=` or `:`; padding after them, where the values form the
column; padding after `,`; and **one row or record per source line even where nothing is
padded** — glyph rasters, icon bitmaps, colour palettes, layout tables, field-descriptor
lists. That last case is the one that bites: a formatter run turned a 13-line font bitmask
table into 1,194 lines, one pixel per line, and the digit shapes a reader could see in the
source were gone. A flat wrapped list of strings is not a table; leave it to the formatter.

Inside a fence, the house rules are: fence the **smallest statement** that contains the
table, never a class body or a file; one alignment column per block, set one space past the
longest key, spaces only and never tabs; a new block restarts the column; and an entry too
long for the column re-pads the whole block in the same commit. A generator that emits a
fenced table **emits the fence too**, or the next regeneration drops it.

**An exclusion hides drift until the day it is removed.** The stack lints and formats the
whole tree — the `python-validate.yml` bullet under *Implementation notes* in
ha-integration-ci's README says why — and `templates/pyproject.toml` excludes nothing, so
anything a repository has been keeping out of ruff's sight becomes visible the moment it
adopts that file. Before a migration, drop the exclusions and format what they were hiding,
as its own `style:` commit. A migration diff is no place to meet a hundred files for the
first time.

---

## Commit conventions, versioning & CI gating

See **`reference/commits.md`** for commit subjects and titles, **`reference/versioning.md`** for where the version comes from and how an rc and a final are published, and **`reference/github-actions.md`** for what the scaffold carries.

---
