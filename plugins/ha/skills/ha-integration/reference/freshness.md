# Cached facts and when to re-derive them

Load-bearing values that were right when captured and go wrong silently — nothing in CI
notices. **Re-derive any row older than ~3 months, and update every listed consumer in the
same pass**; a value fixed in one place and not the others is worse than one that is
uniformly old.

| Cached fact | Value | Captured | Re-derive with | Consumers to update together |
|---|---|---|---|---|
| HA minimum Python | `3.14` (HA dev needs 3.14.2+) | 2026-09-12, unchanged since 2026-06 | developers.home-assistant.io/docs/development_environment | the `python-version` in ha-integration-ci's three reusable workflows (a CI release) · a consumer's `pyproject.toml` ruff `target-version` · `pyrightconfig.json` — those three are what the audit compares (ha-integration-ci's README); pylint's `py-version`, if the repo uses pylint, is **not** checked and must be updated by hand · the value in `templates/pyproject.toml`, its header comments and its banned-api message, and the pyright snippet in `reference/patterns.md` · the `target-version` line `evals/make_fixture.sh` writes |
| Quality-scale canonical rule set | 54 rules, see `reference/quality-scale.md` | 2026-09-12 | developers.home-assistant.io/docs/core/integration-quality-scale/ — or, as data, the `rules:` keys of any Platinum core integration's `quality_scale.yaml` (`airgradient`, `husqvarna_automower`), which is how the 2026-09 re-derivation found two rules the 2026-06 capture lacked | the rule lists in `reference/quality-scale.md` · `TIER_RULES` in ha-integration-ci's `scripts/skill_audit.py`, which is what actually fails a consumer's file (a CI release) · every `quality_scale.yaml` |
| GitHub action versions | checkout `v7.0.1` · dependency-review `v5.0.0` · stale `v11.0.0` | 2026-08-22 | `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name`, then `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` for the SHA | the SHA pins in the four plain workflows in `templates/.github/workflows/`, each with its version in the trailing comment · the checkout line `evals/make_fixture.sh` plants for scenario 02, which must match the template's; the CI repositories' own pins move by their own Dependabot |
| `pytest-homeassistant-custom-component` → HA | `0.13.365` → HA `2026.9.2`, requires-python `>=3.14` | 2026-09-12 | pypi.org/project/pytest-homeassistant-custom-component | `templates/requirements.test.txt` pin · the HA-minimum-Python row above. The template carries no mapping beside the pin, and says why in its own comment |
| Brand assets served from inline `brand/` | since HA `2026.3.0`; HACS dashboard still reads the legacy CDN | 2026-06 | hacs/integration #5171, #5223 | the brand-assets note in `reference/scaffold.md` |
| Panel design sources | the frontend's `src/resources/theme/` (`color/color.globals.ts`, `typography.globals.ts`) · the *Supported theme variables* section of the `frontend` integration page · the two m3.material.io pages | 2026-09-12 for the HA sources; the Material pages were not fetched | `gh api repos/home-assistant/frontend/contents/src/resources/theme --jq '.[].name'` · the headings of `source/_integrations/frontend.markdown` in `home-assistant/home-assistant.io` | the source list under **Fetch before deciding sizes/tokens — don't guess from memory** in `ha-panel-design/SKILL.md` |

What `version_sync.py` compares in the audit is ha-integration-ci's README; it compares
what is declared, and the table above is still what says which value is current.

`hacs/action@main` and `home-assistant/actions/hassfest@master` are **deliberately** on mutable refs — that's the ref each project documents, and a tag pin stops tracking their validation rules. They're exempt from the pin rules; the trade-off is capped with read-only permissions and `persist-credentials: false` in both workflows.
