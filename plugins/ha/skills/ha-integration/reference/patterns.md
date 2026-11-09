# Implementation patterns, file structure and typing

Read this when writing code under `custom_components/` — its layout, entry setup and unload,
typing, or a deprecated API no topic file owns. The rest is `reference/config-flows.md`,
`reference/entities.md`, `reference/fetching-data.md`, `reference/services.md`, panel code
`reference/panels.md`, tests `reference/testing.md`, the manifest *Step 4: Write `manifest.json`* in `reference/scaffold.md`.

**Pick the shape Home Assistant already models, then write that shape the way core writes
it.**

## Contents

1. Writing code in `custom_components/`
2. Step 1: Lay out the files by responsibility
3. Step 2: Pick the shape HA models
4. Step 3: Wire the entry setup and unload
5. Step 4: Type it, and suppress nothing
6. Cases
7. `ConfigEntry` mutation — Step 3
8. `Setup failed for custom integration` — Step 3
9. Repair issues that belong to a config entry — Step 3
10. Deprecated platform APIs — Step 1
11. `TYPE_CHECKING` for expensive or circular imports — Step 4
12. Typed `ConfigEntry` — Step 4

## Writing code in `custom_components/`

### Step 1: Lay out the files by responsibility

The developer docs' set — https://contributors.home-assistant.io/core/integrations/file-structure/
— plus the splits the quality scale asks for and the ones this skill adds. If `__init__.py`
exceeds ~100 lines of logic, extract. `api.py` is the split that matters most: it keeps the
calls to the device or service apart from the HA lifecycle, so it is unit-testable without HA.

| File | Holds | Taken from |
|---|---|---|
| `__init__.py` | `async_setup_entry`, `async_unload_entry`, `async_migrate_entry` only — no business logic | the file-structure page names it; the no-business-logic constraint is this skill's |
| `<platform>.py` | one per HA platform — `sensor.py`, `switch.py`, `light.py`, `button.py`, … | the file-structure page |
| `coordinator.py` | `DataUpdateCoordinator` subclass | the `common-modules` rule, https://contributors.home-assistant.io/core/quality-scale/common-modules/ |
| `entity.py` | shared base entity class when several platforms extend the same base | the `common-modules` rule |
| `config_flow.py` | config and options flows | the `config-flow` rule in `reference/quality-scale.md` |
| `diagnostics.py` | `async_get_config_entry_diagnostics` | the `diagnostics` rule in `reference/quality-scale.md` |
| `api.py` | all I/O to the device or service, through the library that speaks its protocol — no HA imports | this skill |
| `models.py` | dataclasses and type aliases for device data | this skill |
| `const.py` | constants only — no imports from other local modules | this skill |
| `services.py` | `async_setup_services(hass)` called from `async_setup` | this skill |
| `migration.py` | `async_migrate_entry` logic when it is complex; import into `__init__.py` | this skill |
| `helpers.py` / `util.py` | pure functions shared across platforms | this skill |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| protocol parsing, a device state machine or other domain logic inside the integration | a library of its own on PyPI, which `api.py` calls and `requirements` in `manifest.json` pins | an integration is a thin wrapper | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a workaround in the integration for a limit of its library | a fix in the library, then the new pin in `requirements` | the fix belongs where every user of the library gets it | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |

### Step 2: Pick the shape HA models

- An entity platform when the thing has state a user would see in history or on a dashboard.
- A registered service when it is an action with no state.
- An option on the config entry when it is configuration.

> **Note:** notify is an entity platform because a notifier is addressable; a one-shot "send
> this" with no addressable target is a service.

### Step 3: Wire the entry setup and unload

1. `PLATFORMS` lists the platforms this integration provides, and each name has a module
   beside it — `async_forward_entry_setups` imports `<domain>/<platform>.py` per name.
2. `async_setup_entry` stores state on `entry.runtime_data`, then forwards:
   `await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)`.
3. `async_unload_entry` mirrors it with no `async_shutdown` call, returning
   `await hass.config_entries.async_unload_platforms(entry, PLATFORMS)`: a coordinator built with
   `config_entry=entry` registers its shutdown with `entry.async_on_unload` in its `__init__`, and
   `ConfigEntry.async_unload` runs it once the unload succeeds — `helpers/update_coordinator.py`
   and `config_entries.py` in core, at the `.0` tag of the release row in `reference/freshness.md`.
4. If setup creates a device, add `async_remove_config_entry_device` so a user can remove it.
   Type its device parameter `AnyDeviceEntry` (`DeviceEntry | ChildDeviceEntry`), since from
   2026.9 Home Assistant hands it a child device too — `_async_remove_device` in
   `homeassistant/components/config/device_registry.py` at the `2026.9.0` tag.
5. If the entity carries `_attr_translation_key`, add the matching block to
   `translations/en.json` — `entity-translations` in `reference/quality-scale.md`.

What the audit checks of this list at PR time, and how, is *What the audit checks now* in
ha-integration-ci's README,
https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md.

| Scenario | Choice |
|---|---|
| the stored `entry.data` schema changes | *Config entry migration — Step 1* in `reference/config-flows.md` |
| `async_forward_entry_setups` left to run past `async_setup_entry`, in `hass.async_create_task` or another task setup does not wait for | `await` it in `async_setup_entry`, item 2; from 2026.11.0 the forward raises `HomeAssistantError` when it finds the setup finished before it, where 2026.10.0 logged it — `ConfigEntries.async_forward_entry_setups` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.10.0` tag |
| setup signs in through the OAuth2 helper | *OAuth2 errors at setup — Step 1* in `reference/config-flows.md` |
| a service, static path, WebSocket command or panel registered once for the whole integration | *Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 1* in `reference/services.md` |
| the integration raises a repair issue about one config entry | *Repair issues that belong to a config entry — Step 3* |
| the integration changes how it builds a backup agent's `unique_id`, and with it the agent's ID | from 2026.11.0, `async_get_manager(hass).async_rename_agent(f"{DOMAIN}.{old_unique_id}", f"{DOMAIN}.{new_unique_id}")`, from `homeassistant.components.backup`, before the agent loads under its new ID, so users keep its backup settings; it raises `ValueError` once the new ID is loaded, or when both IDs have settings and `overwrite_orphaned_settings=True` is not passed; `backup` goes in `after_dependencies`, *Step 4: Write `manifest.json`* in `reference/scaffold.md` — `BackupManager.async_rename_agent` in `homeassistant/components/backup/manager.py` and `async_get_manager` in `homeassistant/components/backup/__init__.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `manager.py` at the `2026.10.0` tag |
| the integration claims Home Assistant 2026.11.0 or later | `async_setup_entry`, `async_unload_entry` and `async_migrate_entry` may return `None` and raise a `ConfigEntry*` exception on failure; unload is then `await hass.config_entries.async_unload_platforms_or_raise(entry, PLATFORMS)`, which raises a translated `ConfigEntryError` when a platform fails to unload — `_async_process_entry_method_result` and `ConfigEntries.async_unload_platforms_or_raise` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.10.0` tag |
| it claims an older release | all three return a boolean, `True` on success: below 2026.11.0 a `None` fails the setup, the unload or the migration — `ConfigEntry.__async_setup_with_context`, `ConfigEntry.async_unload` and `ConfigEntry.async_migrate` in `homeassistant/config_entries.py` at the `2026.10.0` tag |
| `async_setup_entry` or `async_unload_entry` returns `False` | from 2026.11.0, a `ConfigEntryError` logged with its traceback, whose reason is the generic *Failed to set up the config entry.* or *Failed to unload the config entry.*; for a reason that says what failed, raise `ConfigEntryError` with your own `translation_key` — `_async_process_entry_method_result` in `homeassistant/config_entries.py` and the `exceptions` of `homeassistant/components/homeassistant/strings.json`, at the `.0` tag of the release row in `reference/freshness.md` |

### Step 4: Type it, and suppress nothing

The `strict-typing` rule in `reference/quality-scale.md`. Every file passes *Step 2: Run mypy*
in `reference/lint.md`, under the shipped `mypy.ini`, with zero errors, before a PR is ready.

- **Never add `from __future__ import annotations`** — HA's Python floor (the row in
  `reference/freshness.md`) is past the release where PEP 649 made annotation evaluation
  deferred natively, core bans it, and the shipped `pyproject.toml` enforces the ban through
  ruff (`TID251`).
- **Import HA's own types rather than re-typing them** — `DeviceInfo` from
  `homeassistant.helpers.device_registry`, `AddConfigEntryEntitiesCallback` from
  `homeassistant.helpers.entity_platform` for a config-entry platform's
  `async_add_entities` (`AddEntitiesCallback` is the YAML platform's), `ConfigType`,
  `DiscoveryInfoType` and `StateType` from `homeassistant.helpers.typing`.
- **Mark every method that overrides a base-class method with `@override`**, imported
  `from typing import override` — the `mypy.ini` enables `explicit-override`, so an
  unmarked `async_added_to_hass`, `device_info` or `async_step_user` fails the run:
  `@override` on the line above `async def async_added_to_hass(self) -> None:`.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `# type: ignore` to silence a typing error | fix the type | under `strict-typing` a suppression is a violation, not a shortcut, and the `mypy.ini` enables `ignore-without-code`, so a codeless one fails the run outright | https://contributors.home-assistant.io/core/quality-scale/strict-typing/, and `templates/mypy.ini` |
| `# type: ignore[import-untyped]` on a stubless third-party import | nothing — import it plainly | the `mypy.ini` disables `import-untyped` and fails an unused ignore, so the leftover one is the error | `templates/mypy.ini` |
| `hass.data[DOMAIN][entry.entry_id]`, which is untyped | `entry.runtime_data` on a typed `ConfigEntry` — *Typed `ConfigEntry` — Step 4* | the alias carries the runtime type, so no cast is needed | https://contributors.home-assistant.io/core/quality-scale/runtime-data/ |

| what | lands in | do now | do then |
|---|---|---|---|
| `UNDEFINED` and `UndefinedType` from `homeassistant.helpers.typing`, deprecated for `Undefined`, which is both the default and the type | 2026.12 | `UNDEFINED`, typed `UndefinedType`, since `Undefined` does not exist at 2026.11.0 | `from homeassistant.helpers.typing import Undefined`, then `variable: str \| Undefined \| None = Undefined` |

## Cases

### `ConfigEntry` mutation — Step 3
- Never mutate `ConfigEntry` directly — always use `hass.config_entries.async_update_entry(entry, data=..., options=...)`

### `Setup failed for custom integration` — Step 3

**Symptom:** `Setup failed for custom integration '<domain>': <message>` at ERROR, before any
config entry of the domain is set up, and a notification saying so.

| Scenario | Choice |
|---|---|
| where each message was read | `_async_setup_component` and `_log_error_setup_error` in `homeassistant/setup.py`, `RequirementsNotFound` in `homeassistant/requirements.py` and `DependencyError` in `homeassistant/exceptions.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `Integration not found.`, on a line reading `Setup failed for '<domain>'` with no `custom integration` in it | no integration of that domain could be loaded — its folder, or its `manifest.json`; a repair issue follows where config entries of the domain exist |
| `Unable to import component: <error>`, with a traceback | importing `__init__.py` raised `ImportError` — a name a Home Assistant release moved or removed, or a library missing from `requirements`; the traceback's last frame names the import |
| `Requirements for <domain> not found: [<requirement>].` | pip could not install it, after three tries, under the `package_constraints.txt` the release carries; a pin those constraints contradict never installs |
| `Could not setup dependencies: <domain>, …` | an integration in `dependencies` failed its own setup, and its own line, earlier, says why |
| `Invalid config.` | the YAML under the domain's key failed `CONFIG_SCHEMA`; the lines before it say where |
| `No setup or config entry setup function defined.` | `__init__.py` defines none of `async_setup`, `setup` and `async_setup_entry` |
| `Integration failed to initialize.` | `async_setup` returned `False` |
| `Integration '<domain>' did not return boolean if setup was successful. Disabling component.` | `async_setup` returned something other than `True` or `False` — `None`, from a missing `return` |
| an exception out of `async_setup` | not this line: `Error during setup of component <domain>: <error>`, with the traceback |
| a failure in `async_setup_entry` | not this line either; what Home Assistant logs for each exception is *Logging — Step 1* in `reference/fetching-data.md` |

### Repair issues that belong to a config entry — Step 3

Through `from homeassistant.helpers import issue_registry as ir`.

| Rule | Value |
|---|---|
| where each row was read | `async_create_issue`, `async_delete_issue`, `async_refresh_issues`, `async_keep_issue`, `IssuesRefresh`, `IssueRegistry.async_get_or_create`, `IssueRegistry.async_clear_config_entry` and `IssueRegistry.async_is_hidden` in `homeassistant/helpers/issue_registry.py`, at the `.0` tag of the release row in `reference/freshness.md`; the compatibility floor, the same file at the `2026.10.0` tag |
| the compatibility floor | 2026.11.0; below it no issue belongs to an entry and there is no refresh, so the integration deletes its own issues |
| an issue about one config entry | `ir.async_create_issue(…, config_entry_id=entry.entry_id)`; Home Assistant deletes it when the entry is removed, and hides it from Repairs while the entry is disabled |
| its `issue_id` | still unique within the domain, so an issue several entries can raise carries the entry ID in it |
| a `config_entry_id` no entry has | `HomeAssistantError` |
| creating an issue that already exists | replaces its `config_entry_id`, also when the call leaves it out |
| an issue created before it carried `config_entry_id` | belongs to no entry until it is created again, so a persistent one that never is still needs deleting in `async_remove_entry` |
| re-checking a set of issues | `with ir.async_refresh_issues(hass, DOMAIN, issue_id_pattern="firmware_too_old_", config_entry_id=entry.entry_id):` round the code that creates the issues still valid; when the block ends it deletes the issues of its set not created or kept since it began, so one the user ignored stays ignored |
| the set | `issue_id_pattern`, a regular expression matched from the start of the issue ID; or `issue_ids`, a list; or neither, for every issue of the domain; `config_entry_id` narrows it to that entry's issues |
| an issue that could not be checked, such as a device that did not answer | `ir.async_keep_issue(hass, DOMAIN, issue_id)`, or `async_keep` on the `IssuesRefresh` the block returns |
| an exception out of the block | cancels the refresh, which then applies only the deletes deferred to it |
| an issue deleted by an entity removed during a reload, which may create it again | `ir.async_delete_issue(hass, DOMAIN, issue_id, defer_to_refresh=True)`, which leaves it for an active refresh whose set holds it |
| where the refresh runs | in the event loop only |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| deleting every issue of a kind, then creating the ones still valid | `ir.async_refresh_issues` round the creates | each valid issue disappears and comes back, and one the user ignored shows again | https://contributors.home-assistant.io/blog/2026/10/28/issue-registry-refresh/ |
| deleting an entry's issues in `async_unload_entry` | `config_entry_id` on each issue | a reload unloads the entry too, so the issue flickers | https://contributors.home-assistant.io/blog/2026/10/28/issue-registry-refresh/ |
| `ir.async_refresh_issues` round `async_forward_entry_setups` | the refresh round the code that checks the issues | the forward does not raise when a platform fails or is retried later, so the refresh deletes issues that were never checked | https://contributors.home-assistant.io/blog/2026/10/28/issue-registry-refresh/ |

| what | lands in | do now | do then |
|---|---|---|---|
| `config_subentry_id` on `ir.async_create_issue`, which deletes the issue with its subentry; it needs `config_entry_id`, and the subentry must belong to that entry | 2026.12 | `config_entry_id` alone, with the subentry ID in the `issue_id` | add `config_subentry_id=subentry.subentry_id` |

### Deprecated platform APIs — Step 1

The deprecations, and the calls core's docstrings steer a caller away from, that a custom integration can meet with no section of their own here, in
`reference/config-flows.md` or in `reference/entities.md`.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `mqtt.publish()` or `async_publish()` with `qos=None` or `retain=None` | the defaults, or typed values — the parameters are `qos: int = 0` and `retain: bool = False` | the `None` fallbacks stop working in **2027.6** | `async_publish` in `homeassistant/components/mqtt/client.py` |
| using a condition object as a callable | `async_from_config()` from `homeassistant.helpers.condition`, then `async_check()`, then `async_unload()`; a script is `async_run()` then `await script.async_unload()` | the post gives **2027.1** for the end of the callable form; core at the `.0` tag of the release row in `reference/freshness.md` attaches no warning to it | https://contributors.home-assistant.io/blog/2026/05/13/condition-script-api-changes/ |
| `BrowseMediaSource(domain=None)` | your own domain; the node listing every media source is `RootBrowseMediaSource` | `domain` is a required `str` now — a hard change with no deprecation period | `BrowseMediaSource` and `RootBrowseMediaSource` in `homeassistant/components/media_source/models.py` |
| `async_initialize_triggers(home_assistant_start=…)` | stop passing it; `hass.async_add_startup_job` for work at startup | it already has no effect; removed in **2027.8.0** | `async_initialize_triggers` in `homeassistant/helpers/trigger/__init__.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `modbus.get_hub(hass, name)`, attaching to a hub the user configured in YAML | collect the connection details in your own config flow, then `async_get_unit(hass, entry, params, unit_id)` | logged from 2026.10; stops working in **2027.10** | `get_hub` in `homeassistant/components/modbus/__init__.py` and `async_get_unit` in `homeassistant/components/modbus/connection.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| the `configurator` integration's `async_request_config` or `request_config` | a config flow and config entries | logged from 2026.10 on those two calls; the integration is removed in **2027.10** | `_report_deprecation` in `homeassistant/components/configurator/__init__.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `hass.bus.async_listen(…, run_immediately=…)` or `async_listen_once(…, run_immediately=…)` | drop the argument | passing `True` or `False` raises from 2026.10 | `EventBus.async_listen` and `EventBus.async_listen_once` in `homeassistant/core.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `DISABLED_USER`, imported from `homeassistant.config_entries` | `ConfigEntryDisabler.USER`, a `StrEnum` member whose value is the same `"user"` | removed in 2026.11 with no deprecation logged before it, so the import raises `ImportError` and the integration does not load | `ConfigEntryDisabler` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md`; `DISABLED_USER = ConfigEntryDisabler.USER.value` in the same file at the `2026.10.0` tag |
| an `llm.Tool` whose `async_call` returns a JSON object | `llm.ToolResult(data=…)`, with `error=True` when the call failed, from 2026.10.0 | logged now; stops working in **2027.11.0** | `APIInstance.async_call_tool` in `homeassistant/helpers/llm.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.9.0` tag |
| `ToolResultContent.tool_result` | `ToolResultContent.result`, the `llm.ToolResult` itself, from 2026.10.0 | logged now; stops working in **2027.11.0** | `ToolResultContent.tool_result` in `homeassistant/components/conversation/chat_log.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.9.0` tag |
| an `llm.Tool` with no `integration` | `integration = DOMAIN` on the tool class | logged now, and the domain filled in from the tool's module; stops working in **2027.10** | `report_untagged_tool` in `homeassistant/helpers/llm.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `api.async_get_api_instance(llm_context)`, called on an `llm.API` | `await llm.async_get_api(hass, api_id, llm_context)`, or from 2026.11.0 `await llm.async_get_authorized_api_instance(api, llm_context)` for an `API` already held; and from 2026.11.0, `requires_admin = True` on an `llm.API` of your own whose tools only an admin may use | the direct call skips the admin check, so a non-admin reaches an API that requires an admin, where both helpers raise `Unauthorized` | `async_get_authorized_api_instance`, `API.requires_admin` and the docstring of `API.async_get_api_instance` in `homeassistant/helpers/llm.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.10.0` tag |

> **Note:** a condition platform may implement `_async_setup()` and `_async_unload()` for async
> set-up and teardown, and from 2026.10.0 `_async_track_changes(action)`, calling `action` when
> its result may change, with `needs_polling` `False` once nothing else changes it; all optional.

### `TYPE_CHECKING` for expensive or circular imports — Step 4
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def uses_hass_in_annotations_only(hass: HomeAssistant) -> None:
    """The import never runs; deferred annotations resolve the name when asked."""
```

### Typed `ConfigEntry` — Step 4

Alias the entry to its runtime type so `entry.runtime_data` is not untyped:
```python
# In coordinator.py or models.py:
from homeassistant.config_entries import ConfigEntry

type MyConfigEntry = ConfigEntry[MyCoordinator]


# In platform files:
async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the platform from the typed entry."""
    coordinator = entry.runtime_data  # typed as MyCoordinator, no cast needed
    async_add_entities(MySensor(coordinator, desc) for desc in SENSORS)
```
