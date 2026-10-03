# Quality scale — target Platinum

Read this when claiming a tier: the canonical rule set, and what a claim must have behind
it.

**A runtime rule marked `done` has a test that exercises it — nothing in CI runs the integration.**

## Contents

1. Claiming a tier
2. Step 1: Scaffold `quality_scale.yaml` from the start
3. Step 2: Set every rule in the canonical set
4. Step 3: Prove every `done`
5. Step 4: Claim the tier in the manifest only once it is fully met
6. Cases
7. A local-push MQTT device integration — Step 2

## Claiming a tier

### Step 1: Scaffold `quality_scale.yaml` from the start

Write it before the code, including when modifying an existing integration that lacks one.

```yaml
rules:
  config-flow: done
  test-coverage: done
  diagnostics:
    status: exempt
    comment: Device exposes no sensitive runtime data worth redacting.
```

- Valid statuses: `done`, `todo`, `exempt`; `exempt` requires a `comment`.
- `todo` is fine indefinitely above any claimed tier.

### Step 2: Set every rule in the canonical set

Each rule takes `todo`, `done` or `exempt` as appropriate, and all of them must appear in
`quality_scale.yaml`.

The set is a snapshot; re-verify it per its row in `reference/freshness.md`.

| tier | adds |
|---|---|
| Bronze | `action-setup`, `appropriate-polling`, `brands`, `common-modules`, `config-flow-test-coverage`, `config-flow`, `dependency-transparency`, `docs-actions`, `docs-high-level-description`, `docs-installation-instructions`, `docs-removal-instructions`, `docs-triggers`, `docs-conditions`, `entity-event-setup`, `entity-unique-id`, `has-entity-name`, `runtime-data`, `test-before-configure`, `test-before-setup`, `unique-config-entry` |
| Silver | `config-entry-unloading`, `log-when-unavailable`, `entity-unavailable`, `action-exceptions`, `reauthentication-flow`, `parallel-updates`, `test-coverage`, `integration-owner`, `docs-installation-parameters`, `docs-configuration-parameters` |
| Gold | `entity-translations`, `entity-device-class`, `devices`, `entity-category`, `entity-disabled-by-default`, `discovery`, `stale-devices`, `diagnostics`, `exception-translations`, `icon-translations`, `reconfiguration-flow`, `dynamic-devices`, `discovery-update-info`, `repair-issues`, `docs-use-cases`, `docs-supported-devices`, `docs-supported-functions`, `docs-data-update`, `docs-known-limitations`, `docs-troubleshooting`, `docs-examples` |
| Platinum | `async-dependency`, `inject-websession`, `strict-typing` |

| Rule | Value |
|---|---|
| which tier a rule sits in | `ALL_RULES` in core's `script/hassfest/quality_scale.py`, never the rule's name |
| where one rule is documented | `developers.home-assistant.io/docs/core/integration-quality-scale/rules/<rule-name>/` |

> **Note:** `PlatformNotReady` is for legacy `async_setup_platform` only — config-entry
> integrations use `ConfigEntryNotReady` instead.

### Step 3: Prove every `done`

The test requirement covers the rules about what the integration does when it runs. The
rest are proved by what they name:

| Rule | Value |
|---|---|
| a rule about runtime behaviour — a flow, setup, unload, an entity, an action | a test that exercises it |
| every `docs-*` rule | the documentation it asks for, read — no test can reach it |
| `brands`, `common-modules`, `dependency-transparency`, `integration-owner` | the file or manifest key the rule names, read |
| `async-dependency` | the dependency, read |
| `parallel-updates` | the `PARALLEL_UPDATES` module constant in each platform file, read |
| `strict-typing` | the mypy run — *Step 4: Type it, and suppress nothing* in `reference/patterns.md` |
| `test-coverage` | ha-integration-ci's `scripts/coverage_gate.py` — which modules it holds, and to what bar, is *The coverage gate* under *Implementation notes* in ha-integration-ci's README |

Each of these needs its own test, not just the code:

- `reconfiguration-flow` — a reconfigure-success and a reconfigure-error flow test
- `diagnostics` — asserts the payload shape **and** that secrets are `**REDACTED**`
- `stale-devices` — `async_remove_config_entry_device` → `False` while the device is live,
  `True` once it's gone
- `exception-translations` / `entity-translations` — a test that scrapes the
  `translation_key`s used in code and asserts each exists in `strings.json`, which catches a
  typo'd key that hassfest passes
- `icon-translations` — the same test against `icons.json`, for each `translation_key` whose
  entity has a custom icon; an entity that takes its icon from its device class needs none

A runtime rule no test can reach is `exempt` with a comment, not an unproven `done`; a rule
proved by reading is never `exempt` for want of a test.

### Step 4: Claim the tier in the manifest only once it is fully met

- For a custom integration hassfest reads the manifest only: it checks `quality_scale` is
  one of the known values, and that a Silver-or-above claim names a `codeowners` entry.
- hassfest never opens `quality_scale.yaml` — `validate_iqs_file` in
  `script/hassfest/quality_scale.py` returns for anything outside `homeassistant/components`.
- The rules that core's gate applies there are applied here by the skill's audit — which
  ones, and what each fails on, is *What the audit checks now* in ha-integration-ci's README.
- The audit judges the claim, not the tests: a fresh scaffold claims nothing, so it has
  nothing to prove; what a `done` must have behind it is *What the audit checks now* in
  ha-integration-ci's README.

## Cases

### A local-push MQTT device integration — Step 2

**Fix:** mark the four rules below `exempt`, each with the comment its row gives, and set
`async-dependency` as its row says.

| Rule | Value |
|---|---|
| `appropriate-polling` | exempt — the device pushes, so nothing polls |
| `reauthentication-flow` | exempt — no integration-level auth to renew |
| `inject-websession` | exempt — it makes no HTTP requests |
| `dynamic-devices` | exempt — one device per entry |
| `async-dependency` | exempt when the integration has no external dependency, or its dependencies do no I/O — the rule's two exceptions; `todo` while a dependency that does I/O is sync, since running it in the executor does not meet the rule |
