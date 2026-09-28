---
name: ha-integration
description: >-
  Use when developing or troubleshooting a Home Assistant custom integration — the package
  under `custom_components/`, or the panel it serves.
  TRIGGER WHEN:
  - scaffolding an integration, or adding a platform, flow, coordinator, service, diagnostics
  or manifest key to one
  - fixing a bug or a test in one, or claiming a quality-scale tier
  - restyling its panel: sizing, type, colour, spacing or layout
  - cutting a release, or setting up CI, Dependabot, HACS or hassfest on its repository
  SYMPTOMS:
  - an entity unavailable after restart
  - a notify or custom service broken by an HA update
  - a device_class/state_class mismatch warning
  - a red check on an integration repository
  - a panel foreign beside HA's pages: unscaled text, hardcoded colours broken in dark
  mode, tap targets too small
  NOT for Lovelace cards, YAML dashboards, fault triage (ha-triage), or non-HA Python. Invoke
  before editing integration code or panel CSS; re-invoke after /compact.
---

# Home Assistant Integration Assistant

**Target platinum quality scale, and fetch the mode's source before writing the code that
meets it.**

## Detect the mode

Pick the mode from what is about to be done, then **read that mode's file before acting**.

| Mode | When | Read first | Source |
|---|---|---|---|
| **Scaffold** | no `custom_components/`, or the user wants a new integration — what to ask, what to generate, the brand assets, manifest key order, HACS validation | `reference/scaffold.md` | Creating integrations: https://developers.home-assistant.io/docs/creating_integration_index/ · File structure: https://developers.home-assistant.io/docs/creating_integration_file_structure/ · Manifest: https://developers.home-assistant.io/docs/creating_integration_manifest/ |
| **Modify** | `custom_components/` exists and its package is being added to, changed or fixed — Python, `strings.json`, `services.yaml`, translations — including file structure and typing | `reference/patterns.md` | Config entries: https://developers.home-assistant.io/docs/config_entries_index/ · Config flows: https://developers.home-assistant.io/docs/config_entries_config_flow_handler/ · Data fetching + coordinator: https://developers.home-assistant.io/docs/integration_fetching_data/ · Setup failures: https://developers.home-assistant.io/docs/integration_setup_failures/ · Blocking operations: https://developers.home-assistant.io/docs/asyncio_blocking_operations/ · Real examples: https://github.com/home-assistant/core/tree/dev/homeassistant/components |
| **Manifest** | adding or changing a `manifest.json` key | `reference/scaffold.md` | Manifest: https://developers.home-assistant.io/docs/creating_integration_manifest/ |
| **Panel** | building or fixing an integration that serves a panel — how it is built and served; how it looks is the Panel design row | `reference/panels.md` | — |
| **Panel design** | changing how a panel looks — the CSS or markup of a Lit/TS panel web component: sizing, typography, colour, spacing, layout | `reference/panel-design.md` | Material 3 type scale: https://m3.material.io/styles/typography/type-scale-tokens · Material 3 states and touch targets: https://m3.material.io/foundations/interaction/states/overview · HA theme properties: https://github.com/home-assistant/frontend/tree/dev/src/resources/theme · Theme variables a user may override: https://www.home-assistant.io/integrations/frontend/#supported-theme-variables |
| **Test** | writing or fixing tests, mocking at the boundary, or a suite that fails before any test runs | `reference/testing.md` | — |
| **Lint** | hygiene pass over existing code | *Lint & quality check* below | — |
| **Tier** | claiming a quality-scale tier, and the canonical rule set behind it | `reference/quality-scale.md` | Quality scale: https://developers.home-assistant.io/docs/integration_quality_scale_index/ |
| **Debug** | a root cause is about to be named | `reference/discipline.md` | — |
| **Commit / PR** | writing a commit subject, a PR title or a PR body | `reference/commits.md` | — |
| **Merge** | a check is red, or a merge is about to happen | `reference/discipline.md` | — |
| **Workflow** | writing or reviewing a workflow file, and what may differ from its source | `reference/github-actions.md` | — |
| **Dependabot** | configuring or debugging Dependabot, including the callers' pins and what it cannot reach | `reference/dependabot.md` | — |
| **Release** | cutting or gating a release, including an rc, or touching the version in `manifest.json` | `reference/versioning.md` | — |
| **Repo setup** | first release, or configuring the repository on GitHub: token, required checks, dependency graph, supply chain | `reference/github-setup.md` | — |
| **Audit** | auditing a repository against this skill | `reference/audit.md` | — |
| **Currency** | acting on a pin, SHA, count or Home Assistant release number, or asking whether a cached value is still true | `reference/freshness.md` | What a release changed or deprecated: https://developers.home-assistant.io/blog/ |

## Lint & quality check

1. Run `ruff check .` and `ruff format --check .` under the shipped `pyproject.toml`, with ruff at the version the mypy and ruff row of `reference/freshness.md` names — fix all actionable issues; suppress intentional ones with `# noqa` and a reason
2. Run `mypy --config-file mypy.ini custom_components/`, with mypy at the version the mypy and ruff row of `reference/freshness.md` names — fix all actionable issues
3. Check `quality_scale.yaml` exists; if not, offer to create it
4. Check `manifest.json` against *Step 6: Order `manifest.json`* in `reference/scaffold.md`
5. Report: files changed · issues fixed · issues intentionally suppressed (with rationale) · remaining manual work
