# Scaffolding an integration

What to ask, what to generate, and the conventions the generated code follows. Read with `reference/patterns.md` open — the code patterns live there.

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
- `diagnostics.py` (Gold requirement — see `reference/patterns.md`)
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
  (A user may *additionally* wire personal `SessionStart` + `UserPromptSubmit` hooks in their own `~/.claude/settings.json` to re-arm the rule and anchor the CI conventions per-turn — see `reference/github-actions.md` (reminder-hook recipe) for the full recipe. That's a personal convenience; the canonical, shareable enforcement still lives in the repo's `CLAUDE.md`.)
- `hacs.json` — `name` is the only strict requirement, but the canonical setup ships a **zip release**: `{"name": "My Integration", "content_in_root": false, "zip_release": true, "filename": "<domain>.zip"}` (add `"homeassistant": "2024.1.0"` for a minimum HA version). `zip_release` makes HACS download a release **asset** named `<filename>` instead of the tag source archive — so it **requires** the `release.yml` *Create Release ZIP* workflow (`templates/.github/workflows/release.yml`) to build and attach that asset on every published release. **Without that workflow, HACS install fails with `Could not download`** (the symptom of a `zip_release` repo whose release has no attached zip). Drop `zip_release`/`filename` only if you deliberately want HACS to pull the whole tagged repo archive instead.

  > **The tag is the version, not the committed manifest.** `release.yml` rewrites
  > `manifest.json` from the release tag before zipping, so nobody hand-bumps a version
  > in a PR and the asset users install always matches the release they installed it
  > from. The committed value is a placeholder between releases. [frenck/spook](https://github.com/frenck/spook)
  > patches from the same event; `skill_audit.py` fails a `zip_release` repo whose
  > `release.yml` doesn't. Overriding a bump is choosing the tag. This applies to
  > integrations HACS installs as a zip — a repo whose *committed* file is what
  > consumers read (a plugin marketplace, a library) still has to commit the bump.
- `pyproject.toml`
- `pyrightconfig.json`
- `requirements.test.txt` — **required**; `python_validate.yml` installs from it and runs `pytest`, so an integration without it has no test job. Copy `templates/requirements.test.txt`. Pin `pytest-homeassistant-custom-component` to the release matching the HA version in `python_validate.yml` (it tracks HA releases 1:1 — a mismatched pin fails at import, not at test time).
- `conftest.py` — **required, at the repo root, not in `tests/`**; copy `templates/conftest.py`. Its first import claims the name `custom_components` for this repo before `pytest-homeassistant-custom-component` binds it to the package it bundles; without that, HA cannot see the integration and every setup test fails with `Integration not found`. It also pulls in `enable_custom_integrations` autouse. `pyproject.toml` additionally needs `asyncio_mode = "auto"`. Both verified by ablation — full explanation in `reference/patterns.md`, read it before writing the first test.
- `tests/` — one file per module under test, plus `test_manifest_gate.py` and `test_commit_summary.py` (below). See the testing rules in `reference/patterns.md`.
- `README.md` — **include the AI-assistance disclaimer** as a GitHub `> [!NOTE]` admonition box. Link the skill name to its public repo. Template:
  ```markdown
  > [!NOTE]
  > **AI assistance:** I'm a programmer; this project is built with AI (Claude, via Claude Code) for implementation, code review, and QA — under human direction, guided by my [`ha-integration`](https://github.com/PineappleEmperor/pineapple-claude-hacs) skill. Architecture and final review are mine; every change is human-reviewed before it merges.
  ```
- `LICENSE` — the full text of the chosen licence (MIT unless told otherwise), so GitHub
  resolves an SPDX identifier and the HACS `license` check passes.
- `.gitignore` — copy `templates/.gitignore`. Covers `__pycache__/`, caches, venvs, HA dev artefacts (`.storage/`, `home-assistant.log*`, the `_v2.db`), and `device_map.md` (the `ha-log-triage` device map holds a home's IP/device layout and must never be committed). **Not optional:** without it a local `pytest` run plus a `git add -A` commits `.pyc` files, and a `.pyc` under `templates/` is then copied verbatim into every repo scaffolded from the skill. `skill_audit.py` fails on any tracked compiled artefact.
- `.githooks/commit-msg` — copy `templates/hooks/commit-msg`, `chmod +x`. Terse-subject + AI-trailer rejection. **Enable once per clone: `git config core.hooksPath .githooks`** — an unenabled hook is a file, not a guard. Document that line in `CLAUDE.md`.
- `custom_components/{domain}/brand/icon.png` — **256×256**, required by HACS brands validation
- `custom_components/{domain}/brand/icon@2x.png` — **512×512** (see HiDPI note below)
- `custom_components/{domain}/brand/logo.png` — landscape, shortest side **128–256**
- `custom_components/{domain}/brand/logo@2x.png` — landscape, shortest side **256–512**

> **Brand assets are served from the integration's own `brand/` folder since HA 2026.3.0** (via the Brands Proxy API). The `home-assistant/brands` CDN `custom_integrations/` folder is **legacy** — do not rely on it for new work. Files are PNG, lossless; transparent background for wordmark/logo art (an LED-screen/device screenshot keeps its black background — that's the device, not a missing alpha).
>
> ⚠️ **The HACS store/search dashboard still reads the legacy `data-v2.hacs.xyz` (which mirrors the old brands CDN), NOT the inline `brand/` folder.** So an integration that ships *only* inline brand images — i.e. one that never got a `home-assistant/brands` entry, and now **can't** (brands auto-closes `custom_integrations/*` PRs) — renders **blank in the HACS dashboard** even though HA's own UI shows the icon correctly via the proxy. Integrations with a *legacy* brands entry (added before the Feb-2026 cutoff) keep showing in HACS. This is a HACS-side gap, not a repo defect — nothing to fix in the integration; it resolves when HACS points its dashboard at the proxy (tracked in hacs/integration #5171 and #5223). Don't try to "fix" it by PR-ing `home-assistant/brands` (auto-closed).
>
> ⚠️ **Ship the `@2x` variants or the icon flickers/fails on HiDPI.** The most common "icon shows only sometimes" bug is a present `icon.png` with **no `icon@2x.png`**: a Retina/zoomed client requests `@2x`, 404s, and falls back inconsistently. `icon@2x.png` (512²) and `logo@2x.png` are not optional. Exact, square sizes matter — an off-spec `icon.png` (e.g. 384²) also misbehaves.
>
> **Sources:** a placeholder may start as an SVG rasterised with `cairosvg` (ImageMagick's MSVG renderer botches text) or `convert -background none -density 144 in.svg out.png`. But the asset can equally be a **crisp nearest-neighbour upscale of a real device render** — for a pixel display this is the strongest branding. Pick by where HA shows it: the **logo** renders large (integration page / HACS) so a busy/detailed screen reads well; the **icon** renders small (~48px in the integrations list) so use a **simple, low-detail** screen (fewer, fatter pixels survive the shrink) — a full text-heavy screen turns to mush. Generate the PNG straight from the byte-faithful preview (`render_layout_png(..., scale=N)`), not a photo.

> HACS `check-brands` fails if `custom_components/{domain}/brand/icon.png` is absent and the integration is not listed in the HA brands repo.

**HACS validation — 8 checks**

⚠️ All checks must pass without ignoring any — the `ignore:` input in `hacs_validate.yml` exists for debugging only. Ignoring checks disqualifies the repo from the HACS default store.

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
| `license` | An SPDX-identifiable `LICENSE` in the repo | File in repo |

The `description`, `issues`, `topics` and `license` checks fail silently until the first `hacs_validate` run — they're GitHub settings, not files.

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
  "version": "0.1.0"
}
```

`integration_type` is **required** — choose: `device` / `hub` / `service` / `entity` / `hardware` / `helper` / `system` / `virtual`.

`issue_tracker` is **required by HACS validation** — omitting it fails the `integration_manifest` check.

---

## Implementation patterns, file structure, typing & testing

See **`reference/patterns.md`** — `__init__`/coordinator/entity/notify patterns, `entry.runtime_data`, `DeviceInfo`, the modern `NotifyEntity` path, `from __future__ import annotations` + typed-`ConfigEntry` rules, the file-split conventions, and the **mock-the-boundary** testing rules (real setup-entry `LOADED` test, two-entry parallel test, parser unit tests).

---

## Code style

- Module docstring on every file. **This one may be multi-line** — a file-level explanation of a load-bearing constraint belongs here, not demoted to a comment.
- Short **single-line** docstrings on all public functions and classes. Enforced by `skill_audit.py`; module docstrings are exempt.
- No inline comments unless the WHY is genuinely non-obvious
- No trailing summaries after edits
- ruff + pylint compliant; pyright standard mode

---

## Conventional Commits, versioning & CI gating

See **`reference/versioning.md`** — Conventional Commits → semver mapping, the bump discipline that applies where a committed version is what consumers read, the prerelease/rc cycle, the **last-published-release** version gate, Dependabot, and the `GITHUB_TOKEN` workflow-suppression footgun.

---
