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

**Target platinum quality scale, and fetch the source below before writing the code that
meets it.**

- Creating integrations: https://developers.home-assistant.io/docs/creating_integration_index/
- File structure: https://developers.home-assistant.io/docs/creating_integration_file_structure/
- Manifest: https://developers.home-assistant.io/docs/creating_integration_manifest/
- Config entries: https://developers.home-assistant.io/docs/config_entries_index/
- Config flows: https://developers.home-assistant.io/docs/config_entries_config_flow_handler/
- Data fetching + coordinator: https://developers.home-assistant.io/docs/integration_fetching_data/
- Setup failures: https://developers.home-assistant.io/docs/integration_setup_failures/
- Quality scale: https://developers.home-assistant.io/docs/integration_quality_scale_index/
- What a release changed or deprecated: https://developers.home-assistant.io/blog/
- Real examples: https://github.com/home-assistant/core/tree/dev/homeassistant/components

## Detect the mode

Pick the mode from what is about to be done, then **read that mode's file before acting**.

| Mode | When | Read first |
|---|---|---|
| **Scaffold** | no `custom_components/`, or the user wants a new integration | `reference/scaffold.md` |
| **Modify** | `custom_components/` exists and something is being added, changed or fixed | `reference/patterns.md` |
| **Test** | writing or fixing tests for an integration | `reference/testing.md` |
| **Lint** | hygiene pass over existing code | *Lint & quality check* below |
| **Debug** | a root cause is about to be named | `reference/discipline.md` |
| **Commit / PR** | writing a commit subject, a PR title or a PR body | `reference/commits.md` |
| **Merge** | a check is red, or a merge is about to happen | `reference/discipline.md` |
| **Workflow** | writing or reviewing a workflow file | `reference/github-actions.md` |
| **Release** | cutting or gating a release, or touching the version in `manifest.json` | `reference/versioning.md` |
| **Repo setup** | first release, tokens, required checks | `reference/github-setup.md` |
| **Audit** | verify the skill was actually followed | `reference/audit.md` |
| **Currency** | acting on a pin, SHA, count or Home Assistant release number | `reference/freshness.md` |

## Lint & quality check

1. Run `ruff check .` and `ruff format --check .` under the shipped `pyproject.toml` — fix all actionable issues; suppress intentional ones with `# noqa` and a reason
2. Run `python -m pyright custom_components/` — fix all actionable issues
3. Check `quality_scale.yaml` exists; if not, offer to create it
4. Check `manifest.json` — correct `documentation` URL pointing to the repo, keys in the order *Step 6: Order `manifest.json`* in `reference/scaffold.md` gives
5. Report: files changed · issues fixed · issues intentionally suppressed (with rationale) · remaining manual work

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
| `reference/panels.md` | building or fixing an integration that serves a panel — how it is built and served; how it looks is the `ha-panel-design` skill |
| `reference/discipline.md` | a check is red, or a root cause is about to be named |
| `reference/audit.md` | auditing a repository against this skill |
| `reference/freshness.md` | asking whether a cached value is still true |
