# Implementation patterns, file structure and typing

Read this when writing or changing Python under `custom_components/`. Panel code is
`reference/panels.md`; tests are `reference/testing.md`.

**Pick the shape Home Assistant already models, then write that shape the way core writes
it.**

## Contents

1. Writing code in `custom_components/`
2. Step 1: Pick the shape HA models
3. Step 2: Wire the entry setup and unload
4. Step 3: Split the files by responsibility
5. Step 4: Type it, and suppress nothing
6. Cases
7. `config_flow.py` — Step 1
8. Notify platform (modern pattern — HA 2023.8+) — Step 1
9. Entity platform files — Step 1
10. `EntityDescription` pattern — Step 1
11. `UpdateEntity` (firmware/OTA install) — Step 1
12. `DataUpdateCoordinator` (polling) — Step 1
13. Entity push subscriptions — Step 1
14. `ConfigEntry` mutation — Step 2
15. Logging — Step 1
16. Custom services — Step 1
17. `services.yaml` + `strings.json` (hassfest rules) — Step 1
18. Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 2
19. Diagnostics platform — Step 1
20. Devices belong to one config entry — Step 2
21. Units: prefer the enumerators — Step 1
22. Config entry migration — Step 2
23. Deprecated platform APIs — Step 1
24. Announced for a release after 2026.9 — Step 1
25. `TYPE_CHECKING` for expensive or circular imports — Step 4
26. Typed `ConfigEntry` — Step 4
27. MicroPython firmware files — Step 4

## Writing code in `custom_components/`

### Step 1: Pick the shape HA models

- An entity platform when the thing has state a user would see in history or on a dashboard.
- A registered service when it is an action with no state.
- An option on the config entry when it is configuration.

> **Note:** notify is an entity platform because a notifier is addressable; a one-shot "send
> this" with no addressable target is a service.

### Step 2: Wire the entry setup and unload

1. `PLATFORMS` lists the platforms this integration provides, and each name has a module
   beside it — `async_forward_entry_setups` imports `<domain>/<platform>.py` per name.
2. `async_setup_entry` stores state on `entry.runtime_data`, then forwards:
   `await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)`.
3. `async_unload_entry` mirrors it:
   `return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)`, plus
   `await coordinator.async_shutdown()` when the unload succeeds.
4. If setup creates a device, add `async_remove_config_entry_device` so a user can remove it.
5. If the entity carries `_attr_translation_key`, add the matching block to `strings.json`
   and `translations/en.json` — `entity-translations` in `reference/quality-scale.md`.

**Timing:** the audit fails a repo whose `PLATFORMS` names a module that does not exist
(*What the audit checks now* in ha-integration-ci's README), so a half-wired platform is
caught at PR time rather than by a reader remembering this list.

### Step 3: Split the files by responsibility

If `__init__.py` exceeds ~100 lines of logic, extract. `api.py` is the split that matters
most: it decouples device logic from the HA lifecycle, so it is unit-testable without a
running HA instance.

| File | Holds |
|---|---|
| `__init__.py` | `async_setup_entry`, `async_unload_entry`, `async_migrate_entry` only — no business logic |
| `coordinator.py` | `DataUpdateCoordinator` subclass |
| `api.py` | all I/O to the device or service — no HA imports |
| `models.py` | dataclasses and type aliases for device data |
| `entity.py` | shared base entity class when several platforms extend the same base |
| `const.py` | constants only — no imports from other local modules |
| `config_flow.py` | config and options flows |
| `diagnostics.py` | `async_get_config_entry_diagnostics` |
| `services.py` | `async_setup_services(hass)` called from `async_setup` |
| `migration.py` | `async_migrate_entry` logic when it is complex; import into `__init__.py` |
| `helpers.py` / `util.py` | pure functions shared across platforms |
| `<platform>.py` | one per HA platform (`sensor.py`, `button.py`, …) |

### Step 4: Type it, and suppress nothing

The `strict-typing` rule in `reference/quality-scale.md`. Every file passes the pyright run
*Lint & quality check* in `SKILL.md` names, with zero errors, before a PR is ready.

- **Never add `from __future__ import annotations`** — HA's Python floor (the row in
  `reference/freshness.md`) is past the release where PEP 649 made annotation evaluation
  deferred natively, core bans it, and the shipped `pyproject.toml` enforces the ban through
  ruff (`TID251`).
- **Import HA's own types rather than re-typing them** — `DeviceInfo` from
  `homeassistant.helpers.device_registry`, `AddEntitiesCallback` from
  `homeassistant.helpers.entity_platform`, `ConfigType`, `DiscoveryInfoType` and `StateType`
  from `homeassistant.helpers.typing`.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `# type: ignore` to silence a typing error | fix the type | under `strict-typing` a suppression is a violation, not a shortcut | Step 4 |
| `hass.data[DOMAIN][entry.entry_id]`, which is untyped | `entry.runtime_data` on a typed `ConfigEntry` | the alias carries the runtime type, so no cast is needed | *Typed `ConfigEntry` — Step 4* |
| a bare `cast()` on a stubless third-party import | `# type: ignore[import-untyped]`, or contribute stubs | it is the one accepted suppression, and only with the reason beside it | Step 4 |

## Cases

### `config_flow.py` — Step 1

- `class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):` — `domain=` is a keyword
  argument, not a class attribute
- Include `OptionsFlow` when the integration has configurable options
- Implement `async_step_reauth` for expired or invalid auth — `reauthentication-flow` in
  `reference/quality-scale.md`
- Implement `async_step_reconfigure` for changing connection settings —
  `reconfiguration-flow` in `reference/quality-scale.md`
- `vol.Schema` takes one entry per line and is left to `ruff format` — a flow schema is a
  list of entries, not a table, so it does not earn the `# fmt: off` fence under *Alignment
  a human chose meets `ruff format` — Step 2* in `reference/scaffold.md`:
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
```python
# notify.py
from homeassistant.components.notify import NotifyEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .models import MyConfigEntry  # the typed-entry alias, under Step 4 above


class MyNotifyEntity(NotifyEntity):
    """The notify entity for one device."""

    _attr_has_entity_name = True
    _attr_name = "Notify"

    def __init__(self, hass: HomeAssistant, device_id: str) -> None:
        """Bind the entity to its device."""
        self.hass = hass
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_notify"  # per instance, not class scope

    # This is the real signature. NotifyEntity's service schema carries message and
    # title only, so there is no **kwargs and no `data` to read.
    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send the message to the device."""


async def async_setup_entry(
    hass: HomeAssistant, entry: MyConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add one notify entity for the config entry."""
    opts = {**entry.data, **entry.options}
    async_add_entities([MyNotifyEntity(hass, opts[CONF_DEVICE_ID])])
```

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `discovery.async_load_platform` with a `BaseNotificationService` | the `NotifyEntity` above | the legacy pair is deprecated and fails silently rather than erroring | Step 1 |
| a custom payload passed through `NotifyEntity` | a service registered directly, below | `data` is not in its service schema, which carries `message` and `title` only | Step 1 |

**A custom payload — animations, sounds, colours — registered as its own service:**

```python
# notify.py
from collections.abc import Awaitable, Callable

from homeassistant.components.notify.const import (
    ATTR_DATA,
    ATTR_MESSAGE,
    ATTR_TITLE,
    DOMAIN as NOTIFY_DOMAIN,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_DATA): dict,
    }
)


def make_notify_handler(
    hass: HomeAssistant, device_id: str
) -> Callable[[ServiceCall], Awaitable[None]]:
    """Build the service handler bound to one device."""

    async def async_handle(call: ServiceCall) -> None:
        """Push the message, with any extra payload, to the device."""
        data = call.data.get(ATTR_DATA) or {}
        await push_to_device(hass, device_id, call.data[ATTR_MESSAGE], data)

    return async_handle


# __init__.py async_setup_entry:
if not hass.services.has_service(NOTIFY_DOMAIN, device_id):
    hass.services.async_register(
        NOTIFY_DOMAIN,
        device_id,
        make_notify_handler(hass, device_id),
        schema=SERVICE_SCHEMA,
    )
# async_unload_entry:
if hass.services.has_service(NOTIFY_DOMAIN, device_id):
    hass.services.async_remove(NOTIFY_DOMAIN, device_id)
```
This creates `notify.{device_id}` (e.g. `notify.living_room_display`) with full data support.

### Entity platform files — Step 1
- Extend `CoordinatorEntity` (polling) or `Entity` (push)
- Access runtime state via `entry.runtime_data` not `hass.data[DOMAIN][entry.entry_id]`
- Use `DeviceInfo` TypedDict (from `homeassistant.helpers.device_registry`) — not a plain dict:
  ```python
  from homeassistant.helpers.device_registry import DeviceInfo


  @property
  def device_info(self) -> DeviceInfo:
      """The device this entity belongs to."""
      return DeviceInfo(identifiers={(DOMAIN, self._device_id)}, name="My Device")
  ```
- Set `unique_id` on all entities
- **`_attr_has_entity_name = True` is mandatory for new integrations** — entity name identifies only the data point; main feature entity sets `_attr_name = None` so only device name shows
- Set `_attr_translation_key = "my_key"` for translated entity names/states (pairs with `strings.json` `entity` section)
- Use `_attr_entity_category = EntityCategory.DIAGNOSTIC` (read-only info like RSSI) or `EntityCategory.CONFIG` (settings that change device behaviour) for non-primary entities
- Prefer `_attr_*` class/instance attributes over property methods for static values — only use properties for dynamic/state-dependent values
- Implement `_attr_available` to reflect device reachability
- Read state from `self.coordinator.data` only — never do I/O in properties
- Don't pass `update_before_add=True` to `async_add_entities`. It papers over a real gap and schedules a refresh **debouncer timer** that lingers in tests and frozen-clock runs. The gap: `CoordinatorEntity` does **not** push initial state on add, so a push-style entity (one that sets `_attr_native_value` inside `_handle_coordinator_update`) reads `unknown` until the next poll. Fix it properly — either compute `native_value` as a **property** off `self.coordinator.data` (always current), or call `self._handle_coordinator_update()` at the end of `async_added_to_hass` (after `await super().async_added_to_hass()`) to populate from the already-loaded coordinator data. `first_refresh` runs before entities are added, so the data is there.
- **A list/collection sensor's state should be the `len()` count, with the items in an attribute** — not a timestamp or the raw list. (`last_updated`/`last_changed` are already built-in state attributes; don't re-add them.) Add `_attr_state_class = MEASUREMENT` so the count graphs.
- **A `device_class` constrains which `state_class` is legal — verify the pair against the authoritative source, never guess.** HA hard-codes the allowed combinations in `DEVICE_CLASS_STATE_CLASSES` (`homeassistant/components/sensor/const.py`); a disallowed pair logs *"is using state class X which is impossible considering device class Y"* and silently drops long-term statistics. The constraint: `SensorDeviceClass.MONETARY` permits **only `{SensorStateClass.TOTAL}`** — `MEASUREMENT` is invalid for monetary. Don't "fix" an invalid combo by **deleting** `state_class` (that kills LTS entirely, a worse regression than the warning) — switch to a *valid* one. So a fluctuating money **balance** (settle-up debt, account balance) is `device_class=MONETARY` + `state_class=TOTAL`, not `MEASUREMENT`. Before setting any `device_class`/`state_class` pair, check the current mapping at https://raw.githubusercontent.com/home-assistant/core/dev/homeassistant/components/sensor/const.py (or the device-class table at developers.home-assistant.io/docs/core/entity/sensor) — the mapping changes between HA versions. Lock the chosen pair with an attribute test so a future rewrite can't silently drop it.

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
    hass: HomeAssistant, entry: MyConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add one sensor per description."""
    coordinator = entry.runtime_data
    async_add_entities(MySensor(coordinator, desc) for desc in SENSORS)
```

### `UpdateEntity` (firmware/OTA install) — Step 1
- `_attr_in_progress` only **greys out the dashboard install button** — it does **not** stop a programmatic re-entry. A service call, automation, or two near-simultaneous dashboard clicks can still re-enter `async_install` while an install is mid-flight, double-pushing the OTA. Add an **explicit re-entry guard** at the top of `async_install` (after any can't-install checks), windowed so a crashed/timed-out install can't wedge the entity forever:
  ```python
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
  Clear `_installing` when the new version lands (or the same window elapses) in whatever resyncs state from the device manifest. The `in_progress` flag is for the UI; the boolean+timestamp is the actual lock.

### `DataUpdateCoordinator` (polling) — Step 1
- `update_interval` minimum 5 s
- Set `always_update=False` when API responses support `__eq__` — avoids unnecessary state machine writes
- Raise `ConfigEntryAuthFailed` on auth errors inside `_async_update_data`
- Raise `UpdateFailed` on other errors; use `UpdateFailed(retry_after=60)` for rate-limited APIs
- For push APIs: use `coordinator.async_set_updated_data(data)` instead of adapting to polling

### Entity push subscriptions — Step 1
- Subscribe in `async_added_to_hass`, unsubscribe in `async_will_remove_from_hass` — prevents resource leaks
- Never subscribe in `__init__`

### `ConfigEntry` mutation — Step 2
- Never mutate `ConfigEntry` directly — always use `hass.config_entries.async_update_entry(entry, data=..., options=...)`

### Logging — Step 1

Covers the rule `log-when-unavailable` (`reference/quality-scale.md`) and HA's logging conventions.

- **The coordinator already gives you `log-when-unavailable` for free.** When `_async_update_data` raises `UpdateFailed`, `DataUpdateCoordinator` logs the *first* failure at **ERROR**, subsequent consecutive failures at **DEBUG** (no spam), and logs **recovery** automatically. So **do not** wrap the fetch in your own try/log — manual error logging there is double-logging and *fails* the rule. Same for `ConfigEntryNotReady`/`ConfigEntryAuthFailed`: HA logs the reason once; don't also `_LOGGER.exception(...)` in `async_setup_entry` (delete broad `try/except: log; raise` wrappers — they spam and add nothing).
- **Don't log-and-raise.** Raise the right exception and let HA log it: transient → `UpdateFailed`/`ConfigEntryNotReady`; auth → `ConfigEntryAuthFailed`; service/action errors → `HomeAssistantError`/`ServiceValidationError` (the `action-exceptions` rule). Logging *and* raising the same condition is noise.
- **Level discipline:** `INFO` is shown by default → use it almost never. **Setup / unload / teardown lifecycle = `DEBUG`, not `INFO`.** `WARNING` = recoverable thing the user should know; `ERROR` = unexpected, actionable bug (never for expected transient failures — those are exceptions HA handles). `DEBUG` = per-poll / developer detail.
- **Lazy `%` args, never f-strings:** `_LOGGER.debug("added %s", key)` not `f"added {key}"` — ruff `G004` / pylint `logging-fstring-interpolation` enforce. f-string args evaluate even when the level is disabled.
- **Never log secrets** — credentials, API keys, tokens, raw auth responses.
- Logger name (`logging.getLogger(__name__)`) already carries the module path — don't prefix messages with the integration name or "Home Assistant".
- Remove a module-level `_LOGGER` that ends up unused (e.g. after deleting lifecycle spam) — ruff won't flag an unused module global, so it lingers silently.

### Custom services — Step 1
- Register in `async_setup`, not `async_setup_entry` — *Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 2* below says why
- Use `async_register_platform_entity_service()` for entity-targeted actions
- Document in `services.yaml`; add icons in `icons.json`
- A `selector: config_entry` renders a field labelled "Integration" (hardcoded in the HA frontend). To present a device dropdown, use `selector: device` with `integration: {domain}`, then resolve the HA device → config entry in the handler with the helper HA added for exactly this in 2026.9 (read at the `2026.9.0` tag, `homeassistant/helpers/device_registry.py`):
  ```python
  from homeassistant.helpers.device_registry import (
      async_get_device_and_config_entry_for_domain,
  )

  device, entry = async_get_device_and_config_entry_for_domain(
      hass, call.data[ATTR_DEVICE_ID], domain=DOMAIN
  )
  ```
  It returns a pair, either half of which may be `None`. Handle both before using either:

  | Scenario | Choice |
  |---|---|
  | an unknown device id, or a child device | `(None, None)` |
  | a main device no config entry of your domain owns | `(device, None)` |
  | a pre-migration composite device id | a matching split device and its config entry, which is the case a hand-written loop gets wrong |
  | whether that config entry is loaded | not checked — keep your own `ConfigEntryState.LOADED` test |

  Do **not** fetch the device and then loop over `device.config_entries` for your own: that
  property is deprecated, and the loop is what this helper replaces. See *Devices belong to
  one config entry — Step 2* below.
- **Target the entry, or the call fans out.** `hass.services.async_call(DOMAIN, svc, …)` with no target reaches **every** config entry. An entity action that should touch only its own device passes its own `entry_id`/`device_id` and the handler filters on it; leave it untargeted only for a deliberate bulk call.

### `services.yaml` + `strings.json` (hassfest rules) — Step 1
- The modern convention: `services.yaml` carries only field **structure** (selectors, `required`, `default`, collapsible `sections`); names/descriptions live in `strings.json` under a top-level `services` key (`services.{svc}.name/description`, `.fields.{key}.name/description`, `.sections.{key}.name`). Field keys are flat in `strings.json` even when nested in a `sections` block in `services.yaml`. Keep `translations/en.json` a copy of `strings.json`.
- **hassfest forbids literal URLs in `strings.json` descriptions** — `the string should not contain URLs`. Use plain text, or a `{placeholder}` filled via `description_placeholders` in the flow step. A markdown image `![x]({url})` with a placeholder is fine (no literal `http`).
- Collapsible service form: `fields: { appearance: { collapsed: true, fields: {...} } }` — sections are UI-only; the call data stays flat, so the voluptuous schema is unaffected.

### Register integration-global resources in `async_setup`, not `async_setup_entry` — Step 2
The registration happens once per process; doing it per entry races when two entries set up in parallel. Claim the `hass.data` flag **before** the `await`, or both entries pass the check. The panel case, with the code, is `reference/panels.md`.

### Diagnostics platform — Step 1

The `diagnostics` rule in `reference/quality-scale.md`. Add `diagnostics.py`:

```python
from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

TO_REDACT = {CONF_PASSWORD, CONF_API_KEY, "token"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    """Return the entry and its runtime data with secrets redacted."""
    return async_redact_data(
        {"entry": entry.as_dict(), "data": entry.runtime_data}, TO_REDACT
    )
```
No registration needed — HA discovers it automatically from the file name.

### Devices belong to one config entry — Step 2

A device has exactly one config entry and at most one subentry: read `config_entry_id` and
`config_subentry_id`.

| Rule | Value |
|---|---|
| where each release below comes from | the `breaks_in_ha_version` of the call site that reports that usage, read at the `2026.9.0` tag in `homeassistant/helpers/device_registry.py` and `homeassistant/helpers/device.py` |
| a row naming no release | one core attaches none to |
| the WebSocket keys of the same names | `reference/panels.md` |

**A core caller hits these sooner than a custom integration does.** Where a call site sets
`core_behavior=ReportBehavior.ERROR`, core and core integrations raise `RuntimeError` today
while a custom integration gets a logged warning until the release in the row.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `DeviceEntry.config_entries` | `config_entry_id` | a compatibility property returning `{config_entry_id}`, carrying no `report_usage` and **no removal release stated by core** | Step 2 |
| `DeviceEntry.config_entries_subentries` | `config_entry_id` and `config_subentry_id` | a compatibility property returning `{config_entry_id: {config_subentry_id}}`, with **no removal release stated by core** | Step 2 |
| `DeviceEntry.primary_config_entry` | `config_entry_id` | a compatibility property returning `config_entry_id` itself, with **no removal release stated by core** | Step 2 |
| a loop over a device's config entries to find your own | `async_get_device_and_config_entry_for_domain(hass, device_id, domain=DOMAIN)` | the loop gets a pre-migration composite device id wrong, which the helper resolves | *Custom services — Step 1* |
| `DeviceInfo["via_device"]`, `async_get_or_create(via_device=…)` | `via_device_id`, looked up with `async_get_device_id_by_identifier(hass, identifier, config_entry_id=…)` | an identifier is unique only within a config entry; stops working in **2027.8.0** | Step 2 |
| a `via_device` or `via_device_id` naming the device itself | drop the self-reference | ignored and logged now; raises from **2027.8.0** | Step 2 |
| a composite device id passed as `via_device_id` | the id of one real device | resolved and logged now; stops working in **2027.8** | Step 2 |
| `DeviceRegistry.async_get_device()` | `async_get_device_by_identifier()`, `async_get_device_by_connection()` or `async_get_devices()`, each with the config entry id | the lookup is ambiguous once identifiers repeat across entries; stops working in **2027.8.0** | Step 2 |
| `async_update_device(add_config_entry_id=…, add_config_subentry_id=…, remove_config_entry_id=…, remove_config_subentry_id=…)` | `new_config_entry_id`, `new_config_subentry_id`, or `async_remove_device` | a move is no longer an add plus a remove; stops working in **2027.8.0** | Step 2 |
| `async_get_or_create` re-registering an existing device under a different subentry | `async_update_device(new_config_subentry_id=…)` | it silently moves the device; raises from **2027.8.0** | Step 2 |
| a `disabled_by` that contradicts the owning config entry or the parent device | leave it `UNDEFINED` and let the registry derive it | the value is dropped and logged now; raises from **2027.8** | Step 2 |
| `async_update_device(merge_connections=…, merge_identifiers=…)` | `new_connections`, `new_identifiers`, with the full set computed yourself | merging only ever adds; stops working in **2027.9.0** | Step 2 |
| `async_get_or_create(default_manufacturer=…, default_model=…, default_name=…)` | `manufacturer`, `model`, `name` | there is no primary integration left to defer to; stops working in **2027.9.0** | Step 2 |
| `async_get_or_create(created_at=…, modified_at=…)` | drop the arguments | the registry owns both and always ignored them; stops working in **2027.9.0** | Step 2 |
| `suggested_area` on `DeviceEntry`, `async_get_or_create` or `async_update_device` | drop it | it is ignored; **2026.9** on the property and **2026.9.0** on the `async_update_device` call site | Step 2 |
| a non-`str` value in a device-registry string field (`model`, `sw_version`, …) | pass a `str` | coerced with a warning now; stops working in **2026.12.0** | Step 2 |
| `DeviceRegistry.devices` as a mapping — `.get()`, `.values()`, `.keys()`, `registry.devices[id]`, `device_id in registry.devices` | iterate it for the entries, `async_get(device_id)` for a lookup | it is a read-only collection now; the mapping shim stops working in **2027.9.0** | Step 2 |
| `DeviceRegistry.child_devices` as a mapping | iterate it | there is no compatibility shim at all: no `.get()`, no `.values()`, no lookup by id | Step 2 |
| `DeviceRegistry.deleted_devices` | nothing — it is an internal detail of the registry | stops working in **2027.9.0** | Step 2 |
| `DeviceRegistry.async_is_composite_device_id()` | `async_get(device_id, include_composite_devices=False)` returning `None` | the parameter makes the same test; stops working in **2027.9.0** | Step 2 |
| a `DeviceEntry`-only attribute read off a child device — `connections`, `manufacturer`, `model`, `model_id`, `hw_version`, `sw_version`, `serial_number`, `configuration_url`, `entry_type`, `via_device_id` | branch on `parent_device_id`, then read the parent device | the shim hands back the `DeviceEntry` default, not the parent's value; stops working in **2027.9.0** | Step 2 |
| `async_device_info_to_link_from_entity()`, `async_device_info_to_link_from_device_id()` | `entity.device_entry = async_entity_id_to_device(hass, source_entity_id)` | both already return `None`; removed in **2027.8.0** | Step 2 |
| `async_remove_stale_devices_links_keep_entity_device()`, `async_remove_stale_devices_links_keep_current_device()` | `helper_integration.async_remove_helper_devices(…, remove_all_devices=True)` | both already do nothing; removed in **2027.8.0** | Step 2 |

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

### Config entry migration — Step 2

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
**Return `True` or `False`, and log the reason yourself.** A major version bump with no
`async_migrate_entry` fails setup for every existing user, so ship the handler in the same
change. Read at the `2026.9.0` tag, `ConfigEntry.async_migrate` wraps the call in
`except Exception: self.logger.exception(...); return False`, so every exception is
swallowed alike; what replaces that is *Announced for a release after 2026.9 — Step 1* below.

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
    hass: HomeAssistant, entry: MyConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the platform from the typed entry."""
    coordinator = entry.runtime_data  # typed as MyCoordinator, no cast needed
    async_add_entities(MySensor(coordinator, desc) for desc in SENSORS)
```

### MicroPython firmware files — Step 4

Exclude them from Pyright entirely in `pyrightconfig.json`. Keep the `pythonVersion` key:
it is what the audit's version comparison (ha-integration-ci's README) reads from this
file:
```json
{
  "pythonVersion": "3.14",
  "exclude": ["firmware/"],
  "typeCheckingMode": "standard"
}
```

