# Quality scale — target Platinum

Read this when claiming a tier: the canonical rule set, and what a claim must have behind
it.

**A rule marked `done` has a test that exercises it — nothing in CI runs the integration.**

## Contents

1. Claiming a tier
2. Step 1: Scaffold `quality_scale.yaml` from the start
3. Step 2: Set every rule in the canonical set
4. Step 3: Prove every `done` with a test
5. Step 4: Claim the tier in the manifest only once it is fully met
6. Cases
7. A local-push MQTT device integration — Step 2

## Claiming a tier

### Step 1: Scaffold `quality_scale.yaml` from the start

Write it before the code, including when you are modifying an existing integration that
lacks one, and treat it as the definition-of-done. Ship it as a tracking ledger first.

```yaml
rules:
  config-flow: done
  test-coverage: done
  diagnostics:
    status: exempt
    comment: Device exposes no sensitive runtime data worth redacting.
```

- Valid statuses: `done`, `todo`, `exempt`; `exempt` requires a `comment`.
- `exempt` with a comment is always the honest alternative.
- `todo` is fine indefinitely above any claimed tier.

### Step 2: Set every rule in the canonical set

Each rule takes `todo`, `done` or `exempt` as appropriate, and all of them must appear in
`quality_scale.yaml`.

- 🥉 **Bronze** — UI setup, basic coding standards, automated tests for config, basic docs
- 🥈 **Silver** — + code owners, auto-recovery from errors without log spam, reauth flow
  (`async_step_reauth`), full test coverage
- 🥇 **Gold** — + auto-discovery, full translations, reconfigure flow
  (`async_step_reconfigure`), diagnostics
- 🏆 **Platinum** — + complete type annotations, fully async (no blocking I/O),
  `always_update=False` where applicable, all HA coding standards

> **Note:** `PlatformNotReady` is for legacy `async_setup_platform` only — config-entry
> integrations use `ConfigEntryNotReady` instead.

**Canonical rule set — a snapshot; rules change. Re-verify per its row in
`reference/freshness.md`.** Tier membership is defined by `ALL_RULES` in core's
`script/hassfest/quality_scale.py`, and that is the source for which tier a rule sits in —
not its name. Each rule is documented at
`developers.home-assistant.io/docs/core/integration-quality-scale/rules/<rule-name>/`, under
the index at `developers.home-assistant.io/docs/core/integration-quality-scale/`, which is
the page the freshness row re-derives from.

- **Bronze:** `action-setup`, `appropriate-polling`, `brands`, `common-modules`, `config-flow-test-coverage`, `config-flow`, `dependency-transparency`, `docs-actions`, `docs-high-level-description`, `docs-installation-instructions`, `docs-removal-instructions`, `docs-triggers`, `docs-conditions`, `entity-event-setup`, `entity-unique-id`, `has-entity-name`, `runtime-data`, `test-before-configure`, `test-before-setup`, `unique-config-entry`
- **Silver:** `config-entry-unloading`, `log-when-unavailable`, `entity-unavailable`, `action-exceptions`, `reauthentication-flow`, `parallel-updates`, `test-coverage`, `integration-owner`, `docs-installation-parameters`, `docs-configuration-parameters`
- **Gold:** `entity-translations`, `entity-device-class`, `devices`, `entity-category`, `entity-disabled-by-default`, `discovery`, `stale-devices`, `diagnostics`, `exception-translations`, `icon-translations`, `reconfiguration-flow`, `dynamic-devices`, `discovery-update-info`, `repair-issues`, `docs-use-cases`, `docs-supported-devices`, `docs-supported-functions`, `docs-data-update`, `docs-known-limitations`, `docs-troubleshooting`, `docs-examples`
- **Platinum:** `async-dependency`, `inject-websession`, `strict-typing`

### Step 3: Prove every `done` with a test

Green hassfest and a green audit together prove exactly what Step 4 says and nothing more;
neither **runs the integration**, so nothing in CI can tell you `diagnostics.py` actually
redacts, the reconfigure flow works, `async_remove_config_entry_device` returns correctly,
or that a `translation_key` used in code resolves in `strings.json`.

Each of these needs its own test, not just the code:

- `reconfiguration-flow` — a reconfigure-success and a reconfigure-error flow test
- `diagnostics` — asserts the payload shape **and** that secrets are `**REDACTED**`
- `stale-devices` — `async_remove_config_entry_device` → `False` while the device is live,
  `True` once it's gone
- `exception-translations` / `entity-translations` / `icon-translations` — a test that
  scrapes the `translation_key`s used in code and asserts each exists in `strings.json`,
  which catches a typo'd key that hassfest passes

A rule that is genuinely untestable is `exempt` with a comment, not an unproven `done`.

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

**Fix:** the common `exempt`s are `appropriate-polling` (push, no polling),
`reauthentication-flow` (no integration-level auth), `inject-websession` (no cloud HTTP),
`async-dependency` (only sync libs run in executor) and `dynamic-devices` (one device per
entry).
