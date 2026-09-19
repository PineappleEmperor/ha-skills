# Cached facts and when to re-derive them

Load-bearing values that were right when captured and go wrong silently — nothing in CI
notices. **Re-derive any row older than ~3 months, and update every listed consumer in the
same pass**; a value fixed in one place and not the others is worse than one that is
uniformly old.

| Cached fact | Value | Captured | Re-derive with | Consumers to update together |
|---|---|---|---|---|
| HA release the skill is current for | `2026.9` | 2026-09-19 | `curl -s https://pypi.org/pypi/homeassistant/json \| jq -r .info.version`; then that release's developer-blog posts and the developer section of its release notes | *What changed in recent releases* in `reference/patterns.md` · *Home Assistant pads the panel for the safe area* and *A panel that reads devices reads them by config entry* in `reference/panels.md` · the skill repository's own CI, which reads this cell and fails once PyPI's minor is ahead of it |
| HA minimum Python | `3.14` (HA dev needs 3.14.2+) | 2026-09-12, unchanged since 2026-06 | developers.home-assistant.io/docs/development_environment | the `python-version` in ha-integration-ci's three reusable workflows (a CI release) · a consumer's `pyproject.toml` ruff `target-version` · `pyrightconfig.json` — those three are what the audit compares (*What the audit checks now* in ha-integration-ci's README); pylint's `py-version`, if the repo uses pylint, is **not** checked and must be updated by hand · the value in `templates/pyproject.toml`, its header comments and its banned-api message, and the pyright snippet in `reference/patterns.md` · the `target-version` line `evals/make_fixture.sh` writes |
| Quality-scale canonical rule set | 54 rules, see `reference/quality-scale.md` | 2026-09-12 | developers.home-assistant.io/docs/core/integration-quality-scale/ — or, as data, the `rules:` keys of any Platinum core integration's `quality_scale.yaml` (`airgradient`, `husqvarna_automower`), which is how the 2026-09 re-derivation found two rules the 2026-06 capture lacked | the rule lists in `reference/quality-scale.md` · `TIER_RULES` in ha-integration-ci's `scripts/skill_audit.py`, which is what actually fails a consumer's file (a CI release) · every `quality_scale.yaml` |
| GitHub action versions | checkout `v7.0.1` · dependency-review `v5.0.0` · stale `v11.0.0` | 2026-08-22 | `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name`, then `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` for the SHA | the SHA pins in the four plain workflows in `templates/.github/workflows/`, each with its version in the trailing comment · the checkout line `evals/make_fixture.sh` plants for scenario 02, which must match the template's; the CI repositories' own pins move by their own Dependabot |
| `pytest-homeassistant-custom-component` → HA | `0.13.365` → HA `2026.9.2`, requires-python `>=3.14` | 2026-09-12 | pypi.org/project/pytest-homeassistant-custom-component | `templates/requirements.test.txt` pin · the HA-minimum-Python row above. The template carries no mapping beside the pin, and says why in its own comment |
| Brand assets served from inline `brand/` | since HA `2026.3.0`; HACS dashboard still reads the legacy CDN | 2026-06 | hacs/integration #5171, #5223 | the brand-assets note in `reference/scaffold.md` |
| Brand image specification | 8 filenames (`icon`/`logo`/`dark_icon`/`dark_logo`, each with an `@2x`); icons exactly 256/512 and 1:1; logo shortest side 128–256 and 256–512, band maximum preferred; trimmed of empty space; no HA-branded imagery in a custom integration | 2026-09-19 | `curl -s https://raw.githubusercontent.com/home-assistant/brands/master/README.md` — *Inner workings* for the eight filenames, *Missing image handling* for the fallback chain, and *Image specification* with its two subsections for the rules; the `custom_integrations/` folder is legacy but that README still owns the spec for inline assets | the *Brand assets* section of `reference/scaffold.md` · `check_brand_assets` in ha-integration-ci's `scripts/skill_audit.py`, which is what measures a consumer's files (a CI release) |
| Panel design sources | the frontend's `src/resources/theme/` (`color/color.globals.ts`, `typography.globals.ts`) · the *Supported theme variables* section of the `frontend` integration page · the two m3.material.io pages | 2026-09-12 for the HA sources; the Material pages were not fetched | `gh api repos/home-assistant/frontend/contents/src/resources/theme --jq '.[].name'` · the headings of `source/_integrations/frontend.markdown` in `home-assistant/home-assistant.io` | the source list under **Fetch before deciding sizes/tokens — don't guess from memory** in `ha-panel-design/SKILL.md` |

## When the release row goes red

The skill repository's own CI fails once PyPI's
`homeassistant` minor is ahead of the first row above — that check is maintenance of the
skill and is not something a scaffolded integration carries. The pass that clears it: read the
sources below; for each change a custom integration can meet, add a row to *What changed in
recent releases* in `reference/patterns.md` and apply it in the section that owns the topic;
re-derive every other row here; move the release cell and its captured date; one PR. The
first such pass covered 2026.6 to 2026.9 in one go, on 2026-09-19.

**Both sources, because neither contains the other.** Verified on the 2026.9 pair:

- **developers.home-assistant.io/blog**, paged back to the last captured release. This is
  the only place most API changes are explained. The release notes linked **three** of the
  posts in that window; the rest are reachable only from the blog index.
- **home-assistant.io's release-notes post for that version**, specifically its
  *Backward-incompatible changes* section. Nine entries there for 2026.9, and **none of them
  had a developer-blog post** — including the vacuum `battery_level` removal that *What
  changed in recent releases* in `reference/patterns.md` records, which a blog-only pass
  misses entirely.

**A post is not the source of record; core at the tag is.** A developer-blog post is one
author's description of a change, written before it shipped. It is the source for *what*
changed and *why*. It is not the source for the API's spelling, the module it lives in, the
release it landed in, or the release it is removed in — for those, read
`raw.githubusercontent.com/home-assistant/core/<tag>/…` at the tag the release row names,
and say in the row that you did. The 2026.9 pass got eight facts wrong by stopping at the
post: a removal release the post omitted and `const.py` states, an enum member list copied
from the *replaced* constants rather than the enum, a landing release inferred from a post's
publication date, and a whole API — `async_retry_migration` — written up as usable when it
does not exist in the release the skill claims to be current for. **If a claim can be
checked against core, check it against core.**

**Open every source before writing a row from it.** A change summarised from memory, or
from a release note's one-line mention without the post behind it, is the failure this
procedure exists to prevent — a draft of the 2026.9 table carried four rows with no source,
and the API names in two of them were wrong. If neither the post nor core states a version,
the row says so rather than guessing one. **Do not filter by "platforms we happen to use"**: the skill
scaffolds any integration, so an OAuth2, event-entity, condition or media-source change is
in scope even when no repository in front of you has one.

What `version_sync.py` compares is *What the audit checks now* in ha-integration-ci's
README; it compares what is declared, and the table above is still what says which value is
current.

`hacs/action@main` and `home-assistant/actions/hassfest@master` are **deliberately** on mutable refs; that the audit exempts them, and why, is *What the audit checks now* in ha-integration-ci's README. What rots if they were pinned is their validation rules, which a tag would stop tracking; the trade-off is capped with read-only permissions and `persist-credentials: false` in both workflows.
