# Quality scale — target Platinum

The canonical rule set and what each tier demands.

- The tiers and what each demands
- Scaffold `quality_scale.yaml` from the start
- Gate-enforced, on the claim rather than on the tests
- Prove the rule, don't just claim it — hassfest checks structure, not behaviour

## The tiers and what each demands

Generate `quality_scale.yaml` with each rule set to `todo` or `done` as appropriate.

| Tier | Key requirements |
|------|-----------------|
| 🥉 Bronze | UI setup, basic coding standards, automated tests for config, basic docs |
| 🥈 Silver | + code owners, auto-recovery from errors without log spam, reauth flow (`async_step_reauth`), full test coverage |
| 🥇 Gold | + auto-discovery, full translations, reconfigure flow (`async_step_reconfigure`), diagnostics |
| 🏆 Platinum | + complete type annotations, fully async (no blocking I/O), `always_update=False` where applicable, all HA coding standards |

Note: `PlatformNotReady` is for legacy `async_setup_platform` only — config-entry integrations use `ConfigEntryNotReady` instead.

`quality_scale.yaml` format:
```yaml
rules:
  config-flow: done
  test-coverage: done
  diagnostics:
    status: exempt
    comment: Device exposes no sensitive runtime data worth redacting.
```
Valid statuses: `done`, `todo`, `exempt` (exempt requires a `comment`).

### Scaffold `quality_scale.yaml` from the start

Write it before the code, including when you are modifying an existing integration that lacks one, and treat it as the definition-of-done — don't discover rules by hitting them. **What enforces it, and where:** for a custom integration hassfest reads the manifest only — it checks `quality_scale` is one of the known values and that a Silver-or-above claim names a `codeowners` entry — and never opens `quality_scale.yaml` (`validate_iqs_file` in `script/hassfest/quality_scale.py` returns for anything outside `homeassistant/components`). The rules that core's gate applies there are applied here by the skill's audit — which ones, and what each fails on, is *What the audit checks now* in ha-integration-ci's README. So: ship the yaml as a tracking ledger first, omit the manifest tier until a tier is fully met.

### Gate-enforced, on the claim rather than on the tests

The audit judges the claim, not the tests: it stays silent when nothing is marked `done` — a fresh scaffold claims nothing, so it has nothing to prove — and fails a `done` with nothing behind it, as that README says. One case it has that the README does not yet state: `test-coverage` marked `done` while a `frontend/` panel has no tests of its own. `exempt` with a comment is always the honest alternative; `todo` is fine indefinitely above any claimed tier.

### Prove the rule, don't just claim it — hassfest checks structure, not behaviour

⚠️ Green hassfest and a green audit together prove exactly what *Scaffold `quality_scale.yaml` from the start* says and nothing more; neither **runs the integration**, so nothing in CI can tell you `diagnostics.py` actually redacts, the reconfigure flow works, `async_remove_config_entry_device` returns correctly, or that a `translation_key` used in code resolves in `strings.json`. (For HA core those rules are enforced by human reviewers; for a custom integration nothing enforces them.) So **every rule you mark `done` must have a test that exercises it** — marking `done` off code-presence alone is "claiming compliance" without showing it. Concretely, each of these needs its own test, not just the code: `reconfiguration-flow` (a reconfigure-success + reconfigure-error flow test), `diagnostics` (asserts the payload shape **and** that secrets are `**REDACTED**`), `stale-devices` (`async_remove_config_entry_device` → `False` while the device is live, `True` once it's gone), `exception-translations`/`entity-translations`/`icon-translations` (a test that scrapes the `translation_key`s used in code and asserts each exists in `strings.json` — catches a typo'd key that hassfest passes). If a rule is genuinely untestable, it should be `exempt` with a comment, not an unproven `done`.

**Canonical rule set — a snapshot; rules change. Re-verify per its row in `reference/freshness.md`.** Tier membership is defined by `ALL_RULES` in core's `script/hassfest/quality_scale.py`, and that is the source for which tier a rule sits in — not its name, which is how two `docs-*` rules were once filed under Gold when hassfest has them at Bronze. Each rule is documented at `developers.home-assistant.io/docs/core/integration-quality-scale/rules/<rule-name>/`. All must appear in `quality_scale.yaml`:
- **Bronze:** `action-setup`, `appropriate-polling`, `brands`, `common-modules`, `config-flow-test-coverage`, `config-flow`, `dependency-transparency`, `docs-actions`, `docs-high-level-description`, `docs-installation-instructions`, `docs-removal-instructions`, `docs-triggers`, `docs-conditions`, `entity-event-setup`, `entity-unique-id`, `has-entity-name`, `runtime-data`, `test-before-configure`, `test-before-setup`, `unique-config-entry`
- **Silver:** `config-entry-unloading`, `log-when-unavailable`, `entity-unavailable`, `action-exceptions`, `reauthentication-flow`, `parallel-updates`, `test-coverage`, `integration-owner`, `docs-installation-parameters`, `docs-configuration-parameters`
- **Gold:** `entity-translations`, `entity-device-class`, `devices`, `entity-category`, `entity-disabled-by-default`, `discovery`, `stale-devices`, `diagnostics`, `exception-translations`, `icon-translations`, `reconfiguration-flow`, `dynamic-devices`, `discovery-update-info`, `repair-issues`, `docs-use-cases`, `docs-supported-devices`, `docs-supported-functions`, `docs-data-update`, `docs-known-limitations`, `docs-troubleshooting`, `docs-examples`
- **Platinum:** `async-dependency`, `inject-websession`, `strict-typing`

Common `exempt`s for a local-push MQTT device integration: `appropriate-polling` (push, no polling), `reauthentication-flow` (no integration-level auth), `inject-websession` (no cloud HTTP), `async-dependency` (only sync libs run in executor), `dynamic-devices` (one device per entry).

---
