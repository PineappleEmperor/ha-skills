---
name: ha-integration
description: Use when developing or troubleshooting a Home Assistant custom integration — Python code under `custom_components/`. Covers building, fixing, or reviewing the integration's backend: config/options/reauth/reconfigure flows, the data coordinator and entity platforms (sensor, switch, notify, fan, etc.), manifest, services, diagnostics, and quality_scale. Reach for it on symptom-style reports too: an entity going unavailable after restart, a notify/custom service breaking after an HA update, a `device_class`/`state_class` mismatch HA complains about, a reconfigure flow request, or CI/Dependabot/HACS/hassfest issues on an integration repo. Also use to read or triage a `home-assistant.log` — finding the real fault among thousands of noisy lines. NOT for Lovelace cards, dashboard/panel UI styling, template sensors in YAML, or generic non-HA Python. Invoke before editing integration code; re-invoke after /compact.
---

# Home Assistant Integration Assistant

Help create, modify, and lint Home Assistant custom integrations targeting **platinum quality scale**.

**Always fetch before coding** — these are the authoritative sources:
- Creating integrations: https://developers.home-assistant.io/docs/creating_integration_index/
- Config entries: https://developers.home-assistant.io/docs/config_entries_index/
- Config flows: https://developers.home-assistant.io/docs/config_entries_config_flow_handler/
- Data fetching + coordinator: https://developers.home-assistant.io/docs/integration_fetching_data/
- Setup failures: https://developers.home-assistant.io/docs/integration_setup_failures/
- Quality scale: https://developers.home-assistant.io/docs/integration_quality_scale_index/
- Real examples: https://github.com/home-assistant/core/tree/dev/homeassistant/components

### Freshness — cached facts and when to re-derive them

Several load-bearing values in this skill are **snapshots**. They were right when captured and go wrong silently: nothing in CI notices, and the check written to catch staleness goes stale in the same place (an "is the pin below v6?" rule keeps passing a v6 pin long after v7 ships — which is exactly what happened to `setup-python`). **Re-derive any row older than ~3 months, and update every listed consumer in the same pass** — a value fixed in one place and not the others is worse than one that's uniformly old.

| Cached fact | Value | Captured | Re-derive with | Consumers to update together |
|---|---|---|---|---|
| HA minimum Python | `3.14` (HA dev needs 3.14.2+) | 2026-06 | developers.home-assistant.io/docs/development_environment | `python_validate.yml` `python-version` · `pyproject.toml` ruff `target-version` + pylint `py-version` · `pyrightconfig.json` — all compared by `scripts/version_sync.py` |
| Quality-scale canonical rule set | see *Quality scale* below | 2026-06 | developers.home-assistant.io/docs/core/integration-quality-scale/ | the rule lists below · every `quality_scale.yaml` |
| GitHub action versions | checkout `v7.0.1` · setup-python `v7.0.0` · setup-node `v7.0.0` · setup-uv `v10.0.1` · action-gh-release `v3.0.2` · semantic-pull-request `v6.1.1` · release-drafter `v7.7.0` · dependency-review `v5.0.0` · stale `v11.0.0` | 2026-08-22 | `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name`, then `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` for the SHA | the SHA pins in `templates/.github/workflows/*.yml`, each with its version in the trailing comment |
| `pytest-homeassistant-custom-component` → HA | `0.13.354` → HA `2026.8.0`, requires-python `>=3.14` | 2026-08-07 | pypi.org/project/pytest-homeassistant-custom-component | `templates/requirements.test.txt` pin · the HA-minimum-Python row above |
| Brand assets served from inline `brand/` | since HA `2026.3.0`; HACS dashboard still reads the legacy CDN | 2026-06 | hacs/integration #5171, #5223 | the brand-assets note in Mode 1 |

`scripts/version_sync.py` runs in `quality_audit.yml` and fails when the Python version
in `python_validate.yml`, ruff's `target-version` and `pyrightconfig.json` disagree, or
when `pytest-homeassistant-custom-component` is unpinned. It compares what is declared;
the table above is still what says which value is current.

`hacs/action@main` and `home-assistant/actions/hassfest@master` are **deliberately** on mutable refs — that's the ref each project documents, and a tag pin stops tracking their validation rules. They're exempt from the pin rules above; the trade-off is capped with read-only permissions and `persist-credentials: false` in both workflows.

## When to use this skill

Use it when the task touches any of: a `custom_components/<domain>/` package, a `manifest.json` with a `domain`, a config/options/reauth/reconfigure flow, a `DataUpdateCoordinator` or entity platform (`sensor.py`, `notify.py`, …), `services.yaml`/`quality_scale.yaml`, the integration's GitHub CI (the `pr-checks`/release-drafter/hassfest/HACS stack), or a Home Assistant log to triage. Symptoms that should pull you here: "add a sensor/platform", "config flow won't validate", "hassfest/HACS check failing", "what `state_class` for this `device_class`", "Dependabot keeps bumping actions", "this PR's release version looks wrong", "what's spamming my HA log".

**When NOT to use:** Home Assistant *panel / display UI* work (Lit/TS web component, CSS, layout) — that's the `ha-panel-design` skill. Generic Python/CI work in a repo that isn't an HA integration.

---

## Step 1 — Detect mode

Check the current working directory:
- No `custom_components/` → default to **Scaffold**
- `custom_components/` exists → ask: **Scaffold** new integration / **Modify** existing / **Lint & quality check** / **Audit** (verify the skill was actually followed — see Mode 4)?
- The task is reading/triaging a **HA log** (a `home-assistant.log`, a Settings → System → Logs download, or a copied log dump) → **Log triage** (Mode 5) — regardless of `custom_components/` presence.

---

## Mode 1 — Scaffold new integration

### Gather requirements (ask all at once)

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

### Files to generate

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
- `.gitignore` — copy `templates/.gitignore`. Covers `__pycache__/`, caches, venvs, HA dev artefacts (`.storage/`, `home-assistant.log*`, the `_v2.db`), and `device_map.md` (the Mode 5 log-triage map holds a home's IP/device layout and must never be committed). **Not optional:** without it a local `pytest` run plus a `git add -A` commits `.pyc` files, and a `.pyc` under `templates/` is then copied verbatim into every repo scaffolded from the skill. `skill_audit.py` fails on any tracked compiled artefact.
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

#### `RELEASE_TOKEN` — set this up before the first release

⚠️ **One secret, once per repo, or `auto_draft_pr.yml` cannot open a PR that checks can
run on.** GitHub suppresses workflow events caused by `GITHUB_TOKEN`, so a PR opened with
it fires no `pull_request_target`: no checks run, the required ones never report, and the
PR is permanently unmergeable. That is how `create-dev-pr.yml` was removed. The opener fails
loudly instead, and `skill_audit.py` fails a repo that ships it without the secret.

The **release** path needs no token: both the full release and its next rc are kept as
drafts, and publishing a draft is a human action, so its events fire normally.

**Two ways to provide it. Pick by how many repos you maintain.**

**A GitHub App (preferred for more than one repo).** An App is installed once and then
covers every repo you install it on, its tokens are minted per run and expire in an hour,
and it survives you rotating your own credentials. Events it causes DO trigger workflows,
which is the whole requirement.

1. github.com → Settings → Developer settings → GitHub Apps → **New GitHub App**
2. Name it (e.g. `<you>-release-bot`), untick **Webhook → Active**
3. **Repository permissions**: `Contents: Read and write`, plus `Pull requests: Read and
   write` if you use `auto_draft_pr.yml` — nothing else
4. Create it, note the **App ID**, then **Generate a private key** (downloads a `.pem`)
5. Install it: the App's page → **Install App** → pick the repos
6. In each repo: Settings → **Secrets and variables** → **Actions** → **Secrets** tab →
   **New repository secret** → `APP_ID` (the numeric ID), then again for `APP_PRIVATE_KEY`
   (the whole `.pem` contents, including the BEGIN/END lines) → **Add secret**
7. In `auto_draft_pr.yml`, mint the token before the step that needs it:
   ```yaml
   - uses: actions/create-github-app-token@v2
     id: app-token
     with:
       app-id: ${{ secrets.APP_ID }}
       private-key: ${{ secrets.APP_PRIVATE_KEY }}
   # then use ${{ steps.app-token.outputs.token }} wherever RELEASE_TOKEN appears
   ```

**A fine-grained PAT (fine for a single repo).** Simpler, but tied to your account and it
expires on a date you have to remember.

1. github.com → Settings → Developer settings → Personal access tokens →
   **Fine-grained tokens** → **Generate new token**
2. **Resource owner**: your account · **Repository access**: Only select repositories →
   this repo
3. **Repository permissions**: `Contents: Read and write`, plus `Pull requests: Read and
   write` if you use `auto_draft_pr.yml` — nothing else. (`Metadata: Read` is added
   automatically and cannot be removed.)
4. **Expiration**: 90 days or less
5. **Generate token**, copy the `github_pat_…` value — it is shown once
6. Repo → **Settings** → **Secrets and variables** → **Actions** → **Secrets** tab →
   **New repository secret** → Name `RELEASE_TOKEN`, paste into **Secret** → **Add secret**

**What the grant actually allows.** `Contents: write` covers creating releases, tags and
commits in the repos it is scoped to. Adding `Pull requests: write` lets it open the
draft PR — and, unavoidably, merge one, since GitHub does not separate those. Neither
permission can edit rulesets or branch protection, change repository settings, or reach
any repo outside its scope, so a required-checks ruleset still holds.

Without `Pull requests: write`, `auto_draft_pr.yml` fails with
`Resource not accessible by personal access token (repository.pullRequests)`. That
matters because this token exists to *trigger* workflows — anything it can do, a workflow
it starts can do too.

**Rotating.** Paste a new value into the same secret; nothing else changes. An App's
private key is rotated the same way, and its tokens expire hourly regardless.


#### Make the checks REQUIRED — a workflow is not a gate until it can block a merge

> **A cancelled check blocks; a skipped one does not.** GitHub is explicit that a
> skipped job satisfies a required check, so job-level `if:` guards are fine.
> Cancelled runs are the hazard. Trigger on `labeled`/`unlabeled` with
> `cancel-in-progress` and a bot applying several labels at once starts a run per
> label; the concurrency group cancels all but the last, and those cancelled
> check-runs make the rollup `FAILURE` with nothing broken. The PR then reports
> `mergeable: MERGEABLE` and still cannot merge. Drop those two types: the
> in-workflow autolabeler cannot fire them anyway, because the default token
> suppresses events it causes.
>
> Confirmed by re-running a single cancelled run on ha-lego #22: the rollup went
> from `FAILURE` to `SUCCESS` with nothing else changed.

> **A matrix renames the check.** GitHub names a matrix job's check-run
> `<job> (<value>)`, so a job `Ruff, Pyright and Pytest` with `python-version: ["3.14"]`
> reports as `lint-and-type (3.14)` and a ruleset requiring the bare name waits
> forever. `templates/ruleset.json` shipped exactly this bug. Either drop a
> single-value matrix or put the suffixed name in the ruleset; never assume the
> context equals the job name.

**`scripts/bootstrap_repo.sh` does all of this once**, from the repo root after the first
push: description, topics, issues, the ruleset, `core.hooksPath`, and the `RELEASE_TOKEN`
secret (prompted, never an argument). Every item in it is a GitHub-side setting no file in
the repo can carry, and each fails quietly until the first CI run.

```bash
bash scripts/bootstrap_repo.sh "One-line description of the integration"
```

**A gate that cannot fail is not a gate.** `Version validation` skips its own steps in a
tag-driven repo, so requiring it there guarantees a green check that proves nothing — it
is not in `ruleset.json`. What it still does is useful and advisory: it writes the version
the PR's labels imply into the job summary, where the checks tab shows it.

**Two kinds of workflow, and only one is a gate.** A *check* runs on a pull request and can
be required, so a red one blocks the merge — `CC labelling`, `CC label validation`,
`Version validation`, `CC title validation`, `HACS validation`,
`Hassfest manifest validation`, `Ruff, Pyright and Pytest`, and
`ha-integration conformance check`. Everything else — `Auto draft PR`, `Auto release zip`,
`Auto draft releases`, `Panel bundle staleness check` — is process automation firing on
pushes and releases. It is not a weaker check; it is not a check at all, and requiring one
would block every PR on a context that never reports.

⚠️ **Every workflow here is advisory by default.** GitHub will let a PR merge with all of it red, so without this step the gate stack is decorative. Copy `templates/ruleset.json` and apply it once:

```bash
gh api -X POST repos/<owner>/<repo>/rulesets --input ruleset.json
```

It requires the nine job-name contexts the templates produce and keeps deletions and force-pushes blocked. `skill_audit.py` FAILs a repo whose default branch has no required checks, so skipping this shows up rather than going unnoticed.

Two ways to get it wrong, both of which block every PR permanently:

- **A context that never reports.** Requiring a check the repo doesn't produce (a repo without `quality_audit.yml` must drop `ha-integration conformance check`) leaves PRs waiting for a check that will never run.
- **A path-filtered workflow.** `build` from `frontend_build.yml` is deliberately absent for this reason: it only triggers on `frontend/` changes, so requiring it would block every unrelated PR.

⚠️ **`bypass_actors` must stay empty to mean anything.** A ruleset granting admins `bypass_mode: always` does not constrain anyone holding admin; the push reports `Bypassed rule violations` and proceeds. Overrule deliberately instead: set the ruleset's enforcement to `disabled`, merge, set it back, which leaves an audit-log entry.

> **For AI sessions.** An agent running with your `gh` credentials merges exactly as you do, and `bypass_actors` is evaluated by actor, so any bypass you hold it inherits. Two things make that silent: a broad allow-rule such as `Bash(gh pr *)` in `.claude/settings.local.json` pre-approves `gh pr merge` with no prompt, and an agent with admin can lift any rule it can see. Narrow the allow-rule to read-only verbs (`gh pr view`, `gh pr list`), and give the agent a credential without **Administration** if it genuinely should not edit rulesets or force-push. A restriction the agent can lift is friction, not a limit.

#### Supply chain

Two cheap workflows ship with the stack. `dependency_review.yml` fails a PR that adds a
dependency with a high-severity advisory, reading the PR's own diff. `stale.yml` labels
issues and PRs untouched for 60 days and **never closes them** (`days-before-close: -1`)
— a closed report is a lost report.

Actions are pinned by commit SHA with the version in a trailing comment, because a tag
is mutable — whoever owns the action can repoint it at new code, which then runs with the
workflow's token. Dependabot updates both the SHA and the comment, and `skill_audit.py`
fails a workflow that uses a bare tag or a SHA with nothing saying what it is.

⚠️ **Dependabot cannot see `templates/`.** Its `github-actions` ecosystem only scans
`.github/workflows` at the repo root, so the pins this skill *ships* are never bumped for
you. `skill_audit.py` compares them against this repo's own pins — which Dependabot does
update — and fails when the templates fall behind.

#### Panel integrations (a custom panel served by the integration)

Only if the integration registers a panel. Three things are non-obvious and each fails silently.

**1. The bundle must be committed.** HACS ships the repo as-is and runs no build step on the user's machine, so the esbuild output has to live inside `custom_components/<domain>/panel/` to reach the release zip. A stale bundle then breaks *invisibly*: the old bundle still runs, tests pass, CI is green, and the only symptom is "the fix I made isn't there". Copy `templates/frontend/{package.json,tsconfig.json}` and `templates/.github/workflows/frontend_build.yml`; the workflow's `git diff --exit-code` on the bundle is the point of the whole file. **This differs from a Lovelace *card* repo**, which attaches the built `.js` as a release asset — an integration cannot, because the asset isn't in the zip HACS installs.

**2. `home-assistant-frontend` must be pinned in `requirements.test.txt`.** A panel declares `frontend` (usually `panel_custom` too) in manifest `dependencies`. The frontend *component* has its own pip requirement that `pip install homeassistant` does **not** pull in — component requirements are installed by HA at runtime. Without the pin every setup test fails in CI with `No module named 'hass_frontend'`, while typically **passing locally** because a dev machine already has the package. Worse, the failures read as `'MockConfigEntry' object has no attribute 'runtime_data'`, pointing at the integration rather than the missing dependency. Pin from **core's own manifest** for your HA version, not from PyPI latest:
```bash
curl -s https://raw.githubusercontent.com/home-assistant/core/<ha-version>/homeassistant/components/frontend/manifest.json
```
Gate-enforced: a manifest depending on `frontend`/`panel_custom` with no pin fails the audit.

**3. Registration has two traps.** Cache-bust the module URL or a browser serves the previous panel after an update, and claim the registered flag **before** the `await` or two entries setting up in parallel both register:
```python
if not hass.data.get(REGISTERED):
    hass.data[REGISTERED] = True          # claim BEFORE the await
    integration = await async_get_integration(hass, DOMAIN)
    await panel_custom.async_register_panel(
        hass, ...,
        module_url=f"{PANEL_MODULE_URL}?v={integration.version}",   # or the browser caches
    )
```

**4. Testability is a design property, not a tooling one.** A panel transforms vendor data
before drawing it, and that logic is reachable from nothing else in the stack: `tsc --noEmit`
proves a helper returns a string, not that it returns the right one; the Python suite cannot
see it; and the bundle-staleness check proves the JS matches its source, not that the source
is correct. So **export the pure presentation helpers** rather than inlining them in
`render()` — a panel that inlines everything has nothing to import, and no test runner fixes
that.

```ts
// panel.ts — exported, so a test can reach them
export function isNamed(item: Pick<Set, "name">): boolean { ... }
export function displayName(item: Pick<Set, "name">): string { ... }   // "{?}" -> "Name tbd"
```

The cases worth testing are the ones where the vendor's data is not what you would draw:
a placeholder standing in for an unannounced name, a missing price, a date that has already
passed, a sort comparator, a unit formatter. `templates/frontend/package.json` ships
`vitest` and a `test` script for this; it needs no config file, since vitest's default
include pattern already picks up `frontend/test/*.test.ts`. The runner never reaches users:
`release.yml` zips `custom_components/<domain>/` only, so `frontend/` is CI-time weight and
nothing more.

The same reasoning applies to anything the panel sends. A service call built in TypeScript
against a schema declared in Python has no shared definition and no compiler to link them —
`callService` takes `Record<string, unknown>`, so omitting a `vol.Required` field type-checks
cleanly and fails only at runtime, in the browser, where nobody is watching. A test that
captures the outgoing call and asserts its shape is the only thing that catches it.

> **Panel *styling* — sizing, type, colour, spacing — is the `ha-panel-design` skill, not this one.** This section covers only how the TypeScript reaches the user and how the integration registers it.

#### GitHub CI templates

The full, self-contained CI stack ships in the skill's **`templates/`** dir (mirrors the target repo layout — `templates/.github/workflows/*.yml`, `templates/.github/*.yml`, `templates/scripts/*`, `templates/tests/*`, `templates/hooks/*`). Copy as-is; no external repo. One file per workflow/config/script.

##### Where `templates/` lives, and what to do if you can't find it

`templates/` sits **next to the `SKILL.md` you are reading**, in this skill's own directory. Resolve it in this order:

1. **The base directory announced when this skill loaded.** Invoking a skill prints `Base directory for this skill: <path>` — `templates/` is `<path>/templates/`. Use this first; it is always correct.
2. **Installed as a plugin:** `~/.claude/plugins/cache/*/ha/*/skills/ha-integration/templates/`
3. **Personal or repo skill:** `~/.claude/skills/ha-integration/templates/`, or `plugins/ha/skills/ha-integration/templates/` inside a checkout of the skill repo.
4. **Last resort — search:** `find ~/.claude ~/.agents . -type d -path '*ha-integration/templates' 2>/dev/null`

**If none of those find it, stop and say so.** Report which paths you checked and ask for the skill's location. Do **not** author the workflows, `skill_audit.py`, `manifest_gate.py`, `dependabot.yml`, `release-drafter.yml` or `pr-checks.yml` from this document — the prose *describes* the templates, it does not *replace* them. A hand-written CI stack passes a hand-written audit, and every divergence stays invisible until something breaks in production.

##### Copying the templates

For each canonical file: read the template, write it to the target path byte-for-byte, then apply **only** the substitutions listed below. Do not reformat, reorder keys, rename jobs, add comments, or "improve" a copied file.

**Sanctioned adaptations — the complete list. Any other difference is drift:**

| File | Allowed change |
|---|---|
| `.github/workflows/release.yml` | `<domain>` → the integration's domain (3 occurrences) |
| `.github/workflows/python_validate.yml` | `python-version`, **only** when HA's minimum Python has moved and the template is stale — fix the template too |
| lint/format config (`pyproject.toml`, ruff) | exclusions needed to leave copied files unformatted |

**Traps this section exists to close** (both have happened, with the reminder hook active and the agent believing it was complying):

- **Writing a faithful-sounding paraphrase instead of copying the artefact.** Producing a workflow that does what the prose says is *not* copying the template. Fifteen files drifted this way and passed the audit clean.
- **Multi-line docstrings.** The code style below says *short single-line* docstrings on all public functions and classes. Single line means single line.

#### Workflows orchestrate; scripts decide

A `run:` block may invoke a tool, pass data between steps, and guard on one condition.
Anything that classifies, compares, or computes a value belongs in `scripts/`, where it
has unit tests — logic inside a workflow can only be tested by running CI, so its first
failure is a real PR. If a change to a template workflow needs a `case`, a loop, or a
regex, write it in Python first and call it from the step.

These templates are a dependency other repos inherit, so they are held to that standard
even where a repo's own one-off workflow would not be.

**Read `reference/github-actions.md` before changing any workflow** — it holds the must-preserve behaviours: the sole title-only labeler + removal-only superseded-label step, `$BODY` + bounded Dependabot `replacers`, the last-published-release version gate (with `dependabot[bot]` exempt and the unit-tested `manifest_gate.py`), the `pr-checks` job ordering, its `pull_request_target` safety rules and the marked-block contract, and the optional personal reminder-hook recipe.

---

### manifest.json key order

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

### Implementation patterns, file structure, typing & testing

See **`reference/patterns.md`** — `__init__`/coordinator/entity/notify patterns, `entry.runtime_data`, `DeviceInfo`, the modern `NotifyEntity` path, `from __future__ import annotations` + typed-`ConfigEntry` rules, the file-split conventions, and the **mock-the-boundary** testing rules (real setup-entry `LOADED` test, two-entry parallel test, parser unit tests).

---

### Quality scale — target Platinum

Generate `quality_scale.yaml` with each rule set to `todo` or `done` as appropriate.

| Tier | Key requirements |
|------|-----------------|
| 🥉 Bronze | UI setup, basic coding standards, automated tests for config, basic docs |
| 🥈 Silver | + code owners, auto-recovery from errors without log spam, reauth flow (`async_step_reauth`) |
| 🥇 Gold | + auto-discovery, full translations, reconfigure flow (`async_step_reconfigure`), diagnostics, full test coverage |
| 🏆 Platinum | + complete type annotations, fully async (no blocking I/O), `always_update=False` where applicable, all HA coding standards |

Note: `PlatformNotReady` is for legacy `async_setup_platform` only — config-entry integrations use `ConfigEntryNotReady` instead.

`quality_scale.yaml` format:
```yaml
rules:
  config_flow: done
  test_coverage: done
  diagnostics:
    status: exempt
    comment: Device exposes no sensitive runtime data worth redacting.
```
Valid statuses: `done`, `todo`, `exempt` (exempt requires a `comment`).

**Scaffold `quality_scale.yaml` from the start** (even in Mode 2 on an existing integration that lacks it) and treat it as the definition-of-done — don't discover rules by hitting them. **hassfest gotchas:** the file must list **every** canonical rule with a valid status, `exempt` **must** carry a `comment`, and **only add `"quality_scale": "<tier>"` to `manifest.json` once every rule up to that tier is `done`/`exempt`** — claiming a tier makes hassfest enforce it (a single `todo` at/below that tier fails CI). So: ship the yaml as a tracking ledger first, omit the manifest tier until a tier is fully met.

**Gate-enforced, on the claim rather than on the tests.** `skill_audit.py` stays silent when nothing is marked `done` — a fresh scaffold claims nothing, so it has nothing to prove — and **fails** when any rule is `done` with no `tests/`, or when `test-coverage` is `done` while a `frontend/` panel has no tests of its own. `exempt` with a comment is always the honest alternative; `todo` is fine indefinitely.

⚠️ **Prove the rule, don't just claim it — hassfest checks structure, not behaviour.** A green hassfest + a `done` in `quality_scale.yaml` only proves the file is well-formed and the manifest tier is a valid enum; hassfest **never runs the integration**, so it cannot tell you `diagnostics.py` actually redacts, the reconfigure flow works, `async_remove_config_entry_device` returns correctly, or that a `translation_key` used in code resolves in `strings.json`. (For HA core those rules are enforced by human reviewers; for a custom integration nothing enforces them.) So **every rule you mark `done` must have a test that exercises it** — marking `done` off code-presence alone is "claiming compliance" without showing it. Concretely, each of these needs its own test, not just the code: `reconfiguration-flow` (a reconfigure-success + reconfigure-error flow test), `diagnostics` (asserts the payload shape **and** that secrets are `**REDACTED**`), `stale-devices` (`async_remove_config_entry_device` → `False` while the device is live, `True` once it's gone), `exception-translations`/`entity-translations`/`icon-translations` (a test that scrapes the `translation_key`s used in code and asserts each exists in `strings.json` — catches a typo'd key that hassfest passes). If a rule is genuinely untestable, it should be `exempt` with a comment, not an unproven `done`.

**Canonical rule set — a snapshot; rules change. Re-verify per the *Freshness* table at the top of this skill.** All must appear in `quality_scale.yaml`:
- **Bronze:** `action-setup`, `appropriate-polling`, `brands`, `common-modules`, `config-flow-test-coverage`, `config-flow`, `dependency-transparency`, `docs-actions`, `docs-high-level-description`, `docs-installation-instructions`, `docs-removal-instructions`, `entity-event-setup`, `entity-unique-id`, `has-entity-name`, `runtime-data`, `test-before-configure`, `test-before-setup`, `unique-config-entry`
- **Silver:** `config-entry-unloading`, `log-when-unavailable`, `entity-unavailable`, `action-exceptions`, `reauthentication-flow`, `parallel-updates`, `test-coverage`, `integration-owner`, `docs-installation-parameters`, `docs-configuration-parameters`
- **Gold:** `entity-translations`, `entity-device-class`, `devices`, `entity-category`, `entity-disabled-by-default`, `discovery`, `stale-devices`, `diagnostics`, `exception-translations`, `icon-translations`, `reconfiguration-flow`, `dynamic-devices`, `discovery-update-info`, `repair-issues`, `docs-use-cases`, `docs-supported-devices`, `docs-supported-functions`, `docs-data-update`, `docs-known-limitations`, `docs-troubleshooting`, `docs-examples`
- **Platinum:** `async-dependency`, `inject-websession`, `strict-typing`

Common `exempt`s for a local-push MQTT device integration: `appropriate-polling` (push, no polling), `reauthentication-flow` (no integration-level auth), `inject-websession` (no cloud HTTP), `async-dependency` (only sync libs run in executor), `dynamic-devices` (one device per entry).

---

### Code style

- Module docstring on every file. **This one may be multi-line** — a file-level explanation of a load-bearing constraint belongs here, not demoted to a comment.
- Short **single-line** docstrings on all public functions and classes. Enforced by `skill_audit.py`; module docstrings are exempt.
- No inline comments unless the WHY is genuinely non-obvious
- No trailing summaries after edits
- ruff + pylint compliant; pyright standard mode

---

### Conventional Commits, versioning & CI gating

See **`reference/versioning.md`** — Conventional Commits → semver mapping, the bump discipline that applies where a committed version is what consumers read, the prerelease/rc cycle, the **last-published-release** version gate, Dependabot, and the `GITHUB_TOKEN` workflow-suppression footgun.

---

## PR discipline — the commit subjects are the changelog

**The release notes are built from the commits, not from the PR body.** `scripts/release_notes.py` classifies each subject and groups it; `auto_draft_pr.yml` opens the draft with an empty body. So a body is optional context for reviewers, and writing the changelog into it just says the same thing twice, in a place users never read.

Reasoning, alternatives, verification evidence: those go in the PR **conversation**, where reviewers read them and the notes do not.

| Excuse | Reality |
|---|---|
| "This change is complex, it needs explaining" | Then it needs splitting, or better commit subjects. The subjects are the changelog. |
| "Reviewers need the reasoning" | Reviewers read the conversation. What users get is the commit subjects, so put the change in those. |
| "The verification belongs with the change" | It belongs in a comment. A description is not a lab notebook. |
| "I wrapped it in `<details>` so it's stripped" | The fold is for Dependabot's own output, not a licence to write an essay. |
| "It's only a few paragraphs" | Measured across eight PRs it was 2,728 words, all republished under the repo owner's byline. |

### Red flags — stop

- Typing prose into `gh pr create --body`
- Reaching for `<details>` in a PR description
- A description longer than its diff is interesting
- Explaining *why* anywhere the commit subjects should have said it

**All of these mean: put it in a comment, or fix the commit subjects.**

> **Observed.** This rule already existed, as "keep two or three sentences of summary at the top of the PR body". It was read and ignored across eight consecutive PRs in this skill's own repo. The author was unaware until they read one of their own PRs. Guidance that exists and is skipped needs a prohibition, not a clearer sentence.

---

## Merge discipline — never merge a red check

**A failing check is the gate working. Merging past it is not a judgement call.**

Violating the letter of this rule is violating the spirit of it. The gate stack in this skill exists to stop bad merges; an agent that reasons its way past a red check has removed the only thing standing between a mistake and `main`.

**One exception, and it is narrow.** A `pull_request_target` workflow loads its definition from the **base** branch, so a PR fixing that workflow is always checked by the broken copy and can never go green on its own. That is the only sanctioned case. It covers **one job, on one PR, whose own definition the PR changes**. To use it you must first prove it with a diff (`git show origin/main:.github/workflows/pr-checks.yml` against the branch's), say in the PR that the failure is the bug being fixed, and verify on the next PR.

| Excuse | Reality |
|---|---|
| "I understand why it's red" | Understanding a failure is a reason to fix it, not to merge it. |
| "The content is correct, only the check is wrong" | Then fix the check. A wrong check is a defect, not an exemption. |
| "It's the `pull_request_target` self-validation case" | Prove it with the diff, on that job, on that PR. If you did not check, it is not that case. |
| "I merged past a red check earlier for a good reason" | That merge carried its own proof. This one needs its own. Precedent is not evidence. |
| "The version/label/content is right anyway" | The gate said otherwise. It is reporting what it can see; if it is wrong about that, say why in writing before merging. |
| "It's only advisory, GitHub let me" | Advisory is a repo-configuration accident, not permission. See *Make the checks REQUIRED*. |
| "Re-running it would waste minutes" | Minutes against a bad merge on `main`. |

### Red flags — stop

- About to run `gh pr merge` while any check is red
- Diagnosing a failure **after** merging rather than before
- Reusing a previous exception without re-deriving why it applies
- Reaching for `--admin`, `--force`, or a `bypass_actors` entry to get a merge through
- Telling yourself the failure is "unrelated" without having read the log

**All of these mean: stop, read the log, fix or explain in writing first.**

> **Observed.** This rule exists because it was broken in this skill's own repo. The `pull_request_target` exception was written, then reused a few hours later on a PR it did not cover: the version gate had correctly failed because the PR carried no label, and the merge went through with the failure undiagnosed. Two conditions made it silent — an allow-rule of `Bash(gh pr *)` pre-approving `gh pr merge`, and no required status checks on the branch.

---

## Debugging discipline

- **Trace before naming a cause** — grep the path (publish → subscribe → handler), confirm in code; a pre-trace hunch is a guess, not the diagnosis.
- **Multi-entry service fan-out:** a `hass.services.async_call(DOMAIN, svc, …)` with no target loops **all** config entries. An entity action that should hit only its own device must pass its own `entry_id`/`device_id` and the handler must filter — default to "all" only for a deliberate bulk call.

---

## Mode 2 — Modify existing integration

Identify the integration domain from `custom_components/`. Then ask what to add or change:

- Add new platform
- Add/update translations
- Add options flow
- Add reconfigure flow (`async_step_reconfigure`)
- Add reauth flow (`async_step_reauth`)
- Add or update `quality_scale.yaml`
- Add GitHub workflows
- Cut a release (publish the rc draft, then the full one)
- Other

Apply the same patterns and code style as Mode 1.

---

## Mode 3 — Lint & quality check

1. Run `ruff check custom_components/` — fix all actionable issues; suppress intentional ones with `# noqa` and a reason
2. Run `python -m pyright custom_components/` — fix all actionable issues
3. Check `quality_scale.yaml` exists; if not, offer to create it
4. Check `manifest.json` — correct `documentation` URL pointing to the repo, keys in order (`domain`, `name`, then alphabetical)
5. Report: files changed · issues fixed · issues intentionally suppressed (with rationale) · remaining manual work

---

## Mode 4 — Audit (skill conformance)

**Why this is separate from lint.** Mode 3 (lint) answers *is the code hygienic* — ruff/pyright/manifest order, tool-driven. Mode 4 answers *was this skill actually followed* — are the canonical workflows present and correct, the documented patterns applied, the antipatterns gone, `quality_scale.yaml` honest. The skill has repeatedly been *used* while specific items were missed (stale action pins, a deprecated notify path, an optimistic `exempt`, a hand-created PR). Lint can't catch those; the audit does. **Run it before claiming a tier and before merge — it's part of definition-of-done.**

**Two layers, because a checklist you must remember to run gets skipped:**
1. **Mechanical gate (`scripts/skill_audit.py`, enforced by `quality_audit.yml` on every PR).** Greps the high-confidence, machine-checkable subset and fails CI on any violation. This is what *stops* regressions — it can't be forgotten.
2. **Judgement checklist (below).** The items a grep can't decide — run these by reading the code.

### Mechanical gate — `scripts/skill_audit.py`

The full script is **`templates/scripts/skill_audit.py`** (copy to `scripts/`, `chmod +x`). It ships 29 checks and `scripts/skill_audit.py --list` prints every one with its rationale — read that rather than a list here, which goes stale the moment a check changes (this section once described version-floor pin checks for months after SHA pinning replaced them). Broadly: the canonical workflows exist and are wired to the scripts they call, actions are pinned to commit SHAs, `custom_components/` is free of the deprecated APIs, `quality_scale.yaml` is honest, and a `tests/` dir CI cannot install fails. Keep its rules in lockstep with this skill — when you add an antipattern or canonical workflow here, add the check there.

⚠️ **The gate checks each canonical workflow *exists*, not that it *matches* the template** — a consuming repo has no copy of `templates/` to diff against. Content fidelity is the first item of the judgement checklist below, where the agent *does* have the skill on disk. Green CI is not evidence the templates were copied.

Enforce it in CI with **`templates/.github/workflows/quality_audit.yml`** — runs `scripts/skill_audit.py` on every PR, so conformance can't be silently skipped.

Add `"scripts/*" = ["T20", "INP001"]` to ruff `per-file-ignores` — the audit and its helpers print, and are not a package. When the skill adds a new antipattern or canonical workflow, **add the matching check here** — the gate is only as current as its rules.

### Judgement checklist (read the code — a grep can't decide these)

- **Templates copied, not paraphrased.** Diff `.github/` and `scripts/` against this skill's `templates/` (locate it per *Where `templates/` lives* in Mode 1). Every difference must appear in the sanctioned-adaptations table there. Files that merely *look* equivalent are not equivalent — `skill_audit.py` checks each canonical workflow **exists**, never that it **matches**, so fifteen hand-written files once passed it clean. Run:
  ```bash
  T=<skill>/templates   # from the skill's announced base directory
  diff -ru "$T/.github" .github
  diff -ru "$T/scripts" scripts
  diff -u  "$T/tests/test_manifest_gate.py" tests/test_manifest_gate.py
  ```
  Expected output is the `release.yml` `<domain>` substitution and nothing else. Any other hunk is a finding — report it with the file and hunk, and restore from the template unless the diff is a deliberate, listed adaptation. If `templates/` can't be located, report the audit item as **not checked**; do not mark it passed.
- **Workflows behave, not just exist:** `pr-checks` runs on `pull_request_target`; `title-check` declares `needs: label`, and `version-gate` skips itself where the release tag sets the version; no job checks out the PR head (the version gate pins `base.sha` and reads the PR manifest over the API); no `${{ }}` appears inside any `run:`; bot authors are skipped; the only workflows opening PRs are `auto_draft_pr.yml` (draft-only, gated on `github.actor == github.repository_owner`) and `update_manifest_floors.yml`; `release_drafter` is push-only with no second autolabeler; the version gate compares to the **last published release** and exempts `dependabot[bot]` on the *failing steps*, and is advisory in a tag-driven repo.
- **Patterns applied:** `runtime_data` (not `hass.data[DOMAIN][entry_id]`) for entry state; coordinator `async_shutdown()` on unload; `async_remove_config_entry_device` present if the integration creates a device; `DeviceInfo` TypedDict; `_attr_has_entity_name = True`; typed `ConfigEntry` alias; modern `NotifyEntity` (or a directly-registered service for custom `data`).
- **`quality_scale.yaml` honest:** every canonical rule listed; every `exempt` carries a real `comment`; no optimistic `exempt` masking a gap (e.g. `stale-devices` exempt while a device *is* created); the `manifest.json` tier claimed only when every rule at/below it is `done`/`exempt`.
- **Tests mock the boundary:** a real setup-entry `LOADED` test exists (not just `async_setup_component`); the transport is mocked, not the integration's own functions; a two-entry parallel `LOADED` test exists if multiple devices are allowed; parsers have unit tests.
- **Commit/PR discipline:** subjects are single tight imperatives; the PR title uses a **labellable** type (`feat|fix|chore|docs`, `!` for breaking) — typed by a human, or derived from the commits by `auto_draft_pr.yml`; in an integration the release tag sets the version and no PR carries a bump, while a repo whose committed file is what consumers read bumps once, as the last commit.
- **Cached facts still true.** Re-derive any row in the **Freshness** table (top of this skill) captured more than ~3 months ago, using the command in its *Re-derive with* column. Report each as still-current or stale-with-the-new-value, and update every consumer listed on that row in one pass. The stale-pin patterns in `skill_audit.py` are themselves a cached fact — check them against the action majors, not just the templates against the patterns.

**Report:** per-item pass/fail with `file:line` evidence · what the mechanical gate caught · remaining manual work. Fix findings before claiming the tier.

---

## Mode 5 — Log triage

Triage a Home Assistant log (`home-assistant.log`, a copied `.md`/`.txt` dump, or the **Settings → System → Logs** download). Goal: turn thousands of lines into a short ranked list of *actionable* issues, separating real bugs from the constant background noise HA emits. **A raw error count is meaningless** — one slow client can emit 1000+ identical lines; one config typo emits one. Rank by distinct root cause, not by line count.

### Step 1 — Build (or load) the device inventory FIRST

Logs identify clients/devices by **opaque tokens** — an IP, a browser user-agent, a Z-Wave `node_id`, a `notify.mobile_app_*` slug, a UniFi/camera hostname. Triage stalls every time on "what *is* `192.168.1.42`?". Resolve it **once**, up front, into a persistent map so every future triage is instant.

**The map is user/environment-specific — it does NOT belong in this (shareable) skill repo.** Keep it in a **local, git-ignored file next to the logs** (e.g. `device_map.md` in the log directory) or in Claude auto-memory. Never commit a home's IP/device layout to a public repo.

**Up-front Q&A** — when no map exists, extract the distinct tokens from the log and ask the user to name each once:

```bash
# Web/app clients: IP + device fingerprint (SM-X210 = Galaxy Tab, KFTRPWI = Amazon Fire, etc.)
grep -oE "from [0-9.]+ \(Mozilla[^)]*Build/[^ ;]+" LOG | sort -u
# All LAN IPs by frequency
grep -oE "192\.168\.[0-9]+\.[0-9]+" LOG | sort | uniq -c | sort -rn
# Named device tokens worth resolving
grep -oE "mobile_app_[a-z0-9_]+|node_id=[0-9]+|notify\.[a-z0-9_]+" LOG | sort | uniq -c | sort -rn
```

Then ask the user to fill **device · room/owner · role** for each token. Store as a table:

```markdown
| Token | Device | Room / owner | Role |
|-------|--------|--------------|------|
| 192.168.1.42 (SM-X210) | Android tablet | Kitchen | Wall dashboard |
| node_id=3 | Z-Wave keypad | Front door | Alarmo front pinpad |
| notify.mobile_app_pixel | Phone | (owner) | Alarm notifications |
```

Decode common fingerprints without asking: `SM-*` = Samsung Galaxy (Tab/phone), `KF*`/`Build/PS*` = Amazon Fire, `Pixel*` = Google Pixel, `iPad`/`iPhone` = Apple. Ask only for room/role.

### Step 2 — Aggregate by logger, not by line

```bash
grep -oE "(ERROR|WARNING) \([^)]+\) \[[^]]+\]" LOG | sort | uniq -c | sort -rn
```

Collapse each logger cluster to one row. Then read **one representative line** per cluster — not all of them.

### Step 3 — Classify each cluster: noise vs actionable

**Known noise — acknowledge once, do not chase:**

| Pattern | Why it's noise |
|---------|----------------|
| `[homeassistant.loader] We found a custom integration X which has not been tested` | Boot banner, **one per HACS integration**, every restart. Count ≈ number of custom integrations. Benign. |
| `[websocket_api.http.connection] ... Reached 4096 pending messages` | A **single slow client** can't drain the state_changed queue — almost always a tablet/dashboard right after restart. Check it's **one IP** over a **bounded window** (resolve the IP via the map). Self-heals on reconnect. Burst at boot = client weight, not a code bug; *continuous* = genuinely overloaded dashboard (trim history-graph / auto-entities cards). |
| `[snitun.*]`, `ClientConnectionResetError`, `Task exception was never retrieved` | Nabu Casa Cloud / network transients. Ignore unless frequent + correlated with an outage. |
| transient device fetch (`spotify`, `apple_tv`/`pyatv`, weather) | One-off API/device blips. Ignore unless sustained — sustained → that integration's reauth/availability. |

**Actionable — real bugs to fix:**

- **`extra keys not allowed @ data['<key>']`** in a script/automation `call_service` → a **service-schema deprecation**. The big recurring one: `light.turn_on` dropped **`color_temp`** → use **`color_temp_kelvin`** (kelvin = `1000000 / mired`). Also `white_value` (removed), `effect` keys that moved. Grep config for the dead key and replace.
- **`Action notify.mobile_app_* not found`** / **`Service … not found`** → a referenced entity/service was renamed or its device removed (re-onboarded phone, deleted integration). Update the automation/Alarmo action to the current slug.
- **Z-Wave `NotFoundError: Value N-CC-… not found on node Node(node_id=N)`** → a `zwave_js.set_value` targets a value id the node no longer exposes (re-interview, firmware change, wrong endpoint). Resolve `node_id` via the map, re-check the value id in the device's Z-Wave page.
- **`Bad credentials` / auth errors** (`github`, etc.) → expired token/PAT. Reconfigure that integration.
- **Anything under `custom_components.<your_domain>`** → your code. Trace it (publish→subscribe→handler) per the Debugging discipline section; this is the only cluster the rest of this skill directly acts on.

### Step 4 — Report

Ranked table: **severity · cluster · root cause · fix · evidence (`timestamp` / `file:line`)**. State explicitly which clusters are *known noise* (so the user stops worrying about a scary count) and which are *actionable*. Resolve every opaque token through the device map so the report reads in plain device names ("Kitchen wall tablet", not `192.168.1.42`). If a fix is config-side (scripts/automations/integration settings) and you only have the log, say so and offer to apply it once given the config path.

### Companion-app notification images (off-network delivery)

Recurring config-side fix: a `notify.mobile_app_*` image "works on Wi-Fi, fails on cellular". Root cause is always that the **phone** downloads the attachment over the internet through Nabu Casa — so anything only reachable on the LAN, or served stale, breaks off-network. Three causes:

1. **Hardcoded LAN / internal URL** (`http://192.168.x.x…`, an `internal_url`-based absolute) — unreachable off-network. Use a **relative** path; the companion app prepends the *active* base URL (cloud when remote) and adds auth.
2. **Legacy `attachment: { url, content-type }`** or a bad MIME (`content-type: jpeg` → must be `image/jpeg`). Prefer the modern **`image:`** key — most robust internal↔external resolution + auth.
3. **Stale CDN cache** — the killer. A snapshot written to a **fixed** `/config/www/…` filename and served via `/local/…` gets cached by Nabu Casa's CDN: off-network you receive the *previous* image (or a pre-first-write 404). Compounded by a **write→push race** (the push beats the file flush).

Fixes, best first:
- **`image: /api/camera_proxy/camera.<name>`** — no file, no race, no static cache, authenticated, resolves via cloud. Frame at fetch time (~live). Best for camera alerts; lets you delete the whole `camera.snapshot` step.
- **Point at a public URL directly** when the image is already internet-hosted (e.g. a YouTube thumbnail `https://i1.ytimg.com/vi/<id>/hqdefault.jpg`) — skip HA entirely; drop any `downloader.download_file` + `delay` steps.
- **Keep a frozen local snapshot** only if you must: switch `attachment`→`image:`, add a cache-buster `?v={{ now().timestamp() | int }}`, and a ~1 s `delay` after `camera.snapshot` so the write flushes.
- iOS attachment cap is **10 MB**. Give each alert source a **distinct `tag:`** — a reused tag means a new alert *replaces* the previous one on the lock screen.

> **Scope note:** most HA log errors are **config / automation / external-device** issues, *not* custom-integration code — Mode 5 triages and routes them, but the editing patterns in this skill apply only to the `custom_components.<your_domain>` cluster. Don't add a home's specific errors to this skill; add only a **new reusable noise/actionable *pattern*** here when one recurs across triages.
