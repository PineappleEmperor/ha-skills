# Entities, devices and diagnostics

Read this when writing or changing an entity platform — its entities and their devices, a
notify or update entity, an image it serves, units — or the diagnostics platform.

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
11. Serving an image — Step 1

## Writing the entity platforms

### Step 1: Write the entity platform files

| Rule | Value |
|---|---|
| the base class | `CoordinatorEntity` for polling, `Entity` for push |
| runtime state | `entry.runtime_data`, not `hass.data[DOMAIN][entry.entry_id]` |
| `device_info` | a `DeviceInfo` from `homeassistant.helpers.device_registry`, never a plain dict — a dataclass from 2026.11.0, built with keyword arguments, its fields read and set as attributes, an unset field reading `UNDEFINED`; what no longer works on it is *Devices belong to one config entry — Step 1* |
| `unique_id` | set on every entity |
| `_attr_has_entity_name` | `True`, mandatory for a new integration — the entity name then identifies only the data point |
| the main feature entity's name | `_attr_name = None`, so only the device name shows |
| `_attr_translation_key = "my_key"` | translated entity names and states; pairs with the `entity` section of `translations/en.json` |
| `_attr_entity_category` | on a non-primary entity: `EntityCategory.DIAGNOSTIC` for read-only info such as RSSI, `EntityCategory.CONFIG` for a setting that changes device behaviour |
| a value set at init or on update | an `_attr_*` attribute, never a property method: a class attribute only when every instance shares the value, otherwise assigned in `__init__` or in `_handle_coordinator_update` — `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a value derived on read, from `self.coordinator.data` say | a property — https://contributors.home-assistant.io/core/entities/entity-class/ |
| availability on a push `Entity` | `_attr_available`, reflecting device reachability — set `False` when the device disconnects and `True` when it is back |
| availability on a `CoordinatorEntity` | override `available` and call `super()`, as the device-missing row of *A reply the code does not expect — Step 1* in `reference/fetching-data.md` does — `CoordinatorEntity.available` already returns `last_update_success`, so an `_attr_available` beside it is never read |
| the state source | `self.coordinator.data` only — never I/O in a property |
| a `LightEntity`'s colour modes | both `supported_color_modes` and `color_mode`, each as an `_attr_*` or a property: with one and not the other the light raises `HomeAssistantError` when it reports its state, and ha-integration-ci fails it (W7436, W7437) — `checkers/light_color_mode.py` in core's `packages/pylint-home-assistant/pylint_home_assistant/`, at the `.0` tag of the release row in `reference/freshness.md` |

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
| a class of your own defining `async_added_to_hass`, `async_will_remove_from_hass` or `async_prepare_to_add_to_hass`, with no `async_entity_id_changed` in it or in a subclass of it | `@callback def async_entity_id_changed(self, old_entity_id: str) -> None`, from 2026.11.0: call `super().async_entity_id_changed(old_entity_id)` first, then re-key anything keyed on `self.entity_id`, a state listener or a dispatcher signal say; it must not await, and one that only calls `super()` opts in | until the class opts in, an entity_id change removes the entity and adds it again, running the whole add and remove lifecycle; core changes every entity in place from **2027.11** | `_entity_class_requires_readd` and `Entity.async_entity_id_changed` in `homeassistant/helpers/entity.py`, at the `.0` tag of the release row in `reference/freshness.md`, whose docstrings give the 2027.11; the floor, the same file at the `2026.10.0` tag |
| overriding `add_to_platform_start`, `add_to_platform_finish` or `add_to_platform_abort` to run code before an entity is added | `async def async_prepare_to_add_to_hass(self) -> None`, from 2026.10.0: `await super().async_prepare_to_add_to_hass()` first, read `self.hass`, `self.platform` and `self.parallel_updates`, never `entity_id` or `registry_entry`, and register cleanup with `self.async_on_remove` | the three are the entity platform's own steps; the hook runs on every add attempt, a disabled or colliding entity's included, and `async_will_remove_from_hass` never runs for an add that is aborted, while raising from the hook aborts the add | `EntityPlatform._async_add_entity` in `homeassistant/helpers/entity_platform.py` and `Entity.async_prepare_to_add_to_hass` in `homeassistant/helpers/entity.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `entity.py` at the `2026.9.0` tag |
| `self.async_on_remove(self._unsub)` for a subscription that `async_entity_id_changed` makes again | `self.async_on_remove(lambda: self._unsub())` | the bound function is the first subscription's, so removing the entity calls a stale unsubscribe and the new subscription leaks | https://contributors.home-assistant.io/blog/2026/10/12/new-entity-lifecycle-hooks/ |
| a collection sensor whose state is the raw list or a timestamp | the `len()` count with `_attr_state_class = MEASUREMENT`, and a sensor of its own for any other value worth a history | `last_updated` and `last_changed` are state attributes already, and a count graphs | https://contributors.home-assistant.io/core/entities/sensor/ |
| deleting `state_class` to silence an impossible-pair warning | the `state_class` that device class permits | deleting it drops long-term statistics altogether | `DEVICE_CLASS_STATE_CLASSES` in `homeassistant/components/sensor/const.py` |
| a `translation_key` whose `name` in `translations/en.json` is the device class's own name, on a `binary_sensor`, `button`, `event`, `number`, `sensor` or `update` entity with a device class and no `name` of its own, an `enum` sensor apart | drop the `translation_key` and its entry; where the key also carries other translations, states say, or an icon, or the code reads a `translation_key`, drop only its `name`; ha-integration-ci v5 fails the repeat (W7442) | those platforms name such an entity after its device class already | `checkers/redundant_translation_key.py` in core's `packages/pylint-home-assistant/pylint_home_assistant/`, at the `.0` tag of the release row in `reference/freshness.md` |
| redeclaring an attribute, property or method the base class — `SensorEntity`, `TrackerEntity` — already provides, or guarding against its behaviour changing | the base class as it stands | the base class is the stable API a platform builds on | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a lawn mower stopped but neither docked nor paused, reported as `LawnMowerActivity.PAUSED` or `ERROR` | `LawnMowerActivity.IDLE`; and for an action that cancels the task without docking, `LawnMowerEntityFeature.STOP` with `async_stop` — both from 2026.10.0 | `PAUSED` says the task can be resumed, `ERROR` that the mower needs help | `LawnMowerActivity`, `LawnMowerEntityFeature` and `LawnMowerEntity.async_stop` in `homeassistant/components/lawn_mower/`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `const.py` there at the `2026.9.0` tag |
| `current_temperature`, `target_temperature`, `target_temperature_high`, `target_temperature_low` or `temperature_unit` on a `ClimateEntity`, implemented, set as `_attr_*` or read | the `native_` name of each — `native_current_temperature`, `native_target_temperature`, `native_target_temperature_high`, `native_target_temperature_low`, `native_temperature_unit` — from 2026.11.0; `min_temp`, `max_temp` and `target_temperature_step` keep their names and stay in the native unit | the base class converts from the native unit and sets the `temperature_unit` state attribute itself; the old names log a warning and stop working in **2027.11** | the `DeprecatedEntityProperty` and `DeprecatedEntityAttr` beside each in `homeassistant/components/climate/entity.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `homeassistant/components/climate/__init__.py` at the `2026.10.0` tag |
| `current_temperature`, `target_temperature`, `target_temperature_high`, `target_temperature_low` or `temperature_unit` on a `WaterHeaterEntity`, implemented, set as `_attr_*` or read | the `native_` name of each, as on climate, from 2026.11.0; `min_temp`, `max_temp` and `target_temperature_step` keep their names and stay in the native unit | the base class converts from the native unit and sets the `temperature_unit` state attribute itself; the old names log a warning and stop working in **2027.11** | the `DeprecatedEntityProperty` and `DeprecatedEntityAttr` beside each in `homeassistant/components/water_heater/entity.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `homeassistant/components/water_heater/__init__.py` at the `2026.10.0` tag |
| `two_way_audio=True` on a camera that cannot take audio back over the stream Home Assistant uses | `_attr_camera_entity_capabilities = CameraEntityCapabilities(two_way_audio=…)`, from 2026.11.0, true only where the device has a speaker and the stream Home Assistant takes from it carries audio back — Reolink's only over RTSP | the platform passes the claim to the frontend whenever the stream is WebRTC and the Labs preview feature is on, and checks nothing about the device | `CameraEntityCapabilities` and `Camera.camera_capabilities` in `homeassistant/components/camera/entity.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `homeassistant/components/camera/__init__.py` at the `2026.10.0` tag; https://contributors.home-assistant.io/blog/2026/10/24/camera-two-way-audio/ |
| a new legacy device tracker platform — `get_scanner`, `async_get_scanner`, `setup_scanner` or `async_setup_scanner` in `device_tracker.py`, a `DeviceScanner`, the `see` or `async_see` callback, devices kept in `known_devices.yaml` — or a feature added to an existing one | config entry `ScannerEntity` or `TrackerEntity` entities | legacy device trackers log as deprecated at setup, and are removed in **2027.5** | `DeviceTrackerPlatform.async_setup_legacy` in `homeassistant/components/device_tracker/legacy.py`, whose warning gives the 2027.5, and `.claude/skills/ha-integration-knowledge/platform-device-tracker.md` in core, both at the `.0` tag of the release row in `reference/freshness.md` |
| carrying the legacy trackers over when config entry entities replace a legacy platform — a `SOURCE_IMPORT` flow started from the legacy platform's setup, reading or editing `known_devices.yaml` (`YAML_DEVICES`, `async_load_config`, `remove_device_from_config`, `load_yaml_config_file`), `self.entity_id = "device_tracker.<dev_id>"`, `hass.states.async_remove` on a legacy state, or enabling entities by the file's `track` | new entities on IDs of their own, with the legacy platform left working until it is removed | a `known_devices.yaml` entity has no entity registry entry and keeps `device_tracker.<dev_id>` until the legacy device tracker is removed, so a config entry entity on that ID is dropped at startup or gets an `_2` suffix while the legacy one keeps writing stale states | `.claude/skills/ha-integration-knowledge/platform-device-tracker.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| telling users of a replaced legacy platform only to remove it from `configuration.yaml`, or raising core's `deprecated_yaml` issue for it | a repair issue raised from the legacy platform's setup, only for a platform with a config entry replacement, with `breaks_in_ha_version="2027.5.0"` and a translation key of the integration's own, giving the steps in this order: remove the platform from `configuration.yaml`; remove the tracked devices' entries from `known_devices.yaml`, then restart; set up the integration from the UI and enable the new trackers to use; change their entity IDs to the old ones where needed | while the platform is set up it keeps adding devices to `known_devices.yaml`, the legacy entity IDs stay in use until the restart, and `deprecated_yaml` says the configuration was imported | `.claude/skills/ha-integration-knowledge/platform-device-tracker.md` in core, and the `breaks_in_ha_version` of the `deprecated_see_action` issue in `async_setup_integration` in `homeassistant/components/device_tracker/legacy.py`, both at the `.0` tag of the release row in `reference/freshness.md` |
| `battery_level` on a `device_tracker` entity | a dedicated `SensorDeviceClass.BATTERY` sensor | stops working in **2027.7** | `BaseTrackerEntity.__init_subclass__` in `homeassistant/components/device_tracker/entity.py` |
| `TrackerEntity.location_name` | `in_zones` — zone entity ids, in any order, since the base class sorts them | stops working in **2027.7** | `TrackerEntity.in_zones` in `homeassistant/components/device_tracker/entity.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `battery_level` on `StateVacuumEntity` | a dedicated battery sensor | already removed, in 2026.9 | the Vacuum entry under *Backward-incompatible changes* at https://www.home-assistant.io/blog/2026/09/02/release-20269/ |
| a `TrackerEntity` for a device tracked by connection rather than position | `BaseScannerEntity` | it derives the state from the associated zone and sets the `tracking_type` capability attribute | https://contributors.home-assistant.io/blog/2026/06/15/device-tracker-changes/ |
| a `ScannerEntity` with a MAC address and no device info, left to the device the base class makes for it | `_attr_device_info = DeviceInfo(connections={(CONNECTION_NETWORK_MAC, client.mac)}, name=client.name)` for the tracked client's device, or `_attr_device_info = DeviceInfo()` for none — from 2026.11.0, when `device_info` stopped being final | the default device is logged now, and stops working in **2027.11.0** | `ScannerEntity._async_set_default_device_info` in `homeassistant/components/device_tracker/entity.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the `@final` `ScannerEntity.device_info` in the same file at the `2026.10.0` tag |
| a `ScannerEntity` that is its device's main feature, with an `_attr_name` or a `name` property | `_attr_has_entity_name = True` and `_attr_name = None`, with the client's name on the device, renamed with `async_update_device` when the client's name changes | a name of its own doubles the device's, `device_tracker.printer_printer` | https://contributors.home-assistant.io/blog/2026/10/28/scanner-entity-devices/ |
| `original_name` read off a tracker's entity registry entry, to name a client that is offline at startup | the name of its device | `original_name` is `None` for a tracker with no name | https://contributors.home-assistant.io/blog/2026/10/28/scanner-entity-devices/ |
| counting on a `ScannerEntity` being enabled because its MAC address belongs to another integration's device | `_attr_entity_registry_enabled_default = True`, only where tracking is the device's purpose or the user set the tracked device up on its own | every `ScannerEntity` is disabled by default from 2026.11.0 | `ScannerEntity` in `homeassistant/components/device_tracker/entity.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `ScannerEntity.entity_registry_enabled_default` in the same file at the `2026.10.0` tag |
| a base class of your tracker that sets `_attr_device_info` for another device, the router say | make sure the tracker belongs in that device, or override it | it was ignored before 2026.11.0, and now puts the tracker in that device | https://contributors.home-assistant.io/blog/2026/10/28/scanner-entity-devices/ |
| `RestoreStateData.last_states`, read for a stored state | `restore_state.async_get(hass).async_get_stored_state(entity_id)`, from 2026.11.0; below it, `restore_state.async_get(hass).last_states.get(entity_id)`, a dict keyed by entity_id there; an entity restores its own state through `RestoreEntity` and `async_get_last_state()` or `async_get_last_extra_data()` | removed in 2026.11, as stored states are keyed by entity registry id | `RestoreStateData.async_get_stored_state` in `homeassistant/helpers/restore_state.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `RestoreStateData.last_states` in the same file at the `2026.10.0` tag |

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
| a custom payload passed through `NotifyEntity` | an action of the integration's own, below | `data` is not in its service schema, which carries `message` and `title` only | https://contributors.home-assistant.io/core/entities/notify/ |

**A custom payload — animations, sounds, colours — sent through an action of the integration's own:**

| Rule | Value |
|---|---|
| the schema | a device field beside `message`, an optional `title` and an optional `data` dict, named as *Step 1: Register the custom services* in `reference/services.md` says |
| the handler | resolves the device from the device field, as that step does, then reads the optional `data`, or `{}`, beside the message |
| registering | once, as that step says, never per device in `async_setup_entry`, which ha-integration-ci v5 fails (W7452) |
| removing | nothing: the action stays registered while the integration is loaded |
| what it creates | one action of the integration's domain, `my_device.send_message` say, whose device field picks the device, with full `data` support |

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
| a device or service that says itself whether an update is available | override the `has_update` property, from 2026.11.0; core reads it only when both versions are known, differ and the latest is not skipped, and its default calls `version_is_newer` — `UpdateEntity.has_update` and `state` in `homeassistant/components/update/entity.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `homeassistant/components/update/__init__.py` at the `2026.10.0` tag |

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
| what `async_redact_data` walks | mappings and lists, and from 2026.11.0 a `DeviceInfo` or `ChildDeviceInfo`, through its own `as_dict()`, where below it both were dicts; any other object inside the dict passes through unredacted, so turn each device's dataclass into a dict with `asdict` first, keyed by device id as `coordinator.data` is — the floor, `util.py` at the `2026.10.0` tag |
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
| the parts of one physical product — a power strip's outlets, a wall switch's gangs | child devices, from 2026.9.0: a `ChildDeviceInfo(identifiers=…, name=…, parent_device_id=parent.id)` from the part's entities' `device_info`, or `async_get_or_create_child(config_entry_id=…, parent_device_id=…, identifiers=…)` for a part with no entity, and from 2026.11.0 `async_get_or_create_child_from_info` for a `ChildDeviceInfo` you already hold — `ChildDeviceInfo`, `DeviceRegistry.async_get_or_create_child` and `async_get_or_create_child_from_info` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.8.0` tag |
| `via_device_id` | a gateway or hub between separate physical products, and nothing else |
| a child's parent | a main device, registered first by the same config entry, in the same subentry; a child is never a parent |
| a child whose identifiers match an existing device of the same config entry | that device is converted to the child in place and keeps its id, so automations that target it keep working |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `DeviceEntry.config_entries`, on a main, child or deleted device | `config_entry_id`, which is `None` on a deleted device whose config entry is gone, where the property gave an empty set | a compatibility property returning `{config_entry_id}`, logged from 2026.10; stops working in **2027.10.0** | `_report_deprecated_config_entries_property` in `homeassistant/helpers/device_registry.py` |
| `DeviceEntry.config_entries_subentries`, on a main, child or deleted device | `config_entry_id` and `config_subentry_id` | a compatibility property returning `{config_entry_id: {config_subentry_id}}`, logged from 2026.10; stops working in **2027.10.0** | `_report_deprecated_config_entries_property` in `homeassistant/helpers/device_registry.py` |
| `DeviceEntry.primary_config_entry`, on a main or child device | `config_entry_id` | a compatibility property returning `config_entry_id` itself, logged from 2026.10; stops working in **2027.10.0** | `BaseDeviceEntry.primary_config_entry` in `homeassistant/helpers/device_registry.py` |
| a loop over a device's config entries to find your own | `async_get_device_and_config_entry_for_domain(hass, device_id, domain=DOMAIN)` | the loop gets a pre-migration composite device id wrong, which the helper resolves | `async_get_device_and_config_entry_for_domain` in `homeassistant/helpers/device_registry.py` |
| `device_info["sw_version"] = …`, `device_info.get("name")`, `device_info.update({…})` | the attribute — `device_info.sw_version = …`, `device_info.name`, one assignment per field | a compatibility layer core will deprecate, with no release named yet | `_DeviceInfoMapping` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md`; https://contributors.home-assistant.io/blog/2026/10/13/device-info-class/ |
| `DeviceInfo({…})`, `DeviceInfo(**payload)` carrying a key that is no field, `device_info["config_entry_id"] = …` | keyword arguments that name fields; `config_entry_id` and the other `async_get_or_create` arguments go to that call | a mapping argument and an unknown keyword raise `TypeError`, an unknown key `KeyError` | `DeviceInfo` and `_DeviceInfoMapping.__setitem__` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `device_info.copy()`, `setdefault`, `pop`, `del device_info[key]`, `\|`, `\|=`, a loop over it, `len()` | `copy.copy(device_info)`; to unset a field, assign `UNDEFINED` to it | none of them works on the dataclass, and no compatibility layer covers them | `_DeviceInfoMapping` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `isinstance(device_info, dict)`, or `if not device_info:` for an empty one | `isinstance(device_info, DeviceInfo)`, and `as_dict()` where a plain dict is needed | a `DeviceInfo` is no dict, and an empty `DeviceInfo()` is truthy | https://contributors.home-assistant.io/blog/2026/10/13/device-info-class/ |
| `device_info.name is None`, or `not device_info.name`, to find a field that is unset | `device_info.name is UNDEFINED`, with `UNDEFINED` from `homeassistant.helpers.typing` | `None` is a value — `via_device_id=None` removes the link — and `UNDEFINED` is truthy | https://contributors.home-assistant.io/blog/2026/10/13/device-info-class/ |
| a field tested for with `hasattr` or a `try`, to support an older Home Assistant | `"via_device_id" in DeviceInfo.__annotations__` | `__optional_keys__` and `__required_keys__` still answer, as part of the compatibility layer | https://contributors.home-assistant.io/blog/2026/10/13/device-info-class/ |
| a `DeviceInfo` stored, sent in event data or a WebSocket message, or held by a dataclass that is serialised | `device_info.as_dict()`, which returns the set fields | orjson writes every unset field as `0`, and `dataclasses.asdict` keeps it as `UNDEFINED` | `_DeviceInfoMapping.as_dict` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md`; https://contributors.home-assistant.io/blog/2026/10/13/device-info-class/ |
| `async_get_or_create(config_entry_id=…, **device_info)`, for a `DeviceInfo` you already hold | `async_get_or_create_from_info(config_entry_id=…, device_info=device_info)`, from 2026.11.0 | it takes the `DeviceInfo` as it is, where unpacking goes through the compatibility layer | `DeviceRegistry.async_get_or_create_from_info` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.10.0` tag |
| a write to the `DeviceInfo` that `sensor_device_info_to_hass_device_info()` returns | `copy.copy(device_info)` first; where every advertisement adds the same fields, build and cache your own `DeviceInfo` | it is cached and shared between devices, so every write raises `TypeError` | `sensor_device_info_to_hass_device_info` and `_SharedDeviceInfo` in `homeassistant/helpers/sensor.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `DeviceInfo(via_device=…)`, `async_get_or_create(via_device=…)` | `via_device_id`, looked up with `async_get_device_id_by_identifier(hass, identifier, config_entry_id=…)` | an identifier is unique only within a config entry; stops working in **2027.8.0** | `_DEPRECATED_DEVICE_INFO_PARAMETERS` and `DeviceRegistry._async_get_or_create_from_info` in `homeassistant/helpers/device_registry.py` |
| `ATTR_VIA_DEVICE`, imported from `homeassistant.const` | the string `"via_device_id"` | logged on import; removed in **2027.8** | the `DeprecatedConstant` for `ATTR_VIA_DEVICE` in `homeassistant/const.py` |
| `device_info` or `device_entry` on an entity with no `unique_id`, or on one added by a platform with no config entry | a `unique_id`, on an entity a config entry's platform adds | the device link is dropped and logged already, so the entity has no device; raises from **2027.8.0** | `EntityPlatform._check_device_attach` in `homeassistant/helpers/entity_platform.py` |
| a field beside its `default_` twin — `DeviceInfo(name=…, default_name=…)`, `DeviceInfo(model=…, default_model=…)` — or a `translation_key` beside `default_name` | the plain field alone | it raises `DeviceInfoError`, so the entity is not added and the log reads `<domain>: Not adding entity, error adding device: …` | `_validate_device_info` in `homeassistant/helpers/device_registry.py` and `EntityPlatform._async_add_entity_impl` in `homeassistant/helpers/entity_platform.py`, and https://contributors.home-assistant.io/blog/2026/08/24/device-registry-follow-up-changes/ |
| a `via_device` or `via_device_id` naming the device itself | drop the self-reference | `via_device_id` raises `HomeAssistantError` already; `via_device` is ignored and logged, and raises from **2027.8.0** | `async_get_or_create` and `async_update_device` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a composite device id passed as `via_device_id` | the id of one real device | resolved and logged now; stops working in **2027.8** | `DeviceRegistry._resolve_via_device_id` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.async_get_device()` | `async_get_device_by_identifier()`, `async_get_device_by_connection()` or `async_get_devices()`, each with the config entry id | the lookup is ambiguous once identifiers repeat across entries; stops working in **2027.8.0** | `DeviceRegistry.async_get_device` in `homeassistant/helpers/device_registry.py` |
| `async_update_device(add_config_entry_id=…, add_config_subentry_id=…, remove_config_entry_id=…, remove_config_subentry_id=…)` | `new_config_entry_id`, `new_config_subentry_id`, or `async_remove_device` | a move is no longer an add plus a remove; stops working in **2027.8.0** | `DeviceRegistry.async_update_device` in `homeassistant/helpers/device_registry.py` |
| `async_get_or_create` re-registering an existing device under a different subentry | `async_update_device(new_config_subentry_id=…)` | it silently moves the device; raises from **2027.8.0** | `DeviceRegistry.async_get_or_create` in `homeassistant/helpers/device_registry.py` |
| a `disabled_by` that contradicts the owning config entry or the parent device | leave it `UNDEFINED` and let the registry derive it | the value is dropped and logged now, and a child enabled under a disabled parent is logged and kept disabled; raises from **2027.8** | `DeviceRegistry._async_update_device` and `_async_update_child_device` in `homeassistant/helpers/device_registry.py` |
| `async_update_device(merge_connections=…, merge_identifiers=…)` | `new_connections`, `new_identifiers`, with the full set computed yourself | merging only ever adds; stops working in **2027.9.0** | `DeviceRegistry.async_update_device` in `homeassistant/helpers/device_registry.py` |
| `default_manufacturer`, `default_model` or `default_name`, on a `DeviceInfo` or passed to `async_get_or_create` | `manufacturer`, `model`, `name` | there is no primary integration left to defer to; stops working in **2027.9.0** | `_DEPRECATED_DEVICE_INFO_PARAMETERS` and `DeviceRegistry._async_get_or_create_from_info` in `homeassistant/helpers/device_registry.py` |
| `created_at` or `modified_at`, on a `DeviceInfo` or passed to `async_get_or_create` | drop them | the registry owns both and always ignored them; stops working in **2027.9.0** | `_DEPRECATED_DEVICE_INFO_PARAMETERS` and `DeviceRegistry._async_get_or_create_from_info` in `homeassistant/helpers/device_registry.py` |
| `suggested_area` read off `DeviceEntry`, or passed to `async_update_device` | drop it; `DeviceInfo`, `ChildDeviceInfo`, `async_get_or_create` and `async_get_or_create_child` still take it, and set a new device's area from it | removed in 2026.11: the read raises `AttributeError`, the argument `TypeError` | `DeviceEntry` and `DeviceRegistry.async_update_device` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md`; both still at the `2026.10.0` tag |
| a non-`str` value in a device-registry string field (`model`, `sw_version`, …) | pass a `str` | coerced with a warning now; stops working in **2026.12.0** | `_validate_str` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.devices` as a mapping — `.get()`, `.values()`, `.keys()`, `registry.devices[id]`, `device_id in registry.devices` | iterate it for the entries, `async_get(device_id)` for a lookup | it is a read-only collection now; the mapping shim stops working in **2027.9.0** | `_DeprecatedDeviceRegistryItemsView` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.child_devices` as a mapping | iterate it | there is no compatibility shim at all: no `.get()`, no `.values()`, no lookup by id | `DeviceRegistry._async_load` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.deleted_devices` | nothing — it is an internal detail of the registry | stops working in **2027.9.0** | `DeviceRegistry.deleted_devices` in `homeassistant/helpers/device_registry.py` |
| `DeviceRegistry.async_is_composite_device_id()` | `async_get(device_id, include_composite_devices=False)` returning `None` | the parameter makes the same test; stops working in **2027.9.0** | `DeviceRegistry.async_is_composite_device_id` in `homeassistant/helpers/device_registry.py` |
| a part of one product registered as a device of its own and linked to the product with `via_device` or `via_device_id` | a child device that keeps the part's identifiers, so the existing device converts in place; drop the via link and any parent-name prefix from its name | the via link says how Home Assistant reaches a device, not which product a part belongs to | https://contributors.home-assistant.io/blog/2026/10/22/child-devices/ |
| a part registered as a main device earlier in the same setup — through a `DeviceInfo` left on one of its entities, say — and then as a child | register it only as a child | the conversion raises `DeviceInfoError` until the config entry unloads | `DeviceRegistry._async_validate_device_to_child_conversion` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a child of a parent in a config subentry, registered without `config_subentry_id` | pass the parent's `config_subentry_id` | an omitted one means no subentry, which raises `DeviceInfoError` | `DeviceRegistry._async_get_or_create_child_from_info` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `async_get_or_create` with a live child's identifiers, to make the child a main device again | `async_remove_device(child.id)` first, then `async_get_or_create` with the same identifiers, and add the child's entities again with a `DeviceInfo` | identifiers that overlap a child's raise `DeviceInfoError`, and removing a child removes its entities' registry entries | `DeviceRegistry._async_get_or_create_from_info` in `homeassistant/helpers/device_registry.py`, at the `.0` tag of the release row in `reference/freshness.md`; https://contributors.home-assistant.io/blog/2026/10/22/child-devices/ |
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

### Serving an image — Step 1

| Scenario | Choice |
|---|---|
| where each row was read | `ImageEntity` in `homeassistant/components/image/entity.py`, `ImageView` and `TOKEN_CHANGE_INTERVAL` in `homeassistant/components/image/__init__.py`, `_async_get_image` and `TOKEN_CHANGE_INTERVAL` in `homeassistant/components/camera/__init__.py`, `Entity.entity_picture` in `homeassistant/helpers/entity.py`, `Config.cache_path` in `homeassistant/core_config.py` and `process_uploaded_file` in `homeassistant/components/file_upload/__init__.py`, at the `.0` tag of the release row in `reference/freshness.md`; *Fetching and caching* at https://contributors.home-assistant.io/core/entities/image/index.md |
| a still that changes now and then — a map, a chart, the last snapshot of a doorbell, a QR code | an `image` entity: return the bytes the coordinator holds from `async_image`, and move `image_last_updated` when a new image arrives, never inside `async_image`, which runs on every fetch; or set `image_url`, which the base class downloads once and keeps in `_cached_image` |
| a frame grabbed now from a live or near-live camera | a `camera` entity: core calls `async_camera_image` on every request and keeps no copy, so hold the last frame in memory and fetch again only after a minimum interval |
| what the browser loads for an `image` or `camera` entity | the URL the base class puts in `entity_picture`, `/api/image_proxy/<entity_id>` or `/api/camera_proxy/<entity_id>` with a token core rotates every five minutes, so the integration holds no URL and no token |
| a picture for any other entity that needs credentials, or is reachable only on the LAN | an `image` entity beside it: `_attr_entity_picture` reaches the browser as it stands, with no proxy and no token |
| a file the integration ships and serves unchanged — a sound, a placeholder, a panel bundle | a static path registered once — *Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 1* in `reference/services.md`, and for a panel *Step 3: Register the static path and the panel in `async_setup`* in `reference/panels.md` |
| the integration's icon and logo | *Step 5: Add the brand images to `brand/`* in `reference/scaffold.md` |
| a media player's artwork, or the thumbnails of its media browser | *Artwork in the browser* at https://contributors.home-assistant.io/core/entities/media-player/index.md |
| a media source item whose resolved media is a stream of images, MJPEG say | `MediaSource.async_get_media_image`, from 2026.11.0, so a consumer can fetch one image — its docstring in `homeassistant/components/media_source/models.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.10.0` tag |
| a copy on disk of an image that can be fetched again — event snapshots, downloads | `hass.config.cache_path(DOMAIN, …)`, which is `<config>/.cache/<domain>/`, kept across a restart and left out of backups |
| a picture the user uploads in a config flow | the `file` selector, then `process_uploaded_file` in the executor, copying the file to a folder of the integration's own under `hass.config.path()` before the context closes, which deletes it |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `ImageEntity.__init__(self, hass)`, left at its default `verify_ssl=False` | `ImageEntity.__init__(self, hass, verify_ssl=entry.data[CONF_VERIFY_SSL])`, from a config-flow field that defaults to `True` | the base class turns certificate checks off unless told otherwise | *Keep certificate checks on* at https://contributors.home-assistant.io/security/guides/integrations/; `ImageEntity.__init__` in `homeassistant/components/image/entity.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a new `image_url` set while `_cached_image` still holds the old download | `self._cached_image = None` wherever the URL or the picture behind it changes, then a new `image_last_updated` | the base class never clears the copy, so the old picture keeps being served | *Fetching and caching* at https://contributors.home-assistant.io/core/entities/image/; `ImageEntity.async_image` in `homeassistant/components/image/entity.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| a cache the integration writes under `custom_components/<domain>/` | `hass.config.cache_path(DOMAIN, …)` | every Marketplace update replaces the whole integration folder | *Keep user files across updates* at https://contributors.home-assistant.io/marketplace/guides/integrations/ |
