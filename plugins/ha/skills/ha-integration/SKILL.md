---
name: ha-integration
description: Use when developing or troubleshooting a Home Assistant custom integration — Python code under `custom_components/`. Covers config/options/reauth/reconfigure flows, the data coordinator and entity platforms (sensor, switch, notify, fan, etc.), manifest, services, diagnostics, and quality_scale. Reach for it on symptom-style reports too: an entity going unavailable after restart, a notify/custom service breaking after an HA update, a `device_class`/`state_class` mismatch HA complains about, a reconfigure flow request, or CI/Dependabot/HACS/hassfest issues on an integration repo. NOT for Lovelace cards, panel/display UI styling (`ha-panel-design`), triaging a `home-assistant.log` (`ha-triage`), or generic non-HA Python. Invoke before editing integration code; re-invoke after /compact.
---

# Home Assistant Integration Assistant

**Target platinum quality scale, and fetch the source below before writing the code that
meets it.**

Authoritative sources:
- Creating integrations: https://developers.home-assistant.io/docs/creating_integration_index/
- Config entries: https://developers.home-assistant.io/docs/config_entries_index/
- Config flows: https://developers.home-assistant.io/docs/config_entries_config_flow_handler/
- Data fetching + coordinator: https://developers.home-assistant.io/docs/integration_fetching_data/
- Setup failures: https://developers.home-assistant.io/docs/integration_setup_failures/
- Quality scale: https://developers.home-assistant.io/docs/integration_quality_scale_index/
- Real examples: https://github.com/home-assistant/core/tree/dev/homeassistant/components

---

## Step 1 — Detect mode

Check the working directory, pick a mode, then **read that mode's reference file before acting**.

| Mode | When | Read first |
|---|---|---|
| **Scaffold** | no `custom_components/`, or the user wants a new integration | `reference/scaffold.md`, then `reference/patterns.md` |
| **Modify** | `custom_components/` exists and something is being added or changed | `reference/patterns.md`. Adding a platform also touches `strings.json`/`translations/` and the tier claim — see `reference/quality-scale.md` |
| **Test** | writing or fixing tests for an integration | `reference/testing.md` — the root `conftest.py` and `asyncio_mode` prerequisites decide whether the suite runs at all |
| **Lint** | hygiene pass over existing code | this file, *Lint & quality check* below |
| **Audit** | verify the skill was actually followed | `reference/audit.md`, which says what the mechanical audit covers and what is left to judgement |
| **Release / repo setup** | first release, tokens, required checks | `reference/github-setup.md` — token, ruleset, dependency graph, required contexts. Then `reference/versioning.md` for how the version is decided, `reference/commits.md` for commit subjects and titles, `reference/github-actions.md` for what the scaffold carries |

How a panel is **built and served** stays here, in `reference/panels.md`; how it **looks** is
the `ha-panel-design` skill.

## Invariants — true in every mode

- **The release tag sets the version.** No PR carries a manifest bump; `release.yml` patches
  `manifest.json` at publish. Details in `reference/versioning.md`.
- **The commit subjects are the changelog** — the form each takes, and why the PR body stays
  empty, are `reference/commits.md`.
- **Never merge a red check**, and never merge by disabling one —
  *Merge discipline — never merge a red check* in `reference/discipline.md`.
- **Callers, not bodies; copies, not paraphrases.** The scaffold calls the CI repositories'
  reusable workflows and copies a few configs; every deviation must be a listed adaptation —
  see `reference/audit.md`.
- **Cached facts go stale silently.** Anything captured more than ~3 months ago is re-derived
  before it is trusted; the table and its commands are `reference/freshness.md`.
- **The skill is current for one Home Assistant release at a time**, which the release row
  of `reference/freshness.md` names; what that release changed is in the
  `reference/patterns.md` section that owns the topic, and the row moves only in the skill's
  own repository.

## Reference map

| file | when to read |
|---|---|
| `reference/scaffold.md` | starting a repository: what to ask, what to generate, the brand assets, manifest key order, HACS validation |
| `reference/patterns.md` | writing or changing Python under `custom_components/`, including file structure and typing |
| `reference/testing.md` | writing tests, mocking at the boundary, or a suite that fails before any test runs |
| `reference/commits.md` | writing a commit subject, a PR title or a PR body |
| `reference/github-setup.md` | configuring the repository on GitHub: token, required checks, dependency graph, supply chain |
| `reference/github-actions.md` | writing or reviewing a workflow file, and what may differ from its source |
| `reference/versioning.md` | cutting or gating a release, including an rc |
| `reference/dependabot.md` | configuring or debugging Dependabot, including the callers' pins and what it cannot reach |
| `reference/quality-scale.md` | claiming a tier, and the canonical rule set behind it |
| `reference/panels.md` | building or fixing an integration that serves a panel |
| `reference/discipline.md` | a check is red, or a root cause is about to be named |
| `reference/audit.md` | auditing a repository against this skill |
| `reference/freshness.md` | asking whether a cached value is still true |

---

## Scaffold

Read `reference/scaffold.md`, then `reference/github-setup.md` when the repo needs its GitHub side configured. Ask the requirement questions in one go; do not generate files before they are answered.

---

## Modify existing integration

Identify the integration domain from `custom_components/`. Then ask what to add or change:

- Add new platform
- Add/update translations
- Add options flow
- Add or fix tests (start from `reference/testing.md`)
- Add reconfigure flow (`async_step_reconfigure`)
- Add reauth flow (`async_step_reauth`)
- Add or update `quality_scale.yaml`
- Add GitHub workflows
- Cut a release (publish the rc draft, then the full one)
- Other

Apply the same patterns and code style as a scaffold.

---

## Lint & quality check

1. Run `ruff check .` and `ruff format --check .` under the shipped `pyproject.toml` — fix all actionable issues; suppress intentional ones with `# noqa` and a reason
2. Run `python -m pyright custom_components/` — fix all actionable issues
3. Check `quality_scale.yaml` exists; if not, offer to create it
4. Check `manifest.json` — correct `documentation` URL pointing to the repo, keys in the order `reference/scaffold.md` gives
5. Report: files changed · issues fixed · issues intentionally suppressed (with rationale) · remaining manual work

---

## Audit — skill conformance

Run it before claiming a tier and before merge: canonical workflows present and correct,
documented patterns applied, antipatterns gone, `quality_scale.yaml` honest.

Two layers:

1. **Mechanical gate** — the audit, as the mode table above says.
2. **Judgement checklist** — `reference/audit.md`. The items a grep can't decide.

> **Note:** a green gate does not prove the copied files match; *Step 1: Callers, not
> bodies; copies, not paraphrases* in `reference/audit.md` says why, and what to do about it.

---
