# Cached facts and when to re-derive them

Scope: values copied from somewhere else, which were right when captured and go wrong
silently. No rule lives here — a rule stays in the file that owns it, and a row holds only
the value and the revision it was read at.

**Core rule:** re-derive any row older than ~3 months, and update every listed consumer in
the same pass.

## The cached facts

| Fact | Value | Captured | Re-derive with | Consumers | Gate |
|---|---|---|---|---|---|
| HA release the skill is current for | `2026.9` | 2026-09-19 | `curl -s https://pypi.org/pypi/homeassistant/json \| jq -r .info.version` | every section of `reference/patterns.md` that names a release, and *Announced for a release after 2026.9 — Step 1* · *Step 4: Say whether the panel handles the safe area* and *A panel that reads devices reads them by config entry — Step 3* in `reference/panels.md` | the skill repository's own CI, which fails once PyPI's minor is ahead of this cell |
| HA minimum Python | `3.14` (HA dev needs 3.14.2+) | 2026-09-12, unchanged since 2026-06 | developers.home-assistant.io/docs/development_environment | the `python-version` in ha-integration-ci's three reusable workflows (a CI release) · a consumer's `pyproject.toml` ruff `target-version` · `pyrightconfig.json` · `templates/pyproject.toml`, its header comments and its banned-api message · the pyright snippet in `reference/patterns.md` · the `target-version` line `evals/make_fixture.sh` writes | `version_sync.py` compares the first three; pylint's `py-version` is **not** compared and moves by hand |
| Quality-scale canonical rule set | 54 rules, see `reference/quality-scale.md` | 2026-09-12 | developers.home-assistant.io/docs/core/integration-quality-scale/ — or, as data, the `rules:` keys of any Platinum core integration's `quality_scale.yaml` (`airgradient`, `husqvarna_automower`) | the rule lists in `reference/quality-scale.md` · `TIER_RULES` in ha-integration-ci's `scripts/skill_audit.py` (a CI release) · every `quality_scale.yaml` | none |
| GitHub action versions | checkout `v7.0.1` · dependency-review `v5.0.0` · stale `v11.0.0` | 2026-08-22 | `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name`, then `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` for the SHA | the SHA pins in the four plain workflows in `templates/.github/workflows/`, each with its version in the trailing comment · the checkout line `evals/make_fixture.sh` plants for scenario 02 | `check_action_pins`, which holds the shape — a 40-hex SHA with a version comment — and never the version |
| `pytest-homeassistant-custom-component` → HA | `0.13.365` → HA `2026.9.2`, requires-python `>=3.14` | 2026-09-12 | pypi.org/project/pytest-homeassistant-custom-component | `templates/requirements.test.txt` pin · the HA-minimum-Python row above | `version_sync.py` requires the harness to be pinned, never that this mapping is current |
| Brand image spec | `home-assistant/brands` README at `8853e42` | 2026-09-20 | `gh api 'repos/home-assistant/brands/commits?path=README.md' --jq '.[0].sha'`; re-read the README when it has moved — *Inner workings* for the filenames, *Missing image handling* for the fallbacks, *Image specification* and its two subsections for the rules; the proxy's own behaviour is `developers.home-assistant.io/docs/core/integration/brand_images` | *Step 5: Ship the brand assets* in `reference/scaffold.md` · `check_brand_assets` in ha-integration-ci's `scripts/skill_audit.py` (a CI release) | `check_brand_assets` as released, which fails a missing `brand/`, `icon.png`, `icon@2x.png`, `logo.png` or `logo@2x.png`, and either icon at the wrong size |
| HACS dashboard brand source | the legacy CDN, not the inline `brand/` folder | 2026-06 | hacs/integration #5171, #5223 | the `> **Note:**` under *Step 5: Ship the brand assets* in `reference/scaffold.md` | none — it clears when HACS points its dashboard at the proxy |
| Panel design sources | the frontend's `src/resources/theme/` (`color/color.globals.ts`, `typography.globals.ts`) · the *Supported theme variables* section of the `frontend` integration page · the two m3.material.io pages | 2026-09-12 for the HA sources; the Material pages were not fetched | `gh api repos/home-assistant/frontend/contents/src/resources/theme --jq '.[].name'` · the headings of `source/_integrations/frontend.markdown` in `home-assistant/home-assistant.io` | the source list under *Fetch before deciding sizes or tokens* in `ha-panel-design/SKILL.md` | none |

> **Note:** `hacs/action@main` and `home-assistant/actions/hassfest@master` are on mutable
> refs deliberately, and the audit exempts them — *What the audit checks now* in
> ha-integration-ci's README.
