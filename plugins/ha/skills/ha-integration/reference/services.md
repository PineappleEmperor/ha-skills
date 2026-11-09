# Custom services

Read this when registering a custom service, writing its `services.yaml` and translations, or
when an action does nothing.

**Register integration-global resources in `async_setup`, not `async_setup_entry`.**

## Contents

1. Registering custom services
2. Step 1: Register the custom services
3. Cases
4. An action that does nothing — Step 1
5. `services.yaml` + `translations/en.json` — Step 1
6. Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 1

## Registering custom services

### Step 1: Register the custom services

| Rule | Value |
|---|---|
| where to register | `async_setup`, not `async_setup_entry` — *Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 1* below says why |
| where the registration code lives | `services.py`, in `@callback def async_setup_services(hass: HomeAssistant) -> None`, which `async_setup` calls; it is no coroutine and takes `hass` alone, and a module-level function of `services.py` that it calls, and that is no coroutine either, may register too; ha-integration-ci v5 fails a registration anywhere else (W7452) and any other signature (W7453) — `checkers/actions/services_module.py` in core's `packages/pylint-home-assistant/pylint_home_assistant/`, at the `.0` tag of the release row in `reference/freshness.md`, and the *v5.0.0's edits* bullet of *The version model* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| an entity-targeted action | `async_register_platform_entity_service()` |
| where a service is documented | `services.yaml`, with its icons in `icons.json` |
| a device dropdown | `selector: device` with `integration: {domain}`, never `selector: config_entry`, which the HA frontend labels "Integration" |
| resolving that device to your own config entry | `async_get_device_and_config_entry_for_domain`, in the handler — the helper core added in 2026.9 |
| a call with no target | `hass.services.async_call(DOMAIN, svc, …)` reaches every config entry, so pass your own `entry_id`/`device_id` and filter on it unless the call is a deliberate bulk one |
| a key the schema guarantees | `call.data[KEY]`, not `call.data.get(KEY)`, so a wrong assumption fails at once — `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a value the schema or the entity filter already enforces | no second check in the handler; guard only a value that bypasses validation or is transformed on the way — `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| the names of an integration's first actions, and their fields | a `<Prefix>Service` and a `<Prefix>ServiceArgument` `StrEnum`, with the integration's usual class prefix — `MyDeviceService`, `MyDeviceServiceArgument` — in `services.py`, or in `const.py` when other modules need them; a member for each action registered and each field `services.yaml` lists, and none for an action not registered; the members, never a raw string or a `SERVICE_*`, `ATTR_*` or `CONF_*` constant, in the registration, the schema keys and the `call.data` lookups, while `config_entry_id`, `device_id` and `entity_id` keep the `homeassistant.const` constants; an integration that has actions already need not convert them — `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |

```python
from homeassistant.helpers.device_registry import (
    async_get_device_and_config_entry_for_domain,
)

device, entry = async_get_device_and_config_entry_for_domain(
    hass, call.data[ATTR_DEVICE_ID], domain=DOMAIN
)
```

**What it returns — `async_get_device_and_config_entry_for_domain` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md`, and at the `2026.9.0` tag for the below-2026.10.0 row:**

| Scenario | Choice |
|---|---|
| an unknown device id | `(None, None)` |
| a child device | the child, typed `AnyDeviceEntry`, and its config entry when your domain owns it; `include_child_devices=False` gives `(None, None)` |
| `include_main_devices=False` | `(None, None)` for a main or composite device id, so only a child resolves |
| below 2026.10.0 | a child device id gives `(None, None)`, and passing `include_child_devices` or `include_main_devices` raises `TypeError` |
| a main device no config entry of your domain owns | `(device, None)` |
| a pre-migration composite device id | a matching split device and its config entry, which is the case a hand-written loop gets wrong |
| a composite device id no split matches | the restored composite device, and `None` |
| whether that config entry is loaded | not checked — keep your own `ConfigEntryState.LOADED` test |

## Cases

### An action that does nothing — Step 1

**Symptom:** an action aimed at the integration's entities returns with no error and
changes nothing.

| Scenario | Choice |
|---|---|
| where each row was read | `_resolve_entity_service_call_entities` in `homeassistant/helpers/service.py`, and `async_extract_referenced_entity_ids` and `SelectedEntities.log_missing` in `homeassistant/helpers/target.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| an entity that is unavailable | skipped; named only when targeted by its own id, in `Referenced entities <ids> are missing or not currently available` at WARNING |
| an entity reached through a device, an area or a floor, or a device or area carrying a label | skipped when it carries an `entity_category` or is hidden, so a `CONFIG` or `DIAGNOSTIC` entity never receives an action aimed at its device |
| an entity carrying the label itself | skipped when it is hidden |
| an entity the target's `exclude` block names, or reaches through a device, area, floor or label | skipped, from 2026.11.0, however the rest of the target reaches it, `entity_id: all` included; a target holding only an `exclude` block targets nothing — `TargetSelection` and `async_extract_excluded_entity_ids` in `target.py`; the floor, `target.py` at the `2026.10.0` tag |
| an entity without the action's required features or device class | skipped when reached through a device, area, floor or label; targeted by its own id, the call raises `ServiceNotSupported` |
| no entity left to call | the call returns having called nothing, unless it asked for a response, which raises `Service call requested response data but did not match any entities` |
| an action that reaches more entities than it was aimed at | the "a call with no target" row of Step 1 |

### `services.yaml` + `translations/en.json` — Step 1

| Rule | Value |
|---|---|
| what hassfest checks of a custom integration's actions | not their `name` or `description`, which it accepts in `services.yaml` too — `script/hassfest/services.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| what this stack checks of them | the translation check under *Implementation notes* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| what `services.yaml` carries | field **structure** only — selectors, `required`, `default`, collapsible `sections` |
| what `translations/en.json` carries | every name and description, under a top-level `services` key: `services.{svc}.name/description`, `.fields.{key}.name/description`, `.sections.{key}.name` |
| a field key nested in a `sections` block in `services.yaml` | flat in `translations/en.json` all the same |
| what Home Assistant reads | `translations/<language>.json`, with `en.json` loaded first as the fallback for every other language, and never `strings.json` — `_async_get_component_strings` in `homeassistant/helpers/translation.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `strings.json` | none in a custom integration: core compiles it into `translations/` with a step that runs only in core, so a custom integration ships `translations/en.json` complete, and any other language beside it, under *Custom integrations* at https://contributors.home-assistant.io/core/integrations/translations/ |
| a `[%key:…%]` reference in a `translations/` file | none: nothing resolves it there, so the user sees the raw text; write every string out in full, as *Custom integrations* at https://contributors.home-assistant.io/core/integrations/translations/ says; the audit fails one in `en.json`, per *What the audit checks now* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| a literal URL in a description | forbidden by hassfest — `the string should not contain URLs`; use plain text, or a `{placeholder}` filled via `description_placeholders` in the flow step |
| a markdown image `![x]({url})` with a placeholder | fine, since it leaves no literal `http` |
| a collapsible service form | `fields: { appearance: { collapsed: true, fields: {...} } }` |
| what a section changes in the call | nothing — sections are UI-only, the call data stays flat, so the action's schema is unaffected |

### Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 1
The registration happens once per process; doing it per entry races when two entries set up in parallel. Claim the `hass.data` flag **before** the `await`, or both entries pass the check. The panel case, with the code, is *Step 3: Register the static path and the panel in `async_setup`* in `reference/panels.md`.
