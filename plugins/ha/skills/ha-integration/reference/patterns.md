# Implementation patterns, file structure and typing

Read this when writing or changing the package under `custom_components/` — its Python,
`strings.json`, `services.yaml` and translations. Panel code is `reference/panels.md`, tests
`reference/testing.md`, the manifest *Step 6: Order `manifest.json`* in `reference/scaffold.md`.

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
8. Notify platform (modern pattern — HA 2023.8+) — Step 1
9. Entity platform files — Step 1
10. `EntityDescription` pattern — Step 1
11. `UpdateEntity` (firmware/OTA install) — Step 1
12. `DataUpdateCoordinator` (polling) — Step 1
13. Entity push subscriptions — Step 1
14. A connection that drops — Step 1
15. A reply the code does not expect — Step 1
16. A blocking call inside the event loop — Step 1
17. `ConfigEntry` mutation — Step 3
18. Logging — Step 1
19. Custom services — Step 1
20. `services.yaml` + `strings.json` (hassfest rules) — Step 1
21. Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 3
22. Diagnostics platform — Step 1
23. Devices belong to one config entry — Step 3
24. Units: prefer the enumerators — Step 1
25. Config entry migration — Step 3
26. Deprecated platform APIs — Step 1
27. Announced for a release after 2026.9 — Step 1
28. `TYPE_CHECKING` for expensive or circular imports — Step 4
29. Typed `ConfigEntry` — Step 4

## Writing code in `custom_components/`

### Step 1: Lay out the files by responsibility

The developer docs' set — https://developers.home-assistant.io/docs/creating_integration_file_structure/
— plus the splits the quality scale asks for and the ones this skill adds. If `__init__.py`
exceeds ~100 lines of logic, extract. `api.py` is the split that matters most: it decouples
device logic from the HA lifecycle, so it is unit-testable without a running HA instance.

| File | Holds | Taken from |
|---|---|---|
| `__init__.py` | `async_setup_entry`, `async_unload_entry`, `async_migrate_entry` only — no business logic | the file-structure page names it; the no-business-logic constraint is this skill's |
| `<platform>.py` | one per HA platform — `sensor.py`, `switch.py`, `light.py`, `button.py`, … | the file-structure page |
| `coordinator.py` | `DataUpdateCoordinator` subclass | the `common-modules` rule, https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/common-modules/ |
| `entity.py` | shared base entity class when several platforms extend the same base | the `common-modules` rule |
| `config_flow.py` | config and options flows | the `config-flow` rule in `reference/quality-scale.md` |
| `diagnostics.py` | `async_get_config_entry_diagnostics` | the `diagnostics` rule in `reference/quality-scale.md` |
| `api.py` | all I/O to the device or service — no HA imports | this skill |
| `models.py` | dataclasses and type aliases for device data | this skill |
| `const.py` | constants only — no imports from other local modules | this skill |
| `services.py` | `async_setup_services(hass)` called from `async_setup` | this skill |
| `migration.py` | `async_migrate_entry` logic when it is complex; import into `__init__.py` | this skill |
| `helpers.py` / `util.py` | pure functions shared across platforms | this skill |

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
   `ConfigEntry.async_unload` runs it once the unload succeeds — at the `2026.9.0` tag,
   `homeassistant/helpers/update_coordinator.py` and `homeassistant/config_entries.py`.
4. If setup creates a device, add `async_remove_config_entry_device` so a user can remove it.
   Type its device parameter `AnyDeviceEntry` (`DeviceEntry | ChildDeviceEntry`), since from
   2026.9 Home Assistant hands it a child device too — `_async_remove_device` in
   `homeassistant/components/config/device_registry.py` at the `2026.9.0` tag.
5. If the entity carries `_attr_translation_key`, add the matching block to `strings.json`
   and `translations/en.json` — `entity-translations` in `reference/quality-scale.md`.

What the audit checks of this list at PR time, and how, is *What the audit checks now* in
ha-integration-ci's README.

### Step 4: Type it, and suppress nothing

The `strict-typing` rule in `reference/quality-scale.md`. Every file passes the mypy run
*Lint & quality check* in `SKILL.md` names, under the shipped `mypy.ini`, with zero errors,
before a PR is ready.

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
| `# type: ignore` to silence a typing error | fix the type | under `strict-typing` a suppression is a violation, not a shortcut, and the `mypy.ini` enables `ignore-without-code`, so a codeless one fails the run outright | https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/strict-typing/, and `templates/mypy.ini` |
| `# type: ignore[import-untyped]` on a stubless third-party import | nothing — import it plainly | the `mypy.ini` disables `import-untyped` and fails an unused ignore, so the leftover one is the error | `templates/mypy.ini` |
| `hass.data[DOMAIN][entry.entry_id]`, which is untyped | `entry.runtime_data` on a typed `ConfigEntry` | the alias carries the runtime type, so no cast is needed | https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data/, and *Typed `ConfigEntry` — Step 4* |

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
| a `vol.Schema` in a flow | one entry per line, left to `ruff format` |
| the `# fmt: off` fence | not earned here — a flow schema is a list of entries, not a table; *Alignment a human chose meets `ruff format` — Step 2* in `reference/scaffold.md` |

```python
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="192.168.1.1"): str,
        vol.Required(CONF_PORT, default=8080): int,
    }
)
```

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `OptionsFlowHandler` | `OptionsFlow` | the old name is deprecated | Step 1 |
| a config-entry update listener alongside a reloading method | drop the listener, or call `async_update_and_abort()` in place of `async_update_reload_and_abort()` and pass `reload_on_update=False` to `_abort_if_unique_id_configured()` | the integration reloads twice or races; an error from **2026.12** | Step 1 |
| `FlowHandler.show_advanced_options`, or the `show_advanced_options` key in `FlowHandler.context` | group the extra fields in a schema `section` | the property returns `True` unconditionally and the context key is already gone; removed **2027.6** | Step 1 |
| a hand-written `SelectSelector` of device-class values | `DeviceClassSelector` | it carries HA's own values, so the hand-written translations for them go too | Step 1 |

### Notify platform (modern pattern — HA 2023.8+) — Step 1

The entity itself is https://developers.home-assistant.io/docs/core/entity/notify/; these are
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
| `discovery.async_load_platform` with a `BaseNotificationService` | `NotifyEntity` | the legacy pair is deprecated and fails silently rather than erroring | Step 1 |
| a custom payload passed through `NotifyEntity` | a service registered directly, below | `data` is not in its service schema, which carries `message` and `title` only | https://developers.home-assistant.io/docs/core/entity/notify/ |

**A custom payload — animations, sounds, colours — registered as its own service:**

| Rule | Value |
|---|---|
| the schema | `vol.Required(ATTR_MESSAGE): cv.string`, `vol.Optional(ATTR_TITLE): cv.string`, `vol.Optional(ATTR_DATA): dict` — the constants and `DOMAIN as NOTIFY_DOMAIN` from `homeassistant.components.notify.const` |
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
| `_attr_translation_key = "my_key"` | translated entity names and states; pairs with the `entity` section of `strings.json` |
| `_attr_entity_category` | on a non-primary entity: `EntityCategory.DIAGNOSTIC` for read-only info such as RSSI, `EntityCategory.CONFIG` for a setting that changes device behaviour |
| a value set at init or on update | an `_attr_*` class or instance attribute, assigned in `__init__` or in `_handle_coordinator_update`, never a property method |
| a value derived on read, from `self.coordinator.data` say | a property — https://developers.home-assistant.io/docs/core/entity/ |
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
| a disallowed pair | logs *"is using state class X which is impossible considering device class Y"* and drops long-term statistics |
| the pair once chosen | locked by an attribute test |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `update_before_add=True` on `async_add_entities` | compute `native_value` as a property off `self.coordinator.data`, or call `self._handle_coordinator_update()` at the end of `async_added_to_hass`, after `await super().async_added_to_hass()` | it schedules a debouncer timer that outlives the test and the frozen clock | Step 1 |
| a collection sensor whose state is the raw list or a timestamp | the `len()` count, the items in an attribute, `_attr_state_class = MEASUREMENT` | `last_updated` and `last_changed` are state attributes already, and a count graphs | Step 1 |
| deleting `state_class` to silence an impossible-pair warning | the `state_class` that device class permits | deleting it drops long-term statistics altogether | `DEVICE_CLASS_STATE_CLASSES` in `homeassistant/components/sensor/const.py` |

**Symptom:** `CoordinatorEntity` does not push initial state on add, so an entity that sets
`_attr_native_value` inside `_handle_coordinator_update` reads `unknown` until the next poll
— `first_refresh` has already run, so the data is there to read.

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
| what `_attr_in_progress` does | greys out the dashboard install button, and nothing else |
| what it does not do | stop a second entry from a service call, an automation or two quick clicks |
| the actual lock | a boolean plus a monotonic timestamp, set at the top of `async_install` after the can't-install checks |
| the window on that lock | so a crashed or timed-out install cannot wedge the entity |

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
- `update_interval` minimum 5 s
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
| where each row was read | https://developers.home-assistant.io/docs/integration_setup_failures/, https://developers.home-assistant.io/docs/integration_fetching_data/ and the `entity-unavailable` and `log-when-unavailable` rules; `homeassistant/config_entries.py`, `homeassistant/helpers/update_coordinator.py` and `homeassistant/components/mqtt/client.py` at the `2026.9.0` tag |
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
| `ConfigEntryNotReady` raised from a platform's `async_setup_entry` | raise it from `__init__.py` | it is too late there to be caught by the config entry setup | https://developers.home-assistant.io/docs/integration_setup_failures/ |
| `asyncio.create_task` or `hass.async_create_task` for the reconnect loop | `entry.async_create_background_task` | unload cancels the entry's background tasks and no others, so the loop outlives a reload | `_async_process_on_unload` in `homeassistant/config_entries.py`, at the `2026.9.0` tag |
| the last value left showing while the connection is down | mark the entity unavailable | unavailable is the better state than the last known one | https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unavailable/ |

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
| where each row was read | the `entity-unavailable` and `dynamic-devices` rules; `_async_refresh` and `async_update_listeners` in `homeassistant/helpers/update_coordinator.py` and `SensorEntity.state` in `homeassistant/components/sensor/__init__.py`, at the `2026.9.0` tag |
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
| `raw["field"]` in `_async_update_data` | `.get()` into a field that may be `None` | the `KeyError` is an unexpected error, which takes every entity down for one field | `_async_refresh` in `homeassistant/helpers/update_coordinator.py`, at the `2026.9.0` tag |
| `except Exception: return self.data`, to ride out a bad reply | raise `UpdateFailed` | the entities go on showing the last value as though it were current | https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unavailable/ |
| an entity made unavailable for one missing field | `None`, which reads `unknown` | unavailable is for a fetch that failed, unknown for a piece that is missing | https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-unavailable/ |

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
| where each row was read | https://developers.home-assistant.io/docs/asyncio_blocking_operations/, https://developers.home-assistant.io/docs/asyncio_imports/ and the `inject-websession` rule; `_BLOCKING_CALLS` in `homeassistant/block_async_io.py`, `raise_for_blocking_call` in `homeassistant/util/loop.py` and `async_add_executor_job` in `homeassistant/core.py`, at the `2026.9.0` tag |
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
| `time.sleep` in a coroutine or a `@callback` | `await asyncio.sleep` | core raises as well as logging | `_BLOCKING_CALLS` in `homeassistant/block_async_io.py`, at the `2026.9.0` tag |
| moving only the `open` to the executor | move the reads and writes with it | core sees the `open` and nothing after it, so what is left is never reported | https://developers.home-assistant.io/docs/asyncio_blocking_operations/ |
| an `SSLContext` loaded with certificates on the loop | `async_get_clientsession`, `get_async_client`, or `homeassistant.util.ssl` for a context alone | loading the certificates is blocking disk I/O, which those three keep in the executor | https://developers.home-assistant.io/docs/asyncio_blocking_operations/ |
| an `import` inside a function on the loop, of a module not yet imported | a module-level import | the import machinery reads the module from disk | https://developers.home-assistant.io/docs/asyncio_imports/ |

### `ConfigEntry` mutation — Step 3
- Never mutate `ConfigEntry` directly — always use `hass.config_entries.async_update_entry(entry, data=..., options=...)`

### Logging — Step 1

Covers the rule `log-when-unavailable` (`reference/quality-scale.md`) and HA's logging conventions.

| Rule | Value |
|---|---|
| what the coordinator logs for you | on a poll, the first `UpdateFailed` at ERROR, each consecutive one at DEBUG, and the recovery — which is `log-when-unavailable` met; what it leaves to you on a push connection is *A connection that drops — Step 1* |
| what HA logs for you | the reason behind `ConfigEntryNotReady` and `ConfigEntryAuthFailed`, once |
| which exception to raise | transient → `UpdateFailed` or `ConfigEntryNotReady`; auth → `ConfigEntryAuthFailed`; an action's own failure → `HomeAssistantError` or `ServiceValidationError`, per `action-exceptions` |
| `INFO` | almost never: the one line saying a device or service is gone, and the one saying it is back, where `log-when-unavailable` asks for that level; setup, unload and teardown are `DEBUG` |
| `WARNING` | a recoverable thing the user should know |
| `ERROR` | an unexpected, actionable bug, never an expected transient failure |
| `DEBUG` | per-poll and developer detail |
| the message arguments | lazy `%` args — `_LOGGER.debug("added %s", key)`, which ruff `G004` enforces |
| the message prefix | none: `logging.getLogger(__name__)` already carries the module path |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| wrapping the fetch in your own `try`/log | raise `UpdateFailed` and let the coordinator log | the manual log double-logs and fails `log-when-unavailable` | https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/log-when-unavailable/ |
| `_LOGGER.exception(...)` beside a raise in `async_setup_entry` | raise alone | HA logs the reason once already | Step 1 |
| an f-string in a log call | a lazy `%` arg | the f-string evaluates even when the level is disabled | Step 1 |
| logging a credential, API key, token or raw auth response | log the fact, never the secret | a log is read by whoever is handed it | Step 1 |
| a module-level `_LOGGER` left behind after the calls go | delete it | ruff does not flag an unused module global | Step 1 |

### Custom services — Step 1

| Rule | Value |
|---|---|
| where to register | `async_setup`, not `async_setup_entry` — *Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 3* below says why |
| an entity-targeted action | `async_register_platform_entity_service()` |
| where a service is documented | `services.yaml`, with its icons in `icons.json` |
| a device dropdown | `selector: device` with `integration: {domain}`, never `selector: config_entry`, which the HA frontend labels "Integration" |
| resolving that device to your own config entry | `async_get_device_and_config_entry_for_domain`, in the handler — the helper core added in 2026.9 |
| a call with no target | `hass.services.async_call(DOMAIN, svc, …)` reaches every config entry, so pass your own `entry_id`/`device_id` and filter on it unless the call is a deliberate bulk one |

```python
from homeassistant.helpers.device_registry import (
    async_get_device_and_config_entry_for_domain,
)

device, entry = async_get_device_and_config_entry_for_domain(
    hass, call.data[ATTR_DEVICE_ID], domain=DOMAIN
)
```

| Scenario | Choice |
|---|---|
| an unknown device id, or a child device | `(None, None)` |
| a main device no config entry of your domain owns | `(device, None)` |
| a pre-migration composite device id | a matching split device and its config entry, which is the case a hand-written loop gets wrong |
| a composite device id no split matches | the restored composite device, and `None` |
| whether that config entry is loaded | not checked — keep your own `ConfigEntryState.LOADED` test |

### `services.yaml` + `strings.json` (hassfest rules) — Step 1

| Rule | Value |
|---|---|
| what `services.yaml` carries | field **structure** only — selectors, `required`, `default`, collapsible `sections` |
| what `strings.json` carries | every name and description, under a top-level `services` key: `services.{svc}.name/description`, `.fields.{key}.name/description`, `.sections.{key}.name` |
| a field key nested in a `sections` block in `services.yaml` | flat in `strings.json` all the same |
| `translations/en.json` | a copy of `strings.json` |
| a literal URL in a `strings.json` description | forbidden by hassfest — `the string should not contain URLs`; use plain text, or a `{placeholder}` filled via `description_placeholders` in the flow step |
| a markdown image `![x]({url})` with a placeholder | fine, since it leaves no literal `http` |
| a collapsible service form | `fields: { appearance: { collapsed: true, fields: {...} } }` |
| what a section changes in the call | nothing — sections are UI-only, the call data stays flat, so the voluptuous schema is unaffected |

### Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 3
The registration happens once per process; doing it per entry races when two entries set up in parallel. Claim the `hass.data` flag **before** the `await`, or both entries pass the check. The panel case, with the code, is `reference/panels.md`.

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
| where this was read | `async_redact_data` in `homeassistant/components/diagnostics/util.py`, and `homeassistant/components/nam/diagnostics.py`, at the `2026.9.0` tag |
| what goes in | the fields a bug report needs, each chosen — never `entry.runtime_data` whole |
| what `async_redact_data` walks | mappings and lists only, so an object inside the dict passes through unredacted; turn each device's dataclass into a dict with `asdict` first, keyed by device id as `coordinator.data` is |
| registration | none — HA discovers it from the file name |

### Devices belong to one config entry — Step 3

A device has exactly one config entry and at most one subentry: read `config_entry_id` and
`config_subentry_id`.

| Rule | Value |
|---|---|
| where each release below comes from | the `breaks_in_ha_version` of the call site that reports that usage, read at the `2026.9.0` tag in `homeassistant/helpers/device_registry.py` and `homeassistant/helpers/device.py` |
| a row naming no release | one core attaches none to |
| the WebSocket keys of the same names | `reference/panels.md` |
| a core caller | raises `RuntimeError` today wherever the call site sets `core_behavior=ReportBehavior.ERROR`, while a custom integration gets a logged warning until the row's release |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `DeviceEntry.config_entries` | `config_entry_id` | a compatibility property returning `{config_entry_id}`, carrying no `report_usage` and **no removal release stated by core** | Step 3 |
| `DeviceEntry.config_entries_subentries` | `config_entry_id` and `config_subentry_id` | a compatibility property returning `{config_entry_id: {config_subentry_id}}`, with **no removal release stated by core** | Step 3 |
| `DeviceEntry.primary_config_entry` | `config_entry_id` | a compatibility property returning `config_entry_id` itself, with **no removal release stated by core** | Step 3 |
| a loop over a device's config entries to find your own | `async_get_device_and_config_entry_for_domain(hass, device_id, domain=DOMAIN)` | the loop gets a pre-migration composite device id wrong, which the helper resolves | *Custom services — Step 1* |
| `DeviceInfo["via_device"]`, `async_get_or_create(via_device=…)` | `via_device_id`, looked up with `async_get_device_id_by_identifier(hass, identifier, config_entry_id=…)` | an identifier is unique only within a config entry; stops working in **2027.8.0** | Step 3 |
| a `via_device` or `via_device_id` naming the device itself | drop the self-reference | ignored and logged now; raises from **2027.8.0** | Step 3 |
| a composite device id passed as `via_device_id` | the id of one real device | resolved and logged now; stops working in **2027.8** | Step 3 |
| `DeviceRegistry.async_get_device()` | `async_get_device_by_identifier()`, `async_get_device_by_connection()` or `async_get_devices()`, each with the config entry id | the lookup is ambiguous once identifiers repeat across entries; stops working in **2027.8.0** | Step 3 |
| `async_update_device(add_config_entry_id=…, add_config_subentry_id=…, remove_config_entry_id=…, remove_config_subentry_id=…)` | `new_config_entry_id`, `new_config_subentry_id`, or `async_remove_device` | a move is no longer an add plus a remove; stops working in **2027.8.0** | Step 3 |
| `async_get_or_create` re-registering an existing device under a different subentry | `async_update_device(new_config_subentry_id=…)` | it silently moves the device; raises from **2027.8.0** | Step 3 |
| a `disabled_by` that contradicts the owning config entry or the parent device | leave it `UNDEFINED` and let the registry derive it | the value is dropped and logged now; raises from **2027.8** | Step 3 |
| `async_update_device(merge_connections=…, merge_identifiers=…)` | `new_connections`, `new_identifiers`, with the full set computed yourself | merging only ever adds; stops working in **2027.9.0** | Step 3 |
| `async_get_or_create(default_manufacturer=…, default_model=…, default_name=…)` | `manufacturer`, `model`, `name` | there is no primary integration left to defer to; stops working in **2027.9.0** | Step 3 |
| `async_get_or_create(created_at=…, modified_at=…)` | drop the arguments | the registry owns both and always ignored them; stops working in **2027.9.0** | Step 3 |
| `suggested_area` on `DeviceEntry`, `async_get_or_create` or `async_update_device` | drop it | it is ignored; **2026.9** on the property and **2026.9.0** on the `async_update_device` call site | Step 3 |
| a non-`str` value in a device-registry string field (`model`, `sw_version`, …) | pass a `str` | coerced with a warning now; stops working in **2026.12.0** | Step 3 |
| `DeviceRegistry.devices` as a mapping — `.get()`, `.values()`, `.keys()`, `registry.devices[id]`, `device_id in registry.devices` | iterate it for the entries, `async_get(device_id)` for a lookup | it is a read-only collection now; the mapping shim stops working in **2027.9.0** | Step 3 |
| `DeviceRegistry.child_devices` as a mapping | iterate it | there is no compatibility shim at all: no `.get()`, no `.values()`, no lookup by id | Step 3 |
| `DeviceRegistry.deleted_devices` | nothing — it is an internal detail of the registry | stops working in **2027.9.0** | Step 3 |
| `DeviceRegistry.async_is_composite_device_id()` | `async_get(device_id, include_composite_devices=False)` returning `None` | the parameter makes the same test; stops working in **2027.9.0** | Step 3 |
| a `DeviceEntry`-only attribute read off a child device — `connections`, `manufacturer`, `model`, `model_id`, `hw_version`, `sw_version`, `serial_number`, `configuration_url`, `entry_type`, `via_device_id` | branch on `parent_device_id`, then read the parent device | the shim hands back the `DeviceEntry` default, not the parent's value; stops working in **2027.9.0** | Step 3 |
| `async_device_info_to_link_from_entity()`, `async_device_info_to_link_from_device_id()` | `entity.device_entry = async_entity_id_to_device(hass, source_entity_id)` | both already return `None`; removed in **2027.8.0** | Step 3 |
| `async_remove_stale_devices_links_keep_entity_device()`, `async_remove_stale_devices_links_keep_current_device()` | `helper_integration.async_remove_helper_devices(…, remove_all_devices=True)` | both already do nothing; removed in **2027.8.0** | Step 3 |

> **Note:** the three compatibility properties are the supported way to read a *synthesized
> composite* device — the read-only entry `async_get()` returns for a pre-migration composite
> device id — because it spans several entries that `config_entry_id` cannot express.

### Units: prefer the enumerators — Step 1

| Rule | Value |
|---|---|
| `UnitOfDensity` | mass over volume — `GRAMS_PER_CUBIC_METER`, `MILLIGRAMS_PER_CUBIC_METER`, `MICROGRAMS_PER_CUBIC_METER`, `MICROGRAMS_PER_CUBIC_FOOT` |
| `UnitOfRatio` | ratios — `PARTS_PER_MILLION`, `PARTS_PER_BILLION`, `PERCENTAGE` |
| where each release below comes from | the version argument of the `DeprecatedConstantEnum` beside the constant in `homeassistant/const.py`, read at the `2026.9.0` tag |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `CONCENTRATION_GRAMS_PER_CUBIC_METER`, `CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER`, `CONCENTRATION_MICROGRAMS_PER_CUBIC_METER`, `CONCENTRATION_MICROGRAMS_PER_CUBIC_FOOT` | the matching `UnitOfDensity` member | removed in **2027.8** | Step 1 |
| `CONCENTRATION_PARTS_PER_MILLION`, `CONCENTRATION_PARTS_PER_BILLION` | the matching `UnitOfRatio` member | removed in **2027.8** | Step 1 |
| `CONCENTRATION_PARTS_PER_CUBIC_METER` | nothing — core names no replacement unit | removed in **2027.8** | Step 1 |
| `PERCENTAGE` as a unit of measurement, on a humidity or battery sensor | `UnitOfRatio.PERCENTAGE` | the constant itself is not deprecated and is now defined from the enum (`PERCENTAGE: Final = UnitOfRatio.PERCENTAGE.value`), but using it as a unit is | Step 1 |

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
**Return `True` or `False`, and log the reason yourself:** `ConfigEntry.async_migrate`
swallows every exception alike, and what replaces that is *Announced for a release after
2026.9 — Step 1* below. A major version bump with no `async_migrate_entry` fails setup for
every existing user, so ship the handler in the same change.

### Deprecated platform APIs — Step 1

The deprecations a custom integration can meet that have no section of their own above.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `mqtt.publish()` or `async_publish()` with `qos=None` or `retain=None` | the defaults, or typed values — the parameters are `qos: int = 0` and `retain: bool = False` | the `None` fallbacks stop working in **2027.6** | Step 1 |
| using a condition object as a callable | `async_condition_from_config()`, then `async_check()`, then `async_unload()`; a script is `async_run()` then `await script.async_unload()` | the callable form ends in **2027.1** | Step 1 |
| `BrowseMediaSource(domain=None)` | your own domain; the node listing every media source is `RootBrowseMediaSource` | `domain` is a required `str` now — a hard change with no deprecation period | Step 1 |
| `battery_level` on a `device_tracker` entity | a dedicated `SensorDeviceClass.BATTERY` sensor | stops working in **2027.7** | Step 1 |
| `TrackerEntity.location_name` | `in_zones` — zone entity ids, smallest zone first | stops working in **2027.7** | Step 1 |
| `battery_level` on `StateVacuumEntity` | a dedicated battery sensor | already removed, in 2026.9 | Step 1 |
| `async_initialize_triggers(home_assistant_start=…)` | stop passing it; `hass.async_add_startup_job` for work at startup | it already has no effect; removed in **2027.8** | Step 1 |
| a `TrackerEntity` for a device tracked by connection rather than position | `BaseScannerEntity` | it derives the state from the associated zone and sets the `tracking_type` capability attribute | Step 1 |

> **Note:** a condition platform may implement `_async_setup()` and `_async_unload()` when it
> needs async initialisation or teardown; it is optional and nothing else changes for it.

### Announced for a release after 2026.9 — Step 1

Cleared when the release row in `reference/freshness.md` moves past the landing release.

| what | lands in | do now | do then |
|---|---|---|---|
| `modbus.get_hub` is deprecated | 2026.10 | collect the connection details in your own config flow rather than a YAML hub | call `async_get_unit(hass, entry, connection_params, unit_id)`; `get_hub` is removed in 2027.10 |
| the `configurator` integration is deprecated | not stated — `components/configurator/` carries no deprecation at the `2026.9.0` tag | use a config flow and config entries | nothing; it is removed in 2027.10 |
| `async_migrate_entry` may raise a config-entry exception instead of returning `False` | not stated — neither the `ConfigEntryNotReady` path nor `ConfigEntries.async_retry_migration` exists at the `2026.9.0` tag | return `True`/`False` and log the reason yourself | raise `ConfigEntryNotReady` for something that may resolve itself; any other exception parks the entry in `migration_error` for a repair issue and a later `hass.config_entries.async_retry_migration(entry_id)` |

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
