---
name: ha-integration
description: >-
  Use when building, changing, testing or releasing a Home Assistant custom integration: the
  `custom_components/` package, its panel, or its repository's CI, Dependabot, HACS listing
  and releases — a new platform, config flow, coordinator or manifest key, a red hassfest,
  HACS or CI check, a device_class or state_class warning, a quality-scale tier, a panel that
  looks wrong beside Home Assistant's pages. Not for naming a fault's cause from a log (ha-triage), Lovelace cards, YAML
  dashboards, or Python unrelated to Home Assistant.
---

# Home Assistant Integration Assistant

This skill builds and maintains Home Assistant custom integrations — the code, its tests, its
panel, its CI and its releases — to the platinum tier of Home Assistant's quality scale. Pick
the mode that matches the task, read every file its row names in full, and fetch its sources
before writing anything.

## Pick the mode

A mode is one kind of task; each row says when it applies, which files it reads and which
pages back it.

| Mode | When | Read first | Source |
|---|---|---|---|
| **Scaffold** | no `custom_components/`, or a new integration or a new repository for one, including setting up its CI and release process — from the first questions to the GitHub settings, in order | `reference/scaffold.md`, `reference/lint.md` | Creating integrations: https://contributors.home-assistant.io/core/integrations/create/ · File structure: https://contributors.home-assistant.io/core/integrations/file-structure/ · Manifest: https://contributors.home-assistant.io/core/integrations/manifest/ |
| **Modify** | `custom_components/` exists and its package is being added to, changed or fixed — Python, `services.yaml`, `translations/` — including file structure and typing | `reference/patterns.md`, `reference/lint.md` | Config entries: https://contributors.home-assistant.io/core/integrations/config-entries/ · Config flows: https://contributors.home-assistant.io/core/integrations/config-flow/ · Data fetching + coordinator: https://contributors.home-assistant.io/core/integrations/fetching-data/ · Setup failures: https://contributors.home-assistant.io/core/integrations/setup-failures/ · Blocking operations: https://contributors.home-assistant.io/core/internals/blocking-operations/ · Core's own agent guidelines, written for core's tree, so `homeassistant/components/<domain>/` reads as `custom_components/<domain>/`: https://raw.githubusercontent.com/home-assistant/core/dev/.claude/skills/ha-integration-knowledge/SKILL.md · Real examples: https://github.com/home-assistant/core/tree/dev/homeassistant/components |
| **Manifest** | adding or changing a `manifest.json` key | `reference/scaffold.md` | Manifest: https://contributors.home-assistant.io/core/integrations/manifest/ |
| **Panel** | building or fixing an integration that serves a panel — how it is built and served; how it looks is the Panel design row | `reference/panels.md` | — |
| **Panel design** | changing how a panel looks — the CSS or markup of a Lit/TS panel web component: sizing, typography, colour, spacing, layout | `reference/panel-design.md` | Material 3 type scale: https://m3.material.io/styles/typography/type-scale-tokens · Material 3 states and touch targets: https://m3.material.io/foundations/interaction/states/overview · HA theme properties: https://github.com/home-assistant/frontend/tree/dev/src/resources/theme · Theme variables a user may override: https://www.home-assistant.io/integrations/frontend/#supported-theme-variables |
| **Test** | writing or fixing tests, mocking at the boundary, or a suite that fails before any test runs | `reference/testing.md` | — |
| **Lint** | hygiene pass over existing code | `reference/lint.md`, `reference/scaffold.md` | — |
| **Tier** | claiming a quality-scale tier, and the canonical rule set behind it | `reference/quality-scale.md` | Quality scale: https://contributors.home-assistant.io/core/quality-scale/ · Core's procedure for proving a rule, written for core's tree, so `homeassistant/components/<domain>/` and `tests/components/<domain>/` read as `custom_components/<domain>/` and `tests/`, its `script.hassfest`, `.strict-typing` and requirements-file steps run in core only, and its brands step checks `brand/` instead: https://raw.githubusercontent.com/home-assistant/core/dev/.claude/skills/ha-quality-scale-verify/SKILL.md, whose rule links point at an archived repository — read each rule at `https://contributors.home-assistant.io/core/quality-scale/<rule>/index.md` |
| **Debug** | a root cause is about to be named | `reference/discipline.md` | — |
| **Commit / PR** | writing a commit subject, a PR title or a PR body | `reference/commits.md` | — |
| **Merge** | a check is red, or a merge is about to happen | `reference/discipline.md` | — |
| **Workflow** | writing or reviewing a CI file, and what a copy may change | `reference/github-actions.md` | — |
| **Dependabot** | configuring or debugging Dependabot, including the callers' pins and what it cannot reach | `reference/dependabot.md` | — |
| **Release** | cutting or gating a release once the release process is set up, including an rc, or touching the version in `manifest.json` | `reference/versioning.md` | — |
| **Catalog** | getting the integration into the default catalog HACS and the Marketplace read, or putting its My links in the README | `reference/scaffold.md` | Get into the catalog: https://contributors.home-assistant.io/marketplace/guides/catalog/ |
| **Repo setup** | configuring the repository on GitHub: token, required checks, dependency graph, supply chain | `reference/github-setup.md` | — |
| **Audit** | auditing a repository against this skill | `reference/audit.md`, `reference/lint.md` | — |
| **Freshness** | acting on a pin, SHA, count or Home Assistant release number, or asking whether a cached value is still true | `reference/freshness.md` | What a release changed or deprecated: https://contributors.home-assistant.io/blog/ |
