# Cached facts and when to re-derive them

Scope: values copied from somewhere else, which were right when captured and go wrong
silently. No rule lives here — a rule stays in the file that owns it, and a row holds only
the value and the revision it was read at.

**Core rule:** re-derive any row older than ~3 months, and update every listed consumer in
the same pass. A value fixed in one place and not the others is worse than one uniformly old.

## Contents

1. The cached facts
2. When the release row goes red
3. Step 1: Pull the release's sources
4. Step 2: Read both sources
5. Step 3: Settle every claim against core at the tag
6. Step 4: Write the rows, then move the release cell

## The cached facts

| Fact | Value | Captured | Re-derive with | Consumers | Gate |
|---|---|---|---|---|---|
| HA release the skill is current for | `2026.9` | 2026-09-19 | `curl -s https://pypi.org/pypi/homeassistant/json \| jq -r .info.version`, then *When the release row goes red* below | the fetched sources in `docs/ha-release/` · every section of `reference/patterns.md` that names a release, and *Announced for a release after 2026.9 — Step 1* · *Step 4: Say whether the panel handles the safe area* and *A panel that reads devices reads them by config entry — Step 3* in `reference/panels.md` | `scripts/check_ha_release.py`, which fails once PyPI's minor is ahead of this cell |
| HA minimum Python | `3.14` (HA dev needs 3.14.2+) | 2026-09-12, unchanged since 2026-06 | developers.home-assistant.io/docs/development_environment | the `python-version` in ha-integration-ci's three reusable workflows (a CI release) · a consumer's `pyproject.toml` ruff `target-version` · `pyrightconfig.json` · `templates/pyproject.toml`, its header comments and its banned-api message · the pyright snippet in `reference/patterns.md` · the `target-version` line `evals/make_fixture.sh` writes | `version_sync.py` compares the first three; pylint's `py-version` is **not** compared and moves by hand |
| Quality-scale canonical rule set | 54 rules, see `reference/quality-scale.md` | 2026-09-12 | developers.home-assistant.io/docs/core/integration-quality-scale/ — or, as data, the `rules:` keys of any Platinum core integration's `quality_scale.yaml` (`airgradient`, `husqvarna_automower`), which is how the 2026-09 re-derivation found two rules the 2026-06 capture lacked | the rule lists in `reference/quality-scale.md` · `TIER_RULES` in ha-integration-ci's `scripts/skill_audit.py` (a CI release) · every `quality_scale.yaml` | none — the two lists match today with nothing asserting they still will |
| GitHub action versions | checkout `v7.0.1` · dependency-review `v5.0.0` · stale `v11.0.0` | 2026-08-22 | `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name`, then `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` for the SHA | the SHA pins in the four plain workflows in `templates/.github/workflows/`, each with its version in the trailing comment · the checkout line `evals/make_fixture.sh` plants for scenario 02 | `check_action_pins` holds the *shape* — a 40-hex SHA with a version comment — and never the version; the CI repositories' own pins move by their own Dependabot |
| `pytest-homeassistant-custom-component` → HA | `0.13.365` → HA `2026.9.2`, requires-python `>=3.14` | 2026-09-12 | pypi.org/project/pytest-homeassistant-custom-component | `templates/requirements.test.txt` pin · the HA-minimum-Python row above | `version_sync.py` requires the harness to be pinned, never that this mapping is current |
| Brand image spec | `home-assistant/brands` README at `8853e42` | 2026-09-20 | `gh api 'repos/home-assistant/brands/commits?path=README.md' --jq '.[0].sha'`; re-read the README when it has moved — *Inner workings* for the filenames, *Missing image handling* for the fallbacks, *Image specification* and its two subsections for the rules. The proxy's own behaviour — the `?placeholder=no` opt-out and the endpoint shapes — is not in that README but in `developers.home-assistant.io/docs/core/integration/brand_images` | *Step 5: Ship the brand assets* in `reference/scaffold.md` · `check_brand_assets` in ha-integration-ci's `scripts/skill_audit.py` (a CI release) | `check_brand_assets` as released **fails** a missing `brand/`, `icon.png`, `icon@2x.png`, `logo.png` or `logo@2x.png`, and either icon at the wrong size — so it refuses the square-logo case this spec allows. Narrowing it to `icon.png` is a CI release not yet cut |
| HACS dashboard brand source | the legacy CDN, not the inline `brand/` folder | 2026-06 | hacs/integration #5171, #5223 | the `> **Note:**` under *Step 5: Ship the brand assets* in `reference/scaffold.md` | none — it clears when HACS points its dashboard at the proxy |
| Terms the two source sites publish under | home-assistant.io content is CC BY-NC-SA 4.0; `developers.home-assistant.io` ships no licence file at all | 2026-09-19 | `curl -s https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/LICENSE.md \| head -5`, and check `LICENSE`, `LICENSE.md` and `LICENSE.txt` on both branches of `home-assistant/developers.home-assistant.io` | `LICENCES` in `scripts/fetch_ha_sources.py`, which stamps the notice into every file the fetch writes · the carve-out in this repository's own `LICENSE` | none — a change here is applied by refetching |
| Panel design sources | the frontend's `src/resources/theme/` (`color/color.globals.ts`, `typography.globals.ts`) · the *Supported theme variables* section of the `frontend` integration page · the two m3.material.io pages | 2026-09-12 for the HA sources; the Material pages were not fetched | `gh api repos/home-assistant/frontend/contents/src/resources/theme --jq '.[].name'` · the headings of `source/_integrations/frontend.markdown` in `home-assistant/home-assistant.io` | the source list under **Fetch before deciding sizes/tokens — don't guess from memory** in `ha-panel-design/SKILL.md` | none |

## When the release row goes red

`scripts/check_ha_release.py` fails once PyPI's `homeassistant` minor is ahead of the release
row. That check is maintenance of the skill; a scaffolded integration does not carry it.

**Core rule:** a post says *what* changed and *why*. Core at the tag says everything else.

### Step 1: Pull the release's sources

```
python3 scripts/fetch_ha_sources.py --release <the new minor>
```

| Rule | Value |
|---|---|
| what it writes | the window's developer-blog posts, and the *Backward-incompatible changes* section of the release-notes post, into `docs/ha-release/<minor>/` with an index beside them |
| `--since <older minor>` | widens the window, for a backfill across several releases |
| what to commit | what it wrote |
| why it is not a convenience | the governance gate refuses a patch to this directory that names a release until that release's fetched sources have been served |
| exactly what it demands | `unread_sources` in `scripts/governance_gate.py`, which is the one statement of that rule |
| what the gate proves | that the sources which exist for the release were read — never that what you wrote is true |

### Step 2: Read both sources

Neither contains the other.

| Rule | Value |
|---|---|
| developers.home-assistant.io/blog, paged back to the last captured release | the only place most API changes are explained; a release's notes link a few of its window's posts and the rest are reachable only from the blog index |
| the release-notes post's *Backward-incompatible changes* section | user-facing removals, most of which never get a developer-blog post — the vacuum `battery_level` row in *Deprecated platform APIs — Step 1* of `reference/patterns.md` came from here |

**Timing:** open every source before writing a row from it.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| summarising a change from memory | open the post | a row with no source behind it is the failure this procedure exists to prevent | Step 2 |
| writing a row from a release note's one-line mention | open the post behind it | the mention names the change and not the API | Step 2 |
| filtering by "platforms we happen to use" | read all of them | the skill scaffolds any integration, so an OAuth2, event-entity, condition or media-source change is in scope with no such repository in front of you | Step 2 |

### Step 3: Settle every claim against core at the tag

Read `raw.githubusercontent.com/home-assistant/core/<tag>/…` at the tag the release row
names, and say in the row that you did.

| Scenario | Choice |
|---|---|
| what changed, and why | the developer-blog post |
| the API's spelling, and the module it lives in | core at the tag |
| the release it landed in | core at the tag, never a post's publication date |
| the release it is removed in | core at the tag — the `breaks_in_ha_version` of the call site, or the version argument of the `DeprecatedConstantEnum` beside the constant |
| a version neither states | nothing; the row says so rather than guessing one |

**Symptom:** a post is written before the change ships, so stopping at one yields a removal
release the post omits, an enum member list copied from the replaced constants rather than
the enum, a landing release inferred from a publication date, and an API written up as
usable that the release does not carry.

### Step 4: Write the rows, then move the release cell

| Rule | Value |
|---|---|
| a change a custom integration can meet | a row in the `reference/patterns.md` section that owns the topic |
| a change announced for a release that has not landed | a row in *Announced for a release after 2026.9 — Step 1* of `reference/patterns.md`, cleared when it lands |
| every other row in the table above | re-derived with its own *Re-derive with* command |
| the release cell and its captured date | moved, last |
| the whole pass | one PR |

> **Note:** `hacs/action@main` and `home-assistant/actions/hassfest@master` are deliberately
> on mutable refs and the audit exempts them — *What the audit checks now* in
> ha-integration-ci's README. A tag would stop tracking their validation rules; the
> trade-off is capped with read-only permissions and `persist-credentials: false`.
