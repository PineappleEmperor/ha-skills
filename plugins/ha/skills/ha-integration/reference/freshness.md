# Cached facts and when to re-derive them

Load-bearing values that were right when captured and go wrong silently — nothing in CI
notices. **Re-derive any row older than ~3 months, and update every listed consumer in the
same pass**; a value fixed in one place and not the others is worse than one that is
uniformly old.

| Cached fact | Value | Captured | Re-derive with | Consumers to update together |
|---|---|---|---|---|
| HA minimum Python | `3.14` (HA dev needs 3.14.2+) | 2026-06 | developers.home-assistant.io/docs/development_environment | the `python-version` in ha-integration-ci's three reusable workflows (a CI release) · a consumer's `pyproject.toml` ruff `target-version` · `pyrightconfig.json` — compared by `version_sync.py` in the audit; pylint's `py-version`, if the repo uses pylint, is **not** checked and must be updated by hand |
| Quality-scale canonical rule set | see `reference/quality-scale.md` | 2026-06 | developers.home-assistant.io/docs/core/integration-quality-scale/ | the rule lists in `reference/quality-scale.md` · every `quality_scale.yaml` |
| GitHub action versions | dependency-review `v5.0.0` · stale `v11.0.0` | 2026-08-22 | `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name`, then `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` for the SHA | the SHA pins in the four plain workflows in `templates/.github/workflows/`, each with its version in the trailing comment; the CI repositories' own pins move by their own Dependabot |
| `pytest-homeassistant-custom-component` → HA | `0.13.357` → HA `2026.8.3`, requires-python `>=3.14` | 2026-08-23 | pypi.org/project/pytest-homeassistant-custom-component | `templates/requirements.test.txt` pin · the HA-minimum-Python row above |
| Brand assets served from inline `brand/` | since HA `2026.3.0`; HACS dashboard still reads the legacy CDN | 2026-06 | hacs/integration #5171, #5223 | the brand-assets note in `reference/scaffold.md` |

What `version_sync.py` compares in the audit is ha-integration-ci's README; it compares
what is declared, and the table above is still what says which value is current.

`hacs/action@main` and `home-assistant/actions/hassfest@master` are **deliberately** on mutable refs — that's the ref each project documents, and a tag pin stops tracking their validation rules. They're exempt from the pin rules; the trade-off is capped with read-only permissions and `persist-credentials: false` in both workflows.
