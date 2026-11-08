# Entities, devices and diagnostics

Read this when writing or changing an entity platform — its entities and their devices, a
notify or update entity, units — or the diagnostics platform.

**Set a `unique_id` on every entity.**

## Contents

1. Writing the entity platforms
2. Step 1: Write the entity platform files
3. Cases
4. Notify platform — Step 1
5. An entity that is never added — Step 1
6. `EntityDescription` pattern — Step 1
7. `UpdateEntity` (firmware/OTA install) — Step 1
8. Diagnostics platform — Step 1
9. Devices belong to one config entry — Step 1
10. Units: prefer the enumerators — Step 1

## Writing the entity platforms

### Step 1: Write the entity platform files

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
| availability on a `CoordinatorEntity` | override `available` and call `super()`, as the device-missing row of *A reply the code does not expect — Step 1* in `reference/fetching-data.md` does — `CoordinatorEntity.available` already returns `last_update_success`, so an `_attr_available` beside it is never read |
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
| `battery_level` on a `device_tracker` entity | a dedicated `SensorDeviceClass.BATTERY` sensor | stops working in **2027.7** | `BaseTrackerEntity.__init_subclass__` in `homeassistant/components/device_tracker/entity.py` |
| `TrackerEntity.location_name` | `in_zones` — zone entity ids, in any order, since the base class sorts them | stops working in **2027.7** | `TrackerEntity.in_zones` in `homeassistant/components/device_tracker/entity.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `battery_level` on `StateVacuumEntity` | a dedicated battery sensor | already removed, in 2026.9 | the Vacuum entry under *Backward-incompatible changes* at https://www.home-assistant.io/blog/2026/09/02/release-20269/ |
| a `TrackerEntity` for a device tracked by connection rather than position | `BaseScannerEntity` | it derives the state from the associated zone and sets the `tracking_type` capability attribute | https://contributors.home-assistant.io/blog/2026/06/15/device-tracker-changes/ |
| `RestoreStateData.last_states`, read for a stored state | `restore_state.async_get(hass).async_get_stored_state(entity_id)`; an entity restores its own state through `RestoreEntity` and `async_get_last_state()` or `async_get_last_extra_data()` | removed in 2026.11, as stored states are keyed by entity registry id | `RestoreStateData.async_get_stored_state` in `homeassistant/helpers/restore_state.py`, at the `.0` tag of the release row in `reference/freshness.md` |

**Symptom:** `CoordinatorEntity` does not push initial state on add, so an entity that sets
`_attr_native_value` inside `_handle_coordinator_update` reads `unknown` until the next poll
— `first_refresh` has already run, so the data is there to read.

## Cases

### Notify platform — Step 1

The entity itself is https://contributors.home-assistant.io/core/entities/notify/; these are
the rows a custom integration gets wrong against it.

| Rule | Value |
|---|---|
| the base class | `NotifyEntity`, from `homeassistant.components.notify` |
| `async_send_message` | `(self, message: str, title: str \| None = None) -> None` — no `**kwargs` and no `data` to read, since the service schema carries `message` and `title` only |
| `_attr_unique_id` | `f"{device_id}_notify"`, set per instance and never at class scope |
| `_attr_has_entity_name` and `_attr_name` | `True` and `"Notify"` |
| what setup reads | `{**entry.data, **entry.options}`, off the typed entry — *Typed `ConfigEntry` — Step 4* in `reference/patterns.md` |

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
| `<domain>: Not adding entity, error adding device: <reason>` | the device registry refused `device_info` — *Devices belong to one config entry — Step 1* says what it refuses |
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

### Devices belong to one config entry — Step 1

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
