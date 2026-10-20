# Implementation patterns, file structure and typing

Read this when writing or changing the package under `custom_components/` — its Python,
`services.yaml` and `translations/`. Panel code is `reference/panels.md`, tests
`reference/testing.md`, the manifest *Step 4: Write `manifest.json`* in `reference/scaffold.md`.

**Pick the shape Home Assistant already models, then write that shape the way core writes
it.**

## Contents

1. Writing code in `custom_components/`
2. Step 1: Lay out the files by responsibility
3. Step 2: Pick the shape HA models
4. Step 3: Wire the entry setup and unload
5. Step 4: Type it, and suppress nothing
6. Cases
7. `config_flow.py` — Step 1
8. A config flow that will not open — Step 1
9. Notify platform — Step 1
10. Entity platform files — Step 1
11. An entity that is never added — Step 1
12. `EntityDescription` pattern — Step 1
13. `UpdateEntity` (firmware/OTA install) — Step 1
14. `DataUpdateCoordinator` (polling) — Step 1
15. Entity push subscriptions — Step 1
16. A connection that drops — Step 1
17. A reply the code does not expect — Step 1
18. A blocking call inside the event loop — Step 1
19. `ConfigEntry` mutation — Step 3
20. Logging — Step 1
21. Custom services — Step 1
22. An action that does nothing — Step 1
23. `services.yaml` + `translations/en.json` — Step 1
24. Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 3
25. Diagnostics platform — Step 1
26. Devices belong to one config entry — Step 3
27. Units: prefer the enumerators — Step 1
28. Config entry migration — Step 3
29. OAuth2 errors at setup — Step 3
30. `Setup failed for custom integration` — Step 3
31. A sign-in request that keeps coming back — Step 3
32. Deprecated platform APIs — Step 1
33. Announced for a release after 2026.10 — Step 1
34. `TYPE_CHECKING` for expensive or circular imports — Step 4
35. Typed `ConfigEntry` — Step 4

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

## Cases

### `config_flow.py` — Step 1

- `class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):` — `domain=` is a keyword
  argument, not a class attribute
- Include `OptionsFlow` when the integration has configurable options
- Implement `async_step_reauth` for expired or invalid auth — `reauthentication-flow` in
  `reference/quality-scale.md`
- Implement `async_step_reconfigure` for changing connection settings —
  `reconfiguration-flow` in `reference/quality-scale.md`

| Rule | Value |
|---|---|
| the schema library | `import probatio`, then `probatio.Schema`, `probatio.Required`, `probatio.Optional`, as core writes it; the shipped `pyproject.toml` bans `voluptuous` and `import probatio as vol`, as core's does, and `import probatio` sorts after the `homeassistant` imports, since `homeassistant` is third-party there |
| a `probatio.Schema` in a flow | one entry per line, left to `ruff format` |
| the `# fmt: off` fence | not earned here — a flow schema is a list of entries, not a table; *Alignment a human chose meets `ruff format` — Step 3* in `reference/scaffold.md` |

```python
DATA_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_HOST, default="192.168.1.1"): str,
        probatio.Required(CONF_PORT, default=8080): int,
    }
)
```

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `OptionsFlowWithConfigEntry` as the options flow's base class | `OptionsFlow`, reading `self.config_entry` | core is phasing it out and keeps it for custom integrations only | `OptionsFlowWithConfigEntry` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a config-entry update listener alongside a reloading method | drop the listener, or call `async_update_and_abort()` in place of `async_update_reload_and_abort()` and pass `reload_on_update=False` to `_abort_if_unique_id_configured()` | the integration reloads twice or races; an error from **2026.12** | `async_update_reload_and_abort` and `_abort_if_unique_id_configured` in `homeassistant/config_entries.py` |
| `FlowHandler.show_advanced_options`, or the `show_advanced_options` key in `FlowHandler.context` | group the extra fields in a schema `section` | the property returns `True` unconditionally and the context key is already gone; removed **2027.6** | `FlowHandler.show_advanced_options` in `homeassistant/data_entry_flow.py` |
| a `scan_interval`, `update_interval` or other polling-frequency field, in a config or options flow | an interval the integration sets itself — *`DataUpdateCoordinator` (polling) — Step 1* | a polling interval is not user-configurable | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a field asking for the config entry's name | a title the flow sets, which the user can change later in the UI; a `helper` integration may ask | the name is generated, not asked for | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a hand-written `SelectSelector` of device-class values | `DeviceClassSelector` | it carries HA's own values, so the hand-written translations for them go too | https://contributors.home-assistant.io/blog/2026/09/04/device-and-state-class-selectors/ |
| core's own text, copied word for word into an `abort` section of `translations/en.json`, `config_subentries` included, for an abort core translates itself — `reauth_successful` or `reconfigure_successful` from `async_update_reload_and_abort` or `async_update_and_abort` called without `reason`, `already_in_progress` from `async_set_unique_id`, `single_instance_allowed`, `no_devices_found` and `cloud_not_connected` from `single_config_entry` and the discovery and webhook flow helpers, an OAuth2 flow's shared reasons | delete it; to word one your own way, keep your text and pass `reason` to the helper, or `translation_domain=DOMAIN` to an OAuth2 flow's `async_abort` | those aborts carry the `homeassistant` translation domain, so the copy is never read | `async_update_reload_and_abort`, `async_update_and_abort`, `async_set_unique_id` and `ConfigEntriesFlowManager.async_init` in `homeassistant/config_entries.py`, `DiscoveryFlowHandler` and `WebhookFlowHandler` in `homeassistant/helpers/config_entry_flow.py`, and `AbstractOAuth2FlowHandler.async_abort` with `_SHARED_ABORT_REASONS` in `homeassistant/helpers/config_entry_oauth2_flow.py`, at the `.0` tag of the release row in `reference/freshness.md` |

### A config flow that will not open — Step 1

**Symptom:** adding the integration, or opening its options, fails before the first form,
or the flow ends at once.

| Scenario | Choice |
|---|---|
| where each row was read | `_load_integration`, `_async_get_flow_handler`, `ConfigEntriesFlowManager.async_init`, `OptionsFlowManager.async_create_flow`, `ConfigFlow.async_get_options_flow`, `ConfigFlow.async_supports_options_flow`, `ConfigFlow.async_set_unique_id` and `ConfigFlow._abort_if_unique_id_configured` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `Error occurred loading flow for integration <domain>: <error>`, under the integration's own logger | importing `config_flow.py` raised `ImportError` — a name a Home Assistant release moved or removed, or a library missing from `requirements` |
| `config_flow.py` imports, and the flow is still refused as an unknown handler | no class in it registers the domain: the `domain=` on the class is not the manifest's `domain` |
| `Cannot find integration <domain>` | Home Assistant could not load the integration itself — its folder or its `manifest.json` |
| the entry offers no options flow, or opening it is refused as an unknown handler | the config flow class does not override `async_get_options_flow`; core calls it on the class with the entry, so define it as the base class does, a `@staticmethod` under `@callback`, returning the `OptionsFlow` |
| the flow ends at once on `single_instance_allowed` | `single_config_entry` is `true` and an entry exists; for a flow not started by the user, an ignored entry counts too |
| the flow ends at once on `already_in_progress` | `async_set_unique_id` found another flow, not a reauth, open for the same unique ID |
| the flow ends at once on a reason of its own | the step that returned `async_abort` — `_abort_if_unique_id_configured` gives `already_configured` |

### Notify platform — Step 1

The entity itself is https://contributors.home-assistant.io/core/entities/notify/; these are
the rows a custom integration gets wrong against it.

| Rule | Value |
|---|---|
| the base class | `NotifyEntity`, from `homeassistant.components.notify` |
| `async_send_message` | `(self, message: str, title: str \| None = None) -> None` — no `**kwargs` and no `data` to read, since the service schema carries `message` and `title` only |
| `_attr_unique_id` | `f"{device_id}_notify"`, set per instance and never at class scope |
| `_attr_has_entity_name` and `_attr_name` | `True` and `"Notify"` |
| what setup reads | `{**entry.data, **entry.options}`, off the typed entry — *Typed `ConfigEntry` — Step 4* |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `discovery.async_load_platform` with a `BaseNotificationService` | `NotifyEntity` | the legacy pair registers a `notify.<name>` service, not an entity, and core is moving its own integrations off it | https://contributors.home-assistant.io/blog/2024/04/10/new-notify-entity-platform/ |
| a custom payload passed through `NotifyEntity` | a service registered directly, below | `data` is not in its service schema, which carries `message` and `title` only | https://contributors.home-assistant.io/core/entities/notify/ |

**A custom payload — animations, sounds, colours — registered as its own service:**

| Rule | Value |
|---|---|
| the schema | `probatio.Required(ATTR_MESSAGE): cv.string`, `probatio.Optional(ATTR_TITLE): cv.string`, `probatio.Optional(ATTR_DATA): dict` — the constants and `DOMAIN as NOTIFY_DOMAIN` from `homeassistant.components.notify.const` |
| the handler | a closure bound to one device, reading `call.data.get(ATTR_DATA) or {}` beside `call.data[ATTR_MESSAGE]` |
| registering | in `async_setup_entry`, since the service is per device: `hass.services.async_register(NOTIFY_DOMAIN, device_id, handler, schema=SERVICE_SCHEMA)`, under `if not hass.services.has_service(NOTIFY_DOMAIN, device_id)` |
| removing | in `async_unload_entry`, `hass.services.async_remove(NOTIFY_DOMAIN, device_id)`, under the inverse guard, `if hass.services.has_service(NOTIFY_DOMAIN, device_id)` |
| what it creates | `notify.{device_id}` — `notify.living_room_display`, say — with full `data` support |

### Entity platform files — Step 1

| Rule | Value |
|---|---|
| the base class | `CoordinatorEntity` for polling, `Entity` for push |
| runtime state | `entry.runtime_data`, not `hass.data[DOMAIN][entry.entry_id]` |
| `device_info` | the `DeviceInfo` TypedDict from `homeassistant.helpers.device_registry`, never a plain dict |
| `unique_id` | set on every entity |
| `_attr_has_entity_name` | `True`, mandatory for a new integration — the entity name then identifies only the data point |
| the main feature entity's name | `_attr_name = None`, so only the device name shows |
| `_attr_translation_key = "my_key"` | translated entity names and states; pairs with the `entity` section of `translations/en.json` |
| `_attr_entity_category` | on a non-primary entity: `EntityCategory.DIAGNOSTIC` for read-only info such as RSSI, `EntityCategory.CONFIG` for a setting that changes device behaviour |
| a value set at init or on update | an `_attr_*` class or instance attribute, assigned in `__init__` or in `_handle_coordinator_update`, never a property method |
| a value derived on read, from `self.coordinator.data` say | a property — https://contributors.home-assistant.io/core/entities/entity-class/ |
| availability on a push `Entity` | `_attr_available`, reflecting device reachability — set `False` when the device disconnects and `True` when it is back |
| availability on a `CoordinatorEntity` | override `available` and call `super()`, as the device-missing row of *A reply the code does not expect — Step 1* does — `CoordinatorEntity.available` already returns `last_update_success`, so an `_attr_available` beside it is never read |
| the state source | `self.coordinator.data` only — never I/O in a property |

```python
from typing import override

from homeassistant.helpers.device_registry import DeviceInfo


@property
@override
def device_info(self) -> DeviceInfo:
    """The device this entity belongs to."""
    return DeviceInfo(identifiers={(DOMAIN, self._device_id)}, name="My Device")
```

**The `device_class` a sensor carries decides which `state_class` is legal:**

| Rule | Value |
|---|---|
| where the legal pairs are declared | `DEVICE_CLASS_STATE_CLASSES` in core's `homeassistant/components/sensor/const.py`, which moves between releases |
| `SensorDeviceClass.MONETARY` | `SensorStateClass.TOTAL` only, so a fluctuating balance is `MONETARY` + `TOTAL` |
| a disallowed pair | logs *"is using state class X which is impossible considering device class Y"*, once per entity; the statistics still compile |
| the pair once chosen | locked by an attribute test |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `update_before_add=True` on `async_add_entities` for a `CoordinatorEntity` | compute `native_value` as a property off `self.coordinator.data`, or call `self._handle_coordinator_update()` at the end of `async_added_to_hass`, after `await super().async_added_to_hass()` | it schedules a debouncer timer that outlives the test and the frozen clock | `CoordinatorEntity.async_update` in `homeassistant/helpers/update_coordinator.py` |
| a collection sensor whose state is the raw list or a timestamp | the `len()` count with `_attr_state_class = MEASUREMENT`, and a sensor of its own for any other value worth a history | `last_updated` and `last_changed` are state attributes already, and a count graphs | https://contributors.home-assistant.io/core/entities/sensor/ |
| deleting `state_class` to silence an impossible-pair warning | the `state_class` that device class permits | deleting it drops long-term statistics altogether | `DEVICE_CLASS_STATE_CLASSES` in `homeassistant/components/sensor/const.py` |
| redeclaring an attribute, property or method the base class — `SensorEntity`, `TrackerEntity` — already provides, or guarding against its behaviour changing | the base class as it stands | the base class is the stable API a platform builds on | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a lawn mower stopped but neither docked nor paused, reported as `LawnMowerActivity.PAUSED` or `ERROR` | `LawnMowerActivity.IDLE`; and for an action that cancels the task without docking, `LawnMowerEntityFeature.STOP` with `async_stop` — both from 2026.10.0 | `PAUSED` says the task can be resumed, `ERROR` that the mower needs help | `LawnMowerActivity`, `LawnMowerEntityFeature` and `LawnMowerEntity.async_stop` in `homeassistant/components/lawn_mower/`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `const.py` there at the `2026.9.0` tag |

**Symptom:** `CoordinatorEntity` does not push initial state on add, so an entity that sets
`_attr_native_value` inside `_handle_coordinator_update` reads `unknown` until the next poll
— `first_refresh` has already run, so the data is there to read.

### An entity that is never added — Step 1

**Symptom:** the entity is missing from the integration's page, and the log carries one of
the lines below.

| Scenario | Choice |
|---|---|
| where each line was read | `EntityPlatform._async_add_entity_impl`, `_async_add_entities` and `_async_add_and_update_entities` in `homeassistant/helpers/entity_platform.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `Entity id already exists - ignoring: <entity_id>` | an entity with no `unique_id` whose `entity_id` is taken — one that sets `entity_id` itself, or the same entity added twice; give it a `unique_id` and leave `entity_id` to Home Assistant |
| `Platform <domain> does not generate unique IDs.` | two entities of the platform share a `unique_id`, or one is added twice — a listener for new devices adding a device it already added; build the id from what is unique to the device and the value, and keep a set of what was added |
| `Error adding entity <entity_id> for domain <platform> with platform <domain>`, with a traceback | the entity raised while being added — in `async_added_to_hass`, or in a property read as it registers, `device_info` or `name` say; the last `custom_components/<domain>/` frame of the traceback is the fault |
| `<domain>: Error on device update!`, with a traceback | `async_update` raised on the first update that `update_before_add=True` asks for |
| `<domain>: Not adding entity, error adding device: <reason>` | the device registry refused `device_info` — *Devices belong to one config entry — Step 3* says what it refuses |
| `<domain>: Not adding entity <name>, entity registry error: <reason>` | the entity registry refused the entity, for the reason the line gives |
| `Timed out adding entities for domain <platform> with platform <domain> after <n>s` | the add ran past 15 seconds an entity, and 500 at the least — slow work in `async_added_to_hass` or in the first update |
| `Reached the maximum of 10000 enabled entities for config entry <entry_id>; not adding more entities for integration <domain> …`, at WARNING, once per platform | no entity past the cap is added until one is removed or disabled; create the ones few users need disabled, with `_attr_entity_registry_enabled_default = False` |

### `EntityDescription` pattern — Step 1

Preferred when an integration exposes many similar entities:
```python
@dataclass(frozen=True, kw_only=True)
class MySensorDescription(SensorEntityDescription):
    """Describes one sensor and where its value comes from."""

    value_fn: Callable[[MyData], float]


SENSORS: tuple[MySensorDescription, ...] = (
    MySensorDescription(
        key="temperature", translation_key="temperature", value_fn=lambda d: d.temp
    ),
    MySensorDescription(
        key="humidity", translation_key="humidity", value_fn=lambda d: d.humidity
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add one sensor per description."""
    coordinator = entry.runtime_data
    async_add_entities(MySensor(coordinator, desc) for desc in SENSORS)
```

### `UpdateEntity` (firmware/OTA install) — Step 1

| Rule | Value |
|---|---|
| what `_attr_in_progress` does | `update.install` refuses a call while it is `True` — `_async_install` in `homeassistant/components/update/services.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| who sets it | the entity, at the top of `async_install`; core never sets it `True` |
| who clears it | core, when `async_install` returns or raises |
| what it does not cover | a device still flashing after `async_install` has returned |
| the lock for that | a boolean plus a monotonic timestamp, set at the top of `async_install` after the can't-install checks |
| the window on that lock | so a device that never reports back cannot wedge the entity |

  ```python
  @override
  async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
      """Push the OTA once, refusing a second entry while one is in flight."""
      if self._reflash:
          raise HomeAssistantError("Layout change — reflash via USB, not OTA.")
      if self._installing and time.monotonic() - self._install_started < INSTALL_TIMEOUT:
          raise HomeAssistantError("An update is already in progress for this device.")
      self._installing = True
      self._install_started = time.monotonic()
      self._attr_in_progress = True
      self.async_write_ha_state()
      await self._push_ota(version)
  ```
**Timing:** clear `_installing` where state resyncs from the device manifest — when the new
version lands, or when the window elapses.

### `DataUpdateCoordinator` (polling) — Step 1
- `update_interval` no shorter than the time the source's data takes to change — the `appropriate-polling` rule, https://contributors.home-assistant.io/core/quality-scale/appropriate-polling/; core sets no minimum
- Set `always_update=False` when API responses support `__eq__` — avoids unnecessary state machine writes
- Raise `ConfigEntryAuthFailed` on auth errors inside `_async_update_data`
- Raise `UpdateFailed` on other errors; use `UpdateFailed(retry_after=60)` for rate-limited APIs — it sets the wait before the next poll once, and is ignored during the first refresh
- For push APIs: use `coordinator.async_set_updated_data(data)` instead of adapting to polling

### Entity push subscriptions — Step 1
- Subscribe in `async_added_to_hass`, unsubscribe in `async_will_remove_from_hass` — prevents resource leaks
- Never subscribe in `__init__`

### A connection that drops — Step 1

**Symptom:** entities stay unavailable, or keep their last value, until the integration is
reloaded by hand.

**Fix:** say the connection is gone, retry on a task the config entry owns, and say when it
is back.

| Rule | Value |
|---|---|
| where each row was read | https://contributors.home-assistant.io/core/integrations/setup-failures/, https://contributors.home-assistant.io/core/integrations/fetching-data/ and the `entity-unavailable` and `log-when-unavailable` rules; `homeassistant/config_entries.py`, `homeassistant/helpers/update_coordinator.py` and `homeassistant/components/mqtt/client.py` at the `.0` tag of the release row in `reference/freshness.md` |
| how Home Assistant retries a setup that raised `ConfigEntryNotReady` | after 5 seconds, doubling on each failure up to `SETUP_RETRY_MAX_WAIT`, 600 seconds; and, where the integration supports discovery, as soon as the device is discovered |
| what a failed poll does | `last_update_success` goes false, `CoordinatorEntity.available` returns it, and the next interval tries again |
| what the coordinator catches unaided | `TimeoutError`, `aiohttp.ClientError`, `requests.exceptions.RequestException` and `urllib.error.URLError`, each a failed update |
| a request timeout | `async with asyncio.timeout(10):` round the fetch, the value the fetching-data page's example uses |
| who notices a push connection has dropped | the client library's own disconnect callback — core's MQTT client takes paho's `on_disconnect` |
| a connection that goes quiet without closing | the keepalive the protocol offers — core's MQTT client passes `keepalive` to `connect` |
| a push connection that drops | `coordinator.async_set_update_error(err)`, which logs once at ERROR and takes every `CoordinatorEntity` unavailable |
| a push connection that returns | the next data handed to the coordinator makes them available again and is logged at DEBUG only, so the line saying it is back is yours, once |
| the task that reconnects | `entry.async_create_background_task(hass, coro, name)`, which Home Assistant cancels when the entry unloads |
| the wait between attempts | `await asyncio.sleep(…)` inside that task; core's MQTT client waits a fixed `RECONNECT_INTERVAL_SECONDS`, 10 |
| a reconnect refused for its credentials | stop retrying and call `entry.async_start_reauth(hass)`, as core's MQTT client does |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `ConfigEntryNotReady` raised from a platform's `async_setup_entry` | raise it from `__init__.py` | it is too late there to be caught by the config entry setup | https://contributors.home-assistant.io/core/integrations/setup-failures/ |
| `asyncio.create_task` or `hass.async_create_task` for the reconnect loop | `entry.async_create_background_task` | unload cancels the entry's background tasks and no others, so the loop outlives a reload | `_async_process_on_unload` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| the last value left showing while the connection is down | mark the entity unavailable | unavailable is the better state than the last known one | https://contributors.home-assistant.io/core/quality-scale/entity-unavailable/ |

### A reply the code does not expect — Step 1

**Symptom:** every entity of the integration goes unavailable at once and the log reads
`Unexpected error fetching <name> data` over a `KeyError` or a `TypeError` — after a
firmware update, a new model, or a change at the service.

**Fix:** parse the reply where Step 1 puts the I/O, into fields that may be absent.

```python
@dataclass(frozen=True, kw_only=True)
class Reading:
    """One device's reading; a field the source left out is None."""

    temperature: float | None = None
    mode: str | None = None


def parse_reading(raw: dict[str, Any]) -> Reading:
    """Read what is there, and nothing that is not."""
    temperature = raw.get("temperature")
    mode = raw.get("mode")
    return Reading(
        temperature=temperature if isinstance(temperature, int | float) else None,
        mode=mode if mode in MODES else None,
    )
```

| Rule | Value |
|---|---|
| where each row was read | the `entity-unavailable` and `dynamic-devices` rules; `_async_refresh` and `async_update_listeners` in `homeassistant/helpers/update_coordinator.py` and `SensorEntity.state` in `homeassistant/components/sensor/__init__.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a field missing from an otherwise good reply | `None` for that value: the entity reads `unknown` and the others update |
| a device missing from an otherwise good reply | that entity alone unavailable — `return super().available and self._device_id in self.coordinator.data` |
| an exception the coordinator has no branch for, a `KeyError` or a `TypeError` say, leaving `_async_update_data` | logged with its traceback, and `last_update_success` goes false — so one bad field takes every entity on the coordinator unavailable |
| an exception in one entity's `_handle_coordinator_update` | logged as `Unexpected error updating listener`, and the other entities still update |
| an `ENUM` sensor handed a value outside its `options` | `ValueError`, *"provides state value '…', which is not in the list of options provided"* — map a value you do not know to `None` |
| a sensor with a unit or a state class handed text that is no number | `ValueError`, *"it has the non-numeric value"* |
| a `TIMESTAMP` sensor handed a `datetime` with no timezone | `ValueError`, *"which is missing timezone information"* |
| a device new to the reply | entities added from a coordinator listener, as the `dynamic-devices` rule's example does |
| finding out that the source changed | *A question a mock cannot answer — mocking Step 1* in `reference/testing.md` |
| the test that goes with the fix | *Step 4: Minimum coverage before claiming a tier* in `reference/testing.md` |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `raw["field"]` in `_async_update_data` | `.get()` into a field that may be `None` | the `KeyError` is an unexpected error, which takes every entity down for one field | `_async_refresh` in `homeassistant/helpers/update_coordinator.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `except Exception: return self.data`, to ride out a bad reply | raise `UpdateFailed` | the entities go on showing the last value as though it were current | https://contributors.home-assistant.io/core/quality-scale/entity-unavailable/ |
| an entity made unavailable for one missing field | `None`, which reads `unknown` | unavailable is for a fetch that failed, unknown for a piece that is missing | https://contributors.home-assistant.io/core/quality-scale/entity-unavailable/ |

### A blocking call inside the event loop — Step 1

**Symptom:** the log reads `Detected blocking call to <function> with args … inside the
event loop by custom integration '<domain>' at <file>, line <n>` — at WARNING with a
traceback the first time a line does it, at DEBUG after.

**Fix:** move the call to the executor, or replace it with its async equivalent.

```python
from functools import partial


async def async_read_state(hass: HomeAssistant, path: Path) -> str:
    """Read a file the device writes, off the event loop."""
    return await hass.async_add_executor_job(partial(path.read_text, encoding="utf-8"))
```

| Rule | Value |
|---|---|
| where each row was read | https://contributors.home-assistant.io/core/internals/blocking-operations/ and the `inject-websession` rule; `_BLOCKING_CALLS` in `homeassistant/block_async_io.py`, `raise_for_blocking_call` in `homeassistant/util/loop.py` and `async_add_executor_job` in `homeassistant/core.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| what core detects | `open` and `Path.open`, `read_text`, `read_bytes`, `write_text`, `write_bytes`; `glob.glob`, `glob.iglob`, `os.walk`, `os.listdir`, `os.scandir`; `time.sleep`; `HTTPConnection.putrequest`, which `urllib` goes through; `importlib.import_module`; and `SSLContext.load_default_certs`, `load_verify_locations`, `load_cert_chain` and `set_default_verify_paths` |
| what it lets through all the same | a path under `/proc`, the import of a module already imported, and `load_verify_locations` handed `cadata` alone |
| which of those raise as well as log | `time.sleep` and `HTTPConnection.putrequest` — a `RuntimeError` beginning `Caught blocking call to`, so the call never runs |
| what core cannot detect | anything off that list, the reads and writes on a file once it is open among them |
| a positional argument | `await hass.async_add_executor_job(func, arg)` |
| a keyword argument | `functools.partial`, as above — the method passes positional arguments only |
| a sync library | every call into it through the executor |
| an HTTP client shared with the rest of Home Assistant | `async_get_clientsession` from `homeassistant.helpers.aiohttp_client`, or `get_async_client` from `homeassistant.helpers.httpx_client` |
| an HTTP client of your own, where cookies are used say | `async_create_clientsession` or `create_async_httpx_client`, from the same two modules |
| an import | at module level, which Home Assistant runs before the loop starts or in its import executor |
| an import that must stay inside a function | through the executor, or `async_import_module` from `homeassistant.helpers.importlib` where the module may be imported from more than one place |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `time.sleep` in a coroutine or a `@callback` | `await asyncio.sleep` | core raises as well as logging | `_BLOCKING_CALLS` in `homeassistant/block_async_io.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| moving only the `open` to the executor | move the reads and writes with it | core sees the `open` and nothing after it, so what is left is never reported | https://contributors.home-assistant.io/core/internals/blocking-operations/ |
| an `SSLContext` loaded with certificates on the loop | `async_get_clientsession`, `get_async_client`, or `homeassistant.util.ssl` for a context alone | loading the certificates is blocking disk I/O, which those three keep in the executor | https://contributors.home-assistant.io/core/internals/blocking-operations/ |
| an `import` inside a function on the loop, of a module not yet imported | a module-level import | the import machinery reads the module from disk | https://contributors.home-assistant.io/core/internals/blocking-operations/ |

### `ConfigEntry` mutation — Step 3
- Never mutate `ConfigEntry` directly — always use `hass.config_entries.async_update_entry(entry, data=..., options=...)`

### Logging — Step 1

Covers the rule `log-when-unavailable` (`reference/quality-scale.md`) and HA's logging conventions.

| Rule | Value |
|---|---|
| what the coordinator logs for you | on a poll, the first `UpdateFailed`, timeout or request error at ERROR, nothing for the ones after it, and the recovery at INFO — which is `log-when-unavailable` met; an unexpected exception at ERROR with its traceback, every time; what it leaves to you on a push connection is *A connection that drops — Step 1* |
| what HA logs for you | the reason behind `ConfigEntryAuthFailed` at WARNING, and behind `ConfigEntryNotReady` at INFO on each retry — `ConfigEntry.async_setup`, through `__async_handle_config_entry_setup_error`, in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| which exception to raise | transient → `UpdateFailed` or `ConfigEntryNotReady`; auth → `ConfigEntryAuthFailed`; an action's own failure → `HomeAssistantError` or `ServiceValidationError`, per `action-exceptions` |
| `INFO` | almost never: the one line saying a device or service is gone, and the one saying it is back, where `log-when-unavailable` asks for that level; setup, unload and teardown are `DEBUG` |
| `WARNING` | a recoverable thing the user should know |
| `ERROR` | an unexpected, actionable bug, never an expected transient failure |
| `DEBUG` | per-poll and developer detail |
| the message arguments | lazy `%` args — `_LOGGER.debug("added %s", key)`, which ruff `G004` enforces |
| the message prefix | none: `logging.getLogger(__name__)` already carries the module path |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| wrapping the fetch in your own `try`/log | raise `UpdateFailed` and let the coordinator log | the manual log double-logs and fails `log-when-unavailable` | https://contributors.home-assistant.io/core/quality-scale/log-when-unavailable/ |
| `_LOGGER.exception(...)` beside a raise in `async_setup_entry` | raise alone | HA logs the reason already | `ConfigEntry.async_setup`, through `__async_handle_config_entry_setup_error`, in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| an f-string in a log call | a lazy `%` arg | the f-string evaluates even when the level is disabled | https://contributors.home-assistant.io/core/development/style/ |
| logging a credential, API key, token or raw auth response | log the fact, never the secret | a log is read by whoever is handed it | https://contributors.home-assistant.io/core/development/style/ |
| a module-level `_LOGGER` left behind after the calls go | delete it | ruff does not flag an unused module global | — |

### Custom services — Step 1

| Rule | Value |
|---|---|
| where to register | `async_setup`, not `async_setup_entry` — *Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 3* below says why |
| an entity-targeted action | `async_register_platform_entity_service()` |
| where a service is documented | `services.yaml`, with its icons in `icons.json` |
| a device dropdown | `selector: device` with `integration: {domain}`, never `selector: config_entry`, which the HA frontend labels "Integration" |
| resolving that device to your own config entry | `async_get_device_and_config_entry_for_domain`, in the handler — the helper core added in 2026.9 |
| a call with no target | `hass.services.async_call(DOMAIN, svc, …)` reaches every config entry, so pass your own `entry_id`/`device_id` and filter on it unless the call is a deliberate bulk one |
| a key the schema guarantees | `call.data[KEY]`, not `call.data.get(KEY)`, so a wrong assumption fails at once — `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a value the schema or the entity filter already enforces | no second check in the handler; guard only a value that bypasses validation or is transformed on the way — `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |

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

### An action that does nothing — Step 1

**Symptom:** an action aimed at the integration's entities returns with no error and
changes nothing.

| Scenario | Choice |
|---|---|
| where each row was read | `_resolve_entity_service_call_entities` in `homeassistant/helpers/service.py`, and `async_extract_referenced_entity_ids` and `SelectedEntities.log_missing` in `homeassistant/helpers/target.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| an entity that is unavailable | skipped; named only when targeted by its own id, in `Referenced entities <ids> are missing or not currently available` at WARNING |
| an entity reached through a device, an area or a floor, or a device or area carrying a label | skipped when it carries an `entity_category` or is hidden, so a `CONFIG` or `DIAGNOSTIC` entity never receives an action aimed at its device |
| an entity carrying the label itself | skipped when it is hidden |
| an entity without the action's required features or device class | skipped when reached through a device, area, floor or label; targeted by its own id, the call raises `ServiceNotSupported` |
| no entity left to call | the call returns having called nothing, unless it asked for a response, which raises `Service call requested response data but did not match any entities` |
| an action that reaches more entities than it was aimed at | the "a call with no target" row of *Custom services — Step 1* |

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

### Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 3
The registration happens once per process; doing it per entry races when two entries set up in parallel. Claim the `hass.data` flag **before** the `await`, or both entries pass the check. The panel case, with the code, is *Step 3: Register the static path and the panel in `async_setup`* in `reference/panels.md`.

### Diagnostics platform — Step 1

The `diagnostics` rule in `reference/quality-scale.md`. Add `diagnostics.py`:

```python
from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_API_KEY, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .coordinator import MyConfigEntry

TO_REDACT = {CONF_API_KEY, CONF_PASSWORD, "token"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MyConfigEntry
) -> dict[str, Any]:
    """Return the entry's settings and each device's reading, secrets redacted."""
    coordinator = entry.runtime_data
    return {
        "entry_data": async_redact_data(entry.data, TO_REDACT),
        "entry_options": async_redact_data(entry.options, TO_REDACT),
        "devices": async_redact_data(
            {
                device_id: asdict(reading)
                for device_id, reading in coordinator.data.items()
            },
            TO_REDACT,
        ),
    }
```

| Rule | Value |
|---|---|
| where this was read | `async_redact_data` in `homeassistant/components/diagnostics/util.py`, and `homeassistant/components/nam/diagnostics.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| what goes in | the fields a bug report needs, each chosen — never `entry.runtime_data` whole |
| what `async_redact_data` walks | mappings and lists only, so an object inside the dict passes through unredacted; turn each device's dataclass into a dict with `asdict` first, keyed by device id as `coordinator.data` is |
| registration | none — HA discovers it from the file name |

### Devices belong to one config entry — Step 3

A device has exactly one config entry and at most one subentry: read `config_entry_id` and
`config_subentry_id`.

| Rule | Value |
|---|---|
| where each release below comes from | the `breaks_in_ha_version` of the call site that reports that usage, or the version argument of the `DeprecatedConstant`, read at the `.0` tag of the release row in `reference/freshness.md` in `homeassistant/helpers/device_registry.py`, `homeassistant/helpers/device.py`, `homeassistant/helpers/entity_platform.py` and `homeassistant/const.py` |
| a row naming no release | one core attaches none to |
| the WebSocket keys of the same names | *A panel that reads devices reads them by config entry — Step 3* in `reference/panels.md` |
| how a custom integration is told | a logged warning, from `report_usage` in `homeassistant/helpers/frame.py` or `deprecated_function` in `homeassistant/helpers/deprecation.py`, at the `.0` tag of the release row in `reference/freshness.md` — unless the row says it raises already |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `DeviceEntry.config_entries`, on a main, child or deleted device | `config_entry_id`, which is `None` on a deleted device whose config entry is gone, where the property gave an empty set | a compatibility property returning `{config_entry_id}`, logged from 2026.10; stops working in **2027.10.0** | `_report_deprecated_config_entries_property` in `homeassistant/helpers/device_registry.py` |
| `DeviceEntry.config_entries_subentries`, on a main, child or deleted device | `config_entry_id` and `config_subentry_id` | a compatibility property returning `{config_entry_id: {config_subentry_id}}`, logged from 2026.10; stops working in **2027.10.0** | `_report_deprecated_config_entries_property` in `homeassistant/helpers/device_registry.py` |
| `DeviceEntry.primary_config_entry`, on a main or child device | `config_entry_id` | a compatibility property returning `config_entry_id` itself, logged from 2026.10; stops working in **2027.10.0** | `BaseDeviceEntry.primary_config_entry` in `homeassistant/helpers/device_registry.py` |
| a loop over a device's config entries to find your own | `async_get_device_and_config_entry_for_domain(hass, device_id, domain=DOMAIN)` | the loop gets a pre-migration composite device id wrong, which the helper resolves | `async_get_device_and_config_entry_for_domain` in `homeassistant/helpers/device_registry.py` |
| `DeviceInfo["via_device"]`, `async_get_or_create(via_device=…)` | `via_device_id`, looked up with `async_get_device_id_by_identifier(hass, identifier, config_entry_id=…)` | an identifier is unique only within a config entry; stops working in **2027.8.0** | `DeviceRegistry.async_get_or_create` in `homeassistant/helpers/device_registry.py` |
| `ATTR_VIA_DEVICE`, imported from `homeassistant.const` | the string `"via_device_id"` | logged on import; removed in **2027.8** | the `DeprecatedConstant` for `ATTR_VIA_DEVICE` in `homeassistant/const.py` |
| `device_info` or `device_entry` on an entity with no `unique_id`, or on one added by a platform with no config entry | a `unique_id`, on an entity a config entry's platform adds | the device link is dropped and logged already, so the entity has no device; raises from **2027.8.0** | `EntityPlatform._check_device_attach` in `homeassistant/helpers/entity_platform.py` |
| a `DeviceInfo` carrying a field beside its `default_` twin — `name` beside `default_name`, `model` beside `default_model` | the plain field alone | it raises `DeviceInfoError`, so the entity is not added and the log reads `<domain>: Not adding entity, error adding device: …` | `_validate_device_info` in `homeassistant/helpers/device_registry.py` and `EntityPlatform._async_add_entity_impl` in `homeassistant/helpers/entity_platform.py`, and https://contributors.home-assistant.io/blog/2026/08/24/device-registry-follow-up-changes/ |
| a `via_device` or `via_device_id` naming the device itself | drop the self-reference | `via_device_id` raises `HomeAssistantError` already; `via_device` is ignored and logged, and raises from **2027.8.0** | `async_get_or_create` and `async_update_device` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a composite device id passed as `via_device_id` | the id of one real device | resolved and logged now; stops working in **2027.8** | `DeviceRegistry._resolve_via_device_id` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.async_get_device()` | `async_get_device_by_identifier()`, `async_get_device_by_connection()` or `async_get_devices()`, each with the config entry id | the lookup is ambiguous once identifiers repeat across entries; stops working in **2027.8.0** | `DeviceRegistry.async_get_device` in `homeassistant/helpers/device_registry.py` |
| `async_update_device(add_config_entry_id=…, add_config_subentry_id=…, remove_config_entry_id=…, remove_config_subentry_id=…)` | `new_config_entry_id`, `new_config_subentry_id`, or `async_remove_device` | a move is no longer an add plus a remove; stops working in **2027.8.0** | `DeviceRegistry.async_update_device` in `homeassistant/helpers/device_registry.py` |
| `async_get_or_create` re-registering an existing device under a different subentry | `async_update_device(new_config_subentry_id=…)` | it silently moves the device; raises from **2027.8.0** | `DeviceRegistry.async_get_or_create` in `homeassistant/helpers/device_registry.py` |
| a `disabled_by` that contradicts the owning config entry or the parent device | leave it `UNDEFINED` and let the registry derive it | the value is dropped and logged now, and a child enabled under a disabled parent is logged and kept disabled; raises from **2027.8** | `DeviceRegistry._async_update_device` and `_async_update_child_device` in `homeassistant/helpers/device_registry.py` |
| `async_update_device(merge_connections=…, merge_identifiers=…)` | `new_connections`, `new_identifiers`, with the full set computed yourself | merging only ever adds; stops working in **2027.9.0** | `DeviceRegistry.async_update_device` in `homeassistant/helpers/device_registry.py` |
| `async_get_or_create(default_manufacturer=…, default_model=…, default_name=…)` | `manufacturer`, `model`, `name` | there is no primary integration left to defer to; stops working in **2027.9.0** | `DeviceRegistry.async_get_or_create` in `homeassistant/helpers/device_registry.py` |
| `async_get_or_create(created_at=…, modified_at=…)` | drop the arguments | the registry owns both and always ignored them; stops working in **2027.9.0** | `DeviceRegistry.async_get_or_create` in `homeassistant/helpers/device_registry.py` |
| `suggested_area` read off `DeviceEntry`, or passed to `async_update_device` | drop it; `DeviceInfo` and `async_get_or_create` still take it, and set a new device's area from it | ignored, and past the removal release core names for it — **2026.9** on the property, **2026.9.0** on the `async_update_device` argument | `DeviceEntry.suggested_area` and `async_update_device` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a non-`str` value in a device-registry string field (`model`, `sw_version`, …) | pass a `str` | coerced with a warning now; stops working in **2026.12.0** | `_validate_str` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.devices` as a mapping — `.get()`, `.values()`, `.keys()`, `registry.devices[id]`, `device_id in registry.devices` | iterate it for the entries, `async_get(device_id)` for a lookup | it is a read-only collection now; the mapping shim stops working in **2027.9.0** | `_DeprecatedDeviceRegistryItemsView` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.child_devices` as a mapping | iterate it | there is no compatibility shim at all: no `.get()`, no `.values()`, no lookup by id | `DeviceRegistry._async_load` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.deleted_devices` | nothing — it is an internal detail of the registry | stops working in **2027.9.0** | `DeviceRegistry.deleted_devices` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.async_is_composite_device_id()` | `async_get(device_id, include_composite_devices=False)` returning `None` | the parameter makes the same test; stops working in **2027.9.0** | `DeviceRegistry.async_is_composite_device_id` in `homeassistant/helpers/device_registry.py` |
| a `DeviceEntry`-only attribute read off a child device — `connections`, `manufacturer`, `model`, `model_id`, `hw_version`, `sw_version`, `serial_number`, `configuration_url`, `entry_type`, `via_device_id` | branch on `parent_device_id`, then read the parent device | the shim hands back the `DeviceEntry` default, not the parent's value; stops working in **2027.9.0** | `ChildDeviceEntry.__getattr__` in `homeassistant/helpers/device_registry.py` |
| `async_device_info_to_link_from_entity()`, `async_device_info_to_link_from_device_id()` | `entity.device_entry = async_entity_id_to_device(hass, source_entity_id)` | both already return `None`; removed in **2027.8.0** | `async_device_info_to_link_from_entity` and `async_device_info_to_link_from_device_id` in `homeassistant/helpers/device.py` |
| `async_remove_stale_devices_links_keep_entity_device()`, `async_remove_stale_devices_links_keep_current_device()` | `helper_integration.async_remove_helper_devices(…, remove_all_devices=True)` | both already do nothing; removed in **2027.8.0** | `async_remove_stale_devices_links_keep_entity_device` and `async_remove_stale_devices_links_keep_current_device` in `homeassistant/helpers/device.py` |

> **Note:** on a *synthesized composite* device — the read-only entry `async_get()` returns
> for a pre-migration composite device id — the three properties are the supported read and log
> nothing, since it spans several entries; `is_composite_device`, from 2026.10.0, says which it is.

### Units: prefer the enumerators — Step 1

| Rule | Value |
|---|---|
| `UnitOfDensity` | mass over volume — `GRAMS_PER_CUBIC_METER`, `MILLIGRAMS_PER_CUBIC_METER`, `MICROGRAMS_PER_CUBIC_METER`, `MICROGRAMS_PER_CUBIC_FOOT` |
| `UnitOfRatio` | ratios — `PARTS_PER_MILLION`, `PARTS_PER_BILLION`, `PERCENTAGE` |
| where each release below comes from | the version argument of the `DeprecatedConstantEnum` or `DeprecatedConstant` beside the constant in `homeassistant/const.py`, read at the `.0` tag of the release row in `reference/freshness.md` |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `CONCENTRATION_GRAMS_PER_CUBIC_METER`, `CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER`, `CONCENTRATION_MICROGRAMS_PER_CUBIC_METER`, `CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT` | the matching `UnitOfDensity` member | removed in **2027.8** | the `DeprecatedConstantEnum` beside each in `homeassistant/const.py` |
| `CONCENTRATION_PARTS_PER_MILLION`, `CONCENTRATION_PARTS_PER_BILLION` | the matching `UnitOfRatio` member | removed in **2027.8** | the `DeprecatedConstantEnum` beside each in `homeassistant/const.py` |
| `CONCENTRATION_PARTS_PER_CUBIC_METER` | nothing — core names no replacement unit | removed in **2027.8** | the `DeprecatedConstant` beside it in `homeassistant/const.py` |
| `PERCENTAGE` as a unit of measurement, on a humidity or battery sensor | `UnitOfRatio.PERCENTAGE` | the constant itself is not deprecated and is now defined from the enum (`PERCENTAGE: Final = UnitOfRatio.PERCENTAGE.value`), but using it as a unit is | https://contributors.home-assistant.io/blog/2026/06/30/new-unit-enumerators/ |

### Config entry migration — Step 3

Implement `async_migrate_entry` in `__init__.py` whenever the stored `entry.data` schema changes:
```python
# In config flow:
class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow; the version pair says which stored entries need migrating."""

    VERSION = 2  # bump for breaking changes (fails setup if no handler)
    MINOR_VERSION = 1  # bump for compatible changes (setup continues without handler)


# In __init__.py:
async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Bring a stored entry up to the current version."""
    if entry.version == 1:
        new_data = {**entry.data, "new_field": "default"}
        hass.config_entries.async_update_entry(
            entry, data=new_data, version=2, minor_version=1
        )
    return True
```

| Rule | Value |
|---|---|
| where each row was read | `__async_setup_with_context`, `__async_handle_config_entry_setup_error` and `ConfigEntries.async_retry_migration` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md`; the compatibility floor, `ConfigEntry.async_migrate` there at the `2026.9.0` tag |
| the compatibility floor | 2026.10.0; below it `ConfigEntry.async_migrate` catches any `Exception` and returns `False`, so `ConfigEntryNotReady` ends in `migration_error` too, and `async_retry_migration` does not exist |
| a failure that may clear on its own — a timeout, a device offline | raise `ConfigEntryNotReady`; the migration is retried on the setup schedule |
| any other failure | raise `ConfigEntryError` with a `translation_key`, which the entry shows as its reason, or return `False`; either way the entry stops in `migration_error`, as it does for any other exception, which is logged with its traceback and leaves no reason |
| returning `False` | logs nothing and leaves the entry no reason, so log why before you return it |
| `ConfigEntryAuthFailed` during migration | logged at WARNING and the entry stops in `migration_error`; no reauth flow starts, since reauth expects a migrated entry |
| the way out of `migration_error` | a repair issue whose fix flow calls `await hass.config_entries.async_retry_migration(entry_id)` — https://contributors.home-assistant.io/blog/2026/09/17/use-config-entry-exc-in-migration/ |
| a major version bump with no `async_migrate_entry` | setup fails for every existing user, so ship the handler in the same change |

### OAuth2 errors at setup — Step 3

**Fix:** let the OAuth2 helper's exceptions leave `async_setup_entry` unmapped; each is the
config entry exception that says what happens next, with its message translated.

| Rule | Value |
|---|---|
| where each row was read | `homeassistant/exceptions.py` at the `.0` tag of the release row in `reference/freshness.md`; the compatibility floor, that file and `homeassistant/helpers/config_entry_oauth2_flow.py` at the `2026.9.0` tag |
| the compatibility floor | 2026.10.0; below it the token-request errors and `ImplementationUnavailableError` are no config entry exception, and a missing implementation raises a bare `ValueError`, so an integration that claims an older release keeps its own mapping and its `except ValueError` |
| `ImplementationUnavailableError`, `OAuth2TokenRequestError`, `OAuth2TokenRequestTransientError`, `OAuth2TokenRequestConnectionError` | each a `ConfigEntryNotReady`, so setup is retried |
| `UnknownImplementationError`, `OAuth2TokenRequestReauthError` | each a `ConfigEntryAuthFailed`, so the reauth flow starts |
| their messages | translated under the `homeassistant` domain, so `translations/en.json` carries none of them |
| a different outcome — a status known to be permanent, context only the integration has, state to clean up first | catch the most specific of them, and let the rest propagate |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `try`/`except ImplementationUnavailableError` round `async_get_config_entry_implementation`, raising `ConfigEntryNotReady` | the call alone | the helper's exception already is one | https://contributors.home-assistant.io/blog/2026/09/07/oauth2-central-error-handling/ |
| `except ValueError` round that call | nothing | `UnknownImplementationError` is a `ValueError` too, so the handler turns a reauth into whatever it raises | `UnknownImplementationError` in `homeassistant/exceptions.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| mapping `OAuth2TokenRequestReauthError` to `ConfigEntryAuthFailed`, or `OAuth2TokenRequestError` to `ConfigEntryNotReady`, round `async_get_access_token()` or `async_ensure_token_valid()` | the call alone | each already is the exception it is mapped to | https://contributors.home-assistant.io/blog/2026/09/07/oauth2-central-error-handling/ |
| an `oauth2_implementation_unavailable` key in the `exceptions` section of `translations/en.json` | delete it | the exception's message comes from the `homeassistant` domain | https://contributors.home-assistant.io/blog/2026/09/07/oauth2-central-error-handling/ |

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
| a failure in `async_setup_entry` | not this line either; what Home Assistant logs for each exception is *Logging — Step 1* |

### A sign-in request that keeps coming back — Step 3

**Symptom:** the integration asks the user to sign in again after a sign-in that worked, or
after every outage.

| Scenario | Choice |
|---|---|
| where each row was read | `ConfigEntry.async_start_reauth`, `ConfigFlow.async_update_reload_and_abort` and `ConfigFlow.async_update_and_abort` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| two requests at once | not possible: no second reauth or reconfigure flow starts for an entry while one is open, so a request that returns was raised after the last one finished |
| `ConfigEntryAuthFailed` raised for a timeout, a server error or a rate limit | every outage asks for a sign-in; raise it only when the service refused the credentials — which exception to raise is *Logging — Step 1* |
| the new credentials kept anywhere but the entry | a reload sets up from `entry.data`, so pass them to `async_update_reload_and_abort` as `data_updates` |
| `async_update_and_abort` in the reauth step | it writes the entry and does not reload it, so the running code keeps the old credentials and fails again; use `async_update_reload_and_abort` |
| a client built once and kept past a reload — at module level, or in `async_setup` | it keeps the old credentials; build it in `async_setup_entry` and keep it on `entry.runtime_data` |

### Deprecated platform APIs — Step 1

The deprecations a custom integration can meet that have no section of their own above.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `mqtt.publish()` or `async_publish()` with `qos=None` or `retain=None` | the defaults, or typed values — the parameters are `qos: int = 0` and `retain: bool = False` | the `None` fallbacks stop working in **2027.6** | `async_publish` in `homeassistant/components/mqtt/client.py` |
| using a condition object as a callable | `async_from_config()` from `homeassistant.helpers.condition`, then `async_check()`, then `async_unload()`; a script is `async_run()` then `await script.async_unload()` | the post gives **2027.1** for the end of the callable form; core at the `.0` tag of the release row in `reference/freshness.md` attaches no warning to it | https://contributors.home-assistant.io/blog/2026/05/13/condition-script-api-changes/ |
| `BrowseMediaSource(domain=None)` | your own domain; the node listing every media source is `RootBrowseMediaSource` | `domain` is a required `str` now — a hard change with no deprecation period | `BrowseMediaSource` and `RootBrowseMediaSource` in `homeassistant/components/media_source/models.py` |
| `battery_level` on a `device_tracker` entity | a dedicated `SensorDeviceClass.BATTERY` sensor | stops working in **2027.7** | `BaseTrackerEntity.__init_subclass__` in `homeassistant/components/device_tracker/entity.py` |
| `TrackerEntity.location_name` | `in_zones` — zone entity ids, in any order, since the base class sorts them | stops working in **2027.7** | `TrackerEntity.in_zones` in `homeassistant/components/device_tracker/entity.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `battery_level` on `StateVacuumEntity` | a dedicated battery sensor | already removed, in 2026.9 | the Vacuum entry under *Backward-incompatible changes* at https://www.home-assistant.io/blog/2026/09/02/release-20269/ |
| `async_initialize_triggers(home_assistant_start=…)` | stop passing it; `hass.async_add_startup_job` for work at startup | it already has no effect; removed in **2027.8.0** | `async_initialize_triggers` in `homeassistant/helpers/trigger/__init__.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a `TrackerEntity` for a device tracked by connection rather than position | `BaseScannerEntity` | it derives the state from the associated zone and sets the `tracking_type` capability attribute | https://contributors.home-assistant.io/blog/2026/06/15/device-tracker-changes/ |
| `modbus.get_hub(hass, name)`, attaching to a hub the user configured in YAML | collect the connection details in your own config flow, then `async_get_unit(hass, entry, params, unit_id)` | logged from 2026.10; stops working in **2027.10** | `get_hub` in `homeassistant/components/modbus/__init__.py` and `async_get_unit` in `homeassistant/components/modbus/connection.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| the `configurator` integration's `async_request_config` or `request_config` | a config flow and config entries | logged from 2026.10 on those two calls; the integration is removed in **2027.10** | `_report_deprecation` in `homeassistant/components/configurator/__init__.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `hass.bus.async_listen(…, run_immediately=…)` or `async_listen_once(…, run_immediately=…)` | drop the argument | passing `True` or `False` raises from 2026.10 | `EventBus.async_listen` and `EventBus.async_listen_once` in `homeassistant/core.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| an `llm.Tool` whose `async_call` returns a JSON object | `llm.ToolResult(data=…)`, with `error=True` when the call failed, from 2026.10.0 | logged now; stops working in **2027.11.0** | `APIInstance.async_call_tool` in `homeassistant/helpers/llm.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.9.0` tag |
| `ToolResultContent.tool_result` | `ToolResultContent.result`, the `llm.ToolResult` itself, from 2026.10.0 | logged now; stops working in **2027.11.0** | `ToolResultContent.tool_result` in `homeassistant/components/conversation/chat_log.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.9.0` tag |
| an `llm.Tool` with no `integration` | `integration = DOMAIN` on the tool class | logged now, and the domain filled in from the tool's module; stops working in **2027.10** | `report_untagged_tool` in `homeassistant/helpers/llm.py`, at the `.0` tag of the release row in `reference/freshness.md` |

> **Note:** a condition platform may implement `_async_setup()` and `_async_unload()` for async
> set-up and teardown, and from 2026.10.0 `_async_track_changes(action)`, calling `action` when
> its result may change, with `needs_polling` `False` once nothing else changes it; all optional.

### Announced for a release after 2026.10 — Step 1

| what | lands in | do now | do then |
|---|---|---|---|
| `RestoreStateData.last_states` is removed, as stored states are keyed by entity registry id | 2026.11 — https://contributors.home-assistant.io/blog/2026/10/06/restore-state-last-states-removal/ | restore through `RestoreEntity` and `async_get_last_state()` or `async_get_last_extra_data()`, which are unaffected | `restore_state.async_get(hass).async_get_stored_state(entity_id)` where you read stored states directly |

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
