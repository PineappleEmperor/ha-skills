# Scaffolding an integration

What to ask, what to generate, and the conventions the generated code follows. Read with `reference/patterns.md` open — the code patterns live there.

- Gather requirements (ask all at once)
- Files to generate
- Brand assets are served from the integration's own `brand/` folder
- Sources
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
- `custom_components/{domain}/brand/` — the brand assets. **Eight filenames are valid, not
  four**; which of them you actually ship, and the rules every one of them must meet, are
  *Brand assets* below. `icon.png` is the only one HACS hard-requires.

**The CI stack** is copied, never authored — the invariant in `SKILL.md`. Missing files here
are separate audit failures on the first run, so this is not an optional last step. The table in
`reference/github-actions.md` says which files the scaffold carries and where each is
copied from; the caller blocks come from the CI repositories' READMEs with their
`{{sha}} # {{tag}}` tokens resolved, and `panel-bundle.yml` with `frontend/` belongs only
to an integration that serves a panel, per `reference/panels.md`.

### Brand assets are served from the integration's own `brand/` folder

Via the Brands Proxy API, from the HA version recorded in `reference/freshness.md`. The `home-assistant/brands` CDN `custom_integrations/` folder is **legacy** — do not rely on it for new work. The spec the files must meet is still that repository's README, which is the owner of everything in this section; re-derive against it rather than against this summary when the two disagree.

**The eight filenames, and which to ship**

| File | Size | Ship it when |
|---|---|---|
| `icon.png` | exactly 256×256 | always — the only file HACS hard-requires |
| `icon@2x.png` | exactly 512×512 | always — see the HiDPI note below |
| `logo.png` | shortest side 128–256 | always, today — see the gate note below |
| `logo@2x.png` | shortest side 256–512 | as `logo.png` |
| `dark_icon.png` / `dark_icon@2x.png` | as the icons | the icon is unreadable on a dark ground |
| `dark_logo.png` / `dark_logo@2x.png` | as the logos | the logo is unreadable on a dark ground |

> ⚠️ **The audit currently requires all four unprefixed files, whatever the spec allows.**
> `check_brand_assets` in ha-integration-ci's `skill_audit.py` reports `missing …/logo.png`
> and `missing …/logo@2x.png` as failures for any repository without them. So the
> "ship only the icons" case below is correct about the serving behaviour and **would fail
> your own `quality-audit` run**. Until that check learns the fallback, ship all four; the
> gap is a ha-integration-ci change, tracked in this repository's register.

**Serving falls back, so an absent file is not a broken one.** A missing `logo.png` is
served as `icon.png`; a missing `@2x` is served as its 1×; a missing `dark_` file is served
as its non-prefixed match. Two consequences worth knowing, subject to the gate note above:

- **If the logo would be the *same image* as the icon, ship only the icons.** The spec's
  wording is "if the brand uses the same image for the logo and icon"; the icon already
  fills that slot, so a duplicate at `logo.png` is waste. This is about the image, not the
  shape — a *different* square image is still a legitimate logo, since landscape is
  "preferred" and the only hard rule is the shortest-side band. A device whose display is
  square has a square logo, and that is correct. What is never right is padding a mark into
  a landscape canvas to hit an aspect ratio nobody requires.
- **Dark variants are optional and additive.** Ship them only when the light asset genuinely
  fails on a dark ground — a black wordmark does, a two-colour mark usually does not.

**Rules every file must meet**

- PNG, properly compressed and optimised; **lossless** preferred, **interlaced/progressive**
  preferred, **transparency** preferred.
- Where more than one version exists, the one optimised for a **white** background is the
  unprefixed file; the dark-optimised one takes the `dark_` prefix.
- **Trimmed to the subject.** "The image should be trimmed, so it contains the minimum
  amount of empty space on the edges" — borders and transparent padding included. A brand's
  own guidelines often demand clear space around their logo; that rule governs *placement in
  a UI*, not the asset file, and padding it into the PNG breaks this one. Trim, and let
  Home Assistant do the spacing.
- Icons are **1:1** and exactly 256/512 — not a range.
- Logos: landscape preferred, and "aspect ratio should respect the logo of the brand", so
  never stretch to hit a number. The shortest side has a band, and **the maximum of the band
  is preferred** — 256 and 512, not 128 and 256.
- **Home Assistant branding: the spec says no, practice says otherwise — judge it.** The
  brands README says "custom integrations must not use Home Assistant branded images, as
  this might confuse the end-user into thinking that the integration is an internal/official
  integration". That was written as a review rule for PRs into the central repository, and
  **nothing enforces it on an inline `brand/` folder**, which no one reviews. Sampling
  fifteen widely installed custom integrations in 2026-09 found the house-and-node mark in
  use — `localtuya`'s icon is that mark recoloured orange, and it is one of the most
  installed custom integrations there is. So the real line is the stated rationale, not the
  letter: do not dress an integration up as an official one. Using Home Assistant's visual
  language — its blue, a device drawn in it, the node motif as a small element of a mark
  that is plainly your own — is common and uncontroversial. Passing your integration off as
  shipped-with-core is not.
- The marks are their owners'. They are used for identification only and imply no
  endorsement — so reproduce a brand's own artwork rather than deriving a new mark from it,
  and where the brand publishes usage terms, meet them.

> ⚠️ **The HACS store/search dashboard still reads the legacy `data-v2.hacs.xyz` (which mirrors the old brands CDN), NOT the inline `brand/` folder.** So an integration that ships *only* inline brand images — i.e. one that never got a `home-assistant/brands` entry, and now **can't** (brands auto-closes `custom_integrations/*` PRs) — renders **blank in the HACS dashboard** even though HA's own UI shows the icon correctly via the proxy. Integrations with a *legacy* brands entry (added before the Feb-2026 cutoff) keep showing in HACS. This is a HACS-side gap, not a repo defect — nothing to fix in the integration; it resolves when HACS points its dashboard at the proxy (tracked per its row in `reference/freshness.md`). Don't try to "fix" it by PR-ing `home-assistant/brands` (auto-closed).
>
> ⚠️ **Ship the `@2x` variants anyway.** The proxy serves `icon.png` when `icon@2x.png` is
> absent, so this is not the 404 it once was — the 404 case is a plain
> `brands.home-assistant.io/<domain>/icon.png` URL with no `icon.png` at all. What you get
> instead is a HiDPI client rendering a 256px image where it asked for 512, which reads as a
> soft or blurry icon rather than a missing one. Their sizes are exact when present, and an
> off-spec `icon.png` misbehaves on every client.

### Sources

**Prefer a source that scales over a source that is already the right size.** In order: the
brand's own vector (a press kit's EPS/PDF/SVG — render it with ghostscript or `cairosvg` and
scale *down* to every size), then their largest raster, then something generated. Every
target then comes from one master, so the whole set is consistent and nothing is upscaled.
Where only a small raster exists, compose from the crispest part you have — an existing
256×256 icon scaled down beats the same mark cropped out of a 512×157 lockup.

Anything generated is **drawn from named constants in a committed script**, not hand-edited,
with a short `docs/brand.md` recording what the constants mean. That way the set can be
regenerated at a new size or a new colour without redrawing, and a reviewer can see why the
proportions are what they are. A brand with no usable artwork at all still gets this: a
simple mark in the brand's sampled colours, generated, and replaced later if the vendor
supplies one.

A placeholder may start as an SVG rasterised with `cairosvg` (ImageMagick's MSVG renderer botches text) or `convert -background none -density 144 in.svg out.png`. But the asset can equally be a **crisp nearest-neighbour upscale of a real device render** — for a pixel display this is the strongest branding. A device screenshot keeps its black background: that is the device, not a missing alpha channel, and it is not the untrimmed padding the spec forbids. Pick by where HA shows it: the **logo** renders large (integration page / HACS) so a busy/detailed screen reads well; the **icon** renders small (~48px in the integrations list) so use a **simple, low-detail** screen (fewer, fatter pixels survive the shrink) — a full text-heavy screen turns to mush. Generate the PNG straight from the byte-faithful preview (`render_layout_png(..., scale=N)`), not a photo.

> HACS `check-brands` fails if `custom_components/{domain}/brand/icon.png` is absent and the integration is not listed in the HA brands repo.

**HACS validation — 9 checks**

⚠️ All nine must pass; none may be ignored (the `ignore:` input is off-limits — `reference/github-actions.md` has the workflow contract). Fix them here, at scaffold time, since each one maps to a file or a GitHub setting:

| Check | What's needed | Where to fix |
|-------|--------------|--------------|
| `archived` | Repo not archived | GitHub repo settings |
| `brands` | `brand/icon.png` present | File in repo |
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
