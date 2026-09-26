---
name: ha-integration
description: >-
  Use when developing or troubleshooting a Home Assistant custom integration — Python under
  `custom_components/`.
  TRIGGER WHEN:
  - scaffolding an integration, or adding a platform, flow, coordinator, service, diagnostics
  or manifest key to one
  - fixing a bug or a test in one, or claiming a quality-scale tier
  - cutting a release, or setting up CI, Dependabot, HACS or hassfest on its repository
  SYMPTOMS:
  - an entity unavailable after restart
  - a notify or custom service broken by an HA update
  - a device_class/state_class mismatch HA complains about
  - a red check on an integration repository
  NOT for Lovelace cards, panel styling (ha-panel-design), log triage (ha-triage), or
  non-HA Python. Invoke before editing integration code; re-invoke after /compact.
---

# Home Assistant Integration Assistant

**Target platinum quality scale, and fetch the mode's source before writing the code that
meets it.**

## Detect the mode

Pick the mode from what is about to be done, then **read that mode's file before acting**.

| Mode | When | Read first | Source |
|---|---|---|---|
| **Scaffold** | no `custom_components/`, or the user wants a new integration — what to ask, what to generate, the brand assets, manifest key order, HACS validation | `reference/scaffold.md` | Creating integrations: https://developers.home-assistant.io/docs/creating_integration_index/ · File structure: https://developers.home-assistant.io/docs/creating_integration_file_structure/ · Manifest: https://developers.home-assistant.io/docs/creating_integration_manifest/ |
| **Modify** | `custom_components/` exists and anything under it is being added, changed or fixed — Python, `manifest.json`, `strings.json`, `services.yaml`, translations — including file structure and typing | `reference/patterns.md` | Config entries: https://developers.home-assistant.io/docs/config_entries_index/ · Config flows: https://developers.home-assistant.io/docs/config_entries_config_flow_handler/ · Data fetching + coordinator: https://developers.home-assistant.io/docs/integration_fetching_data/ · Setup failures: https://developers.home-assistant.io/docs/integration_setup_failures/ · Real examples: https://github.com/home-assistant/core/tree/dev/homeassistant/components |
| **Panel** | building or fixing an integration that serves a panel — how it is built and served; how it looks is the `ha-panel-design` skill | `reference/panels.md` | — |
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

1. Run `ruff check .` and `ruff format --check .` under the shipped `pyproject.toml` — fix all actionable issues; suppress intentional ones with `# noqa` and a reason
2. Run `python -m pyright custom_components/` — fix all actionable issues
3. Check `quality_scale.yaml` exists; if not, offer to create it
4. Check `manifest.json` — correct `documentation` URL pointing to the repo, keys in the order *Step 6: Order `manifest.json`* in `reference/scaffold.md` gives
5. Report: files changed · issues fixed · issues intentionally suppressed (with rationale) · remaining manual work
