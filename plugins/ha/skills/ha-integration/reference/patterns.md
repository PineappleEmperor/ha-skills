# Implementation patterns, file structure and typing

The canonical lookup for code inside `custom_components/`: pattern, rule, copyable
snippet. Panel code is `reference/panels.md`; tests are `reference/testing.md`.

- `__init__.py`
- Notify platform (modern pattern — HA 2023.8+)
- `config_flow.py`
- Entity platform files
- `EntityDescription` pattern
- `UpdateEntity` (firmware/OTA install)
- `DataUpdateCoordinator` (polling)
- Entity push subscriptions
- `ConfigEntry` mutation
- Logging
- Custom services
- `services.yaml` + `strings.json` (hassfest rules)
- Register integration-global resources in `async_setup`, not `async_setup_entry`
- Diagnostics platform
- Devices belong to one config entry
- Units: prefer the enumerators
- Config entry migration
- File structure conventions
- Typing
- Do not add `from __future__ import annotations`
- `TYPE_CHECKING` for expensive or circular imports
- Typed `ConfigEntry`
- Avoid `# type: ignore`
- MicroPython firmware files
- HA itself is fully typed
- What changed in recent releases

| Pattern | For |
|---|---|
| `` `__init__.py` `` | entry setup/unload, `runtime_data`, platform forward |
| Notify platform | the modern `NotifyEntity` path, not `BaseNotificationService` |
| `` `config_flow.py` `` | user/reauth/reconfigure steps, unique-id aborts |
| Entity platform files | `CoordinatorEntity`, `DeviceInfo`, naming, availability |
| `` `UpdateEntity` `` | firmware/OTA install |
| `` `DataUpdateCoordinator` `` | polling, backoff, shutdown |
| Entity push subscriptions | subscribe/unsubscribe lifecycle |
| `` `ConfigEntry` `` mutation | options updates without a reload loop |
| Logging | `log-when-unavailable`, HA conventions |
| Custom services | registration, schema, `services.yaml` + `strings.json` |
| Typing | no `from __future__ import annotations`, `TYPE_CHECKING`, typed `ConfigEntry` |

### `__init__.py`

**Pick the shape HA models.** An entity platform when the thing has state a user would see
in history or on a dashboard. A registered service when it is an action with no state. An
option on the config entry when it is configuration. Notify is an entity platform because a
notifier is addressable; a one-shot "send this" with no addressable target is a service.

**Wire it in one change:**

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

The audit fails a repo whose `PLATFORMS` names a module that does not exist
(ha-integration-ci's README, *What the audit checks now*), so the gate catches a half-wired
platform without anyone having to remember this list.

### Notify platform (modern pattern — HA 2023.8+)
```python
# notify.py
from homeassistant.components.notify import NotifyEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .models import MyConfigEntry  # the typed-entry alias, under Typing below


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
⚠️ **Do NOT use** `discovery.async_load_platform` + `BaseNotificationService` — deprecated, silently fails in recent HA versions.
⚠️ `NotifyEntity` only supports `message` and `title` — `data` is **not in its service schema**. If you need custom payload fields (animations, sounds, colours, etc.), register the service directly instead:
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

### `config_flow.py`
- `class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):` — `domain=` is a keyword arg, not a class attribute
- Include `OptionsFlow` (not `OptionsFlowHandler` — that name is deprecated) when the integration has configurable options
- Implement `async_step_reauth` for expired/invalid auth — `reauthentication-flow` in `reference/quality-scale.md`
- Implement `async_step_reconfigure` for changing connection settings — `reconfiguration-flow` in `reference/quality-scale.md`
- **Deprecated since 2026.6, an error from 2026.12: a config-entry update listener together
  with a reloading method.** Having both makes the integration reload twice, or race. Pick
  one: drop the listener and rely on the flow's reloading methods, use
  `async_update_and_abort()` in place of `async_update_reload_and_abort()`, and pass
  `reload_on_update=False` to `_abort_if_unique_id_configured()`.
- `vol.Schema` — one entry per line, left to `ruff format` (the format check collapses
  hand-aligned columns; `# fmt: off` is how a table worth aligning survives it, under *Code
  style* in `reference/scaffold.md` — but a flow schema is a list of entries, not a table,
  so let the formatter have it):
  ```python
  DATA_SCHEMA = vol.Schema(
      {
          vol.Required(CONF_HOST, default="192.168.1.1"): str,
          vol.Required(CONF_PORT, default=8080): int,
      }
  )
  ```

### Entity platform files
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

### `EntityDescription` pattern

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

### `UpdateEntity` (firmware/OTA install)
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

### `DataUpdateCoordinator` (polling)
- `update_interval` minimum 5 s
- Set `always_update=False` when API responses support `__eq__` — avoids unnecessary state machine writes
- Raise `ConfigEntryAuthFailed` on auth errors inside `_async_update_data`
- Raise `UpdateFailed` on other errors; use `UpdateFailed(retry_after=60)` for rate-limited APIs
- For push APIs: use `coordinator.async_set_updated_data(data)` instead of adapting to polling

### Entity push subscriptions
- Subscribe in `async_added_to_hass`, unsubscribe in `async_will_remove_from_hass` — prevents resource leaks
- Never subscribe in `__init__`

### `ConfigEntry` mutation
- Never mutate `ConfigEntry` directly — always use `hass.config_entries.async_update_entry(entry, data=..., options=...)`

### Logging

Covers the rule `log-when-unavailable` (`reference/quality-scale.md`) and HA's logging conventions.

- **The coordinator already gives you `log-when-unavailable` for free.** When `_async_update_data` raises `UpdateFailed`, `DataUpdateCoordinator` logs the *first* failure at **ERROR**, subsequent consecutive failures at **DEBUG** (no spam), and logs **recovery** automatically. So **do not** wrap the fetch in your own try/log — manual error logging there is double-logging and *fails* the rule. Same for `ConfigEntryNotReady`/`ConfigEntryAuthFailed`: HA logs the reason once; don't also `_LOGGER.exception(...)` in `async_setup_entry` (delete broad `try/except: log; raise` wrappers — they spam and add nothing).
- **Don't log-and-raise.** Raise the right exception and let HA log it: transient → `UpdateFailed`/`ConfigEntryNotReady`; auth → `ConfigEntryAuthFailed`; service/action errors → `HomeAssistantError`/`ServiceValidationError` (the `action-exceptions` rule). Logging *and* raising the same condition is noise.
- **Level discipline:** `INFO` is shown by default → use it almost never. **Setup / unload / teardown lifecycle = `DEBUG`, not `INFO`.** `WARNING` = recoverable thing the user should know; `ERROR` = unexpected, actionable bug (never for expected transient failures — those are exceptions HA handles). `DEBUG` = per-poll / developer detail.
- **Lazy `%` args, never f-strings:** `_LOGGER.debug("added %s", key)` not `f"added {key}"` — ruff `G004` / pylint `logging-fstring-interpolation` enforce. f-string args evaluate even when the level is disabled.
- **Never log secrets** — credentials, API keys, tokens, raw auth responses.
- Logger name (`logging.getLogger(__name__)`) already carries the module path — don't prefix messages with the integration name or "Home Assistant".
- Remove a module-level `_LOGGER` that ends up unused (e.g. after deleting lifecycle spam) — ruff won't flag an unused module global, so it lingers silently.

### Custom services
- Register in `async_setup`, not `async_setup_entry` — *Register integration-global resources in `async_setup`, not `async_setup_entry`* below says why
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
  It returns a pair, either half of which may be `None`: `(None, None)` for an unknown id or
  a child device, `(device, None)` when no entry of your domain owns it. Handle both before
  using either. Do **not** fetch the device and then loop over `device.config_entries`
  looking for your own — that property is deprecated, and the loop is what the helper
  replaces. It also resolves a pre-migration composite device id to your domain's split
  device, which is the case a hand-written loop gets wrong. See *Devices belong to one
  config entry* below.
- **Target the entry, or the call fans out.** `hass.services.async_call(DOMAIN, svc, …)` with no target reaches **every** config entry. An entity action that should touch only its own device passes its own `entry_id`/`device_id` and the handler filters on it; leave it untargeted only for a deliberate bulk call.

### `services.yaml` + `strings.json` (hassfest rules)
- The modern convention: `services.yaml` carries only field **structure** (selectors, `required`, `default`, collapsible `sections`); names/descriptions live in `strings.json` under a top-level `services` key (`services.{svc}.name/description`, `.fields.{key}.name/description`, `.sections.{key}.name`). Field keys are flat in `strings.json` even when nested in a `sections` block in `services.yaml`. Keep `translations/en.json` a copy of `strings.json`.
- **hassfest forbids literal URLs in `strings.json` descriptions** — `the string should not contain URLs`. Use plain text, or a `{placeholder}` filled via `description_placeholders` in the flow step. A markdown image `![x]({url})` with a placeholder is fine (no literal `http`).
- Collapsible service form: `fields: { appearance: { collapsed: true, fields: {...} } }` — sections are UI-only; the call data stays flat, so the voluptuous schema is unaffected.

### Register integration-global resources in `async_setup`, not `async_setup_entry`
The registration happens once per process; doing it per entry races when two entries set up in parallel. Claim the `hass.data` flag **before** the `await`, or both entries pass the check. The panel case, with the code, is `reference/panels.md`.

### Diagnostics platform

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

### Devices belong to one config entry

Rewritten in 2026.8: a device has exactly one config entry and at most one subentry.
**The deadlines differ by row, so read the last column rather than the section.**

| Deprecated | Use instead | Stops working |
|---|---|---|
| `DeviceEntry.config_entries` | `config_entry_id` | **2027.10** for a custom integration |
| `DeviceEntry.config_entries_subentries` | `config_entry_id` and `config_subentry_id` | **2027.10** for a custom integration |
| `DeviceEntry.primary_config_entry` | `config_entry_id` | **2027.10** for a custom integration |
| `DeviceInfo["via_device"]`, `async_get_or_create(via_device=…)` | `via_device_id` | **2027.8** |
| `DeviceRegistry.async_get_device()` | `async_get_device_by_identifier()` / `async_get_device_by_connection()`, with the config entry id | **2027.8** |
| `async_update_device(add_config_entry_id=…, remove_config_entry_id=…)` and the subentry pair | `new_config_entry_id`, `new_config_subentry_id` | **2027.8** |

The three plural properties are the ones with the longer runway, and only for a custom
integration: from **2026.10** a core caller reading one gets a `RuntimeError` immediately,
while a custom integration keeps working with a logged warning until 2027.10. Everything
else in the table warns until 2027.8. A deadline is not a reprieve either way.

Looping over a device's entries to find your own is the pattern this replaces: call
`async_get_device_and_config_entry_for_domain(hass, device_id, domain=DOMAIN)` instead, as
*Custom services* above shows. Helper-integration methods
(`async_device_info_to_link_from_entity`, `async_device_info_to_link_from_device_id`) now
return `None` and are removed in 2027.8 — set `self.device_entry` instead.

### Units: prefer the enumerators

Two enums arrived in **2026.7** and the loose constants they replace are deprecated, with no
removal release announced:

- `UnitOfDensity` for mass-over-volume — `g/m³`, `mg/m³`, `µg/m³`, `µg/ft³`
- `UnitOfRatio` for unitless ratios — `ppm`, `ppb`

The `CONCENTRATION_*` constants are deprecated (`CONCENTRATION_PARTS_PER_CUBIC_METER` with
no replacement at all), and **`PERCENTAGE` is deprecated specifically as a unit of
measurement** even though the constant itself stays. A humidity or battery sensor should
take its unit from the enum rather than the bare string.

### Config entry migration

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
Major version bump without `async_migrate_entry` = setup **fails** for existing users. Always implement the handler before shipping a major bump.

**Raise, rather than returning `False`.** Returning `False` tells the user nothing. The
handler may raise a config-entry exception instead, which is translatable and carries the
reason: `ConfigEntryNotReady` for something that may resolve itself (a timeout, a service
briefly down) leaves the entry to retry later; any other exception, `ConfigEntryError`
included, stops migration and parks the entry in `migration_error`, which is not recoverable
on its own. For that second case, raise a repair issue so the user knows what to fix, and
call `hass.config_entries.async_retry_migration(entry_id)` once they have.

---

### File structure conventions

Split files by responsibility. Rule of thumb: if `__init__.py` exceeds ~100 lines of logic, extract.

| File | Purpose |
|------|---------|
| `__init__.py` | `async_setup_entry`, `async_unload_entry`, `async_migrate_entry` only — no business logic |
| `coordinator.py` | `DataUpdateCoordinator` subclass |
| `api.py` | All I/O to the device/service — no HA imports; makes it independently testable |
| `models.py` | Dataclasses and type aliases for device data |
| `entity.py` | Shared base entity class when multiple platforms extend the same base |
| `const.py` | Constants only — no imports from other local modules |
| `config_flow.py` | Config + options flows |
| `diagnostics.py` | `async_get_config_entry_diagnostics` |
| `services.py` | `async_setup_services(hass)` called from `async_setup`; keeps `__init__.py` clean |
| `migration.py` | `async_migrate_entry` logic if complex; import into `__init__.py` |
| `helpers.py` / `util.py` | Pure functions shared across platforms |
| `<platform>.py` | One per HA platform (`sensor.py`, `button.py`, etc.) |

`api.py` is the most important split — it decouples device logic from HA lifecycle and makes unit testing possible without a running HA instance.

---

### Typing

Complete, correct typing is the `strict-typing` rule in `reference/quality-scale.md` — not cosmetic. It catches contract violations between platforms, coordinator data shapes, and config entry contents at development time rather than runtime. Every file must pass the pyright run *Lint & quality check* in `SKILL.md` names, with zero errors, before a PR is ready. Suppressions are failures, not fixes.

### Do not add `from __future__ import annotations`

HA's Python floor (the row in `reference/freshness.md`) is past the release where PEP 649
made annotation evaluation deferred natively, so forward references and
`TYPE_CHECKING`-only imports work without it. The import only switches Python
back to the older stringified behaviour, which some runtime tooling handles worse. Core bans
it, and the shipped `pyproject.toml` enforces the ban through ruff (`TID251`).

### `TYPE_CHECKING` for expensive or circular imports
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def uses_hass_in_annotations_only(hass: HomeAssistant) -> None:
    """The import never runs; deferred annotations resolve the name when asked."""
```

### Typed `ConfigEntry`

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

### Avoid `# type: ignore`

Under `strict-typing` a type suppression is a violation, not a shortcut. The common HA patterns that tempt one all have proper solutions:
- `hass.data[DOMAIN]` is untyped → don't use it; use `entry.runtime_data` with typed `ConfigEntry` instead
- `entry.runtime_data` assignment errors → solved by the typed `ConfigEntry` alias above
- Third-party library missing stubs → contribute stubs or use `cast()` with a comment explaining why

Only acceptable suppression: `# type: ignore[import-untyped]` on a third-party import with no available stubs, where contributing stubs is out of scope.

### MicroPython firmware files

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

### HA itself is fully typed

Import its types directly rather than re-typing them:
```python
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
```

---

### What changed in recent releases

The window this skill is current for is the release row in `reference/freshness.md`, and the
procedure beside it is what extends this table. **Every row below was written from a source
opened and read** — the change and its removal release from the developer-blog post, and,
where the post names no landing release, from the release notes that link it, which is why
some rows carry a release the post itself does not state. A row whose release neither
source gives says so in the last column rather than guessing. Rows beyond the captured
release are here because the post announcing them landed inside the window; they are a
warning, not a claim that the skill has been checked against that release.

| Release | Change | What to do | Gone in |
|---|---|---|---|
| 2026.6 | config-entry update listener together with a reloading method | drop one: `async_update_and_abort()` over `async_update_reload_and_abort()`, `reload_on_update=False` on `_abort_if_unique_id_configured()` | an **error from 2026.12** |
| 2026.7 | `UnitOfDensity`, `UnitOfRatio` | replace the `CONCENTRATION_*` constants; stop using `PERCENTAGE` *as a unit of measurement* | no removal release announced |
| 2026.8 | a device has one config entry and at most one subentry | see *Devices belong to one config entry* above | warnings until **2027.8**; helper methods removed then |
| 2026.8 | custom panels get safe-area padding by default | the opt-out lands a release later — `reference/panels.md` | — |
| 2026.9 | `async_get_device_and_config_entry_for_domain()` in `helpers.device_registry` | use it in place of a loop over a device's entries; it handles composite device ids too | — |
| 2026.9 | `panel_custom` gains the `handle_safe_area` opt-out | `handle_safe_area=True` to `async_register_panel`, or the key under a `panel_custom:` entry — `reference/panels.md` | — |
| 2026.10 | the plural device accessors are enforced | `config_entry_id` — and see the per-row deadlines in *Devices belong to one config entry* above, which are not all the same | core raises now; a **custom integration warns until 2027.10** |
| 2026.6 | `FlowHandler.show_advanced_options`, and the `show_advanced_options` key in `FlowHandler.context` | group the extra fields in a schema `section` instead; the property returns `True` unconditionally meanwhile and the context key is already gone | removed **2027.6** |
| 2026.6 | MQTT `publish()` / `async_publish()` take `qos: int = 0` and `retain: bool = False` | stop passing `None`; take the defaults or pass typed values | `None` stops working **2027.6** |
| 2026.8 | device registry WebSocket gains `config_entry_id` and `config_subentry_id` | a panel reads those, not the plural fields — `reference/panels.md` | plural fields removed **2027.8** |
| 2026.8 | `config/device_registry/list_linked_devices` and `list_composite_splits` | new WebSocket commands, read at the `2026.8.0` tag; the post assigns them no release | — |
| 2026.9 | child devices in the device list; `config/device_registry/remove` | handle entries with a `parent_device_id` and missing hardware fields; call the new remove command | `remove_config_entry` removed **2027.9** |
| — | `DeviceClassSelector` and `StateClassSelector` | migrate a flow that picks a device or state class off `SelectSelector`, and drop the stale translations for its values | no version or deprecation stated in the post |
| — | `async_migrate_entry` may raise instead of returning `False` | `ConfigEntryNotReady` to retry later; anything else halts at `migration_error`, so pair it with a repair issue and `async_retry_migration()` | no version stated in the post |
| 2026.6 | conditions and scripts are objects with a lifecycle | `async_condition_from_config()`, then `async_check()`, then `async_unload()`; a script is `async_run()` then `await script.async_unload()`. A condition platform may add `_async_setup()` / `_async_unload()` | calling a condition object directly ends **2027.1** |
| 2026.6 | `BrowseMediaSource(domain=…)` is required | pass your own domain; the all-sources root node is `RootBrowseMediaSource` | a hard change, not a deprecation |
| 2026.7 | `device_tracker`: `battery_level` and `TrackerEntity.location_name` | a dedicated battery sensor; `in_zones` (zone entity ids, smallest first) for location. New: `BaseScannerEntity`, the `tracking_type` attribute | both stop working **2027.7** |
| 2026.7 | `async_initialize_triggers(home_assistant_start=…)` | stop passing it — it already has no effect; `hass.async_add_startup_job` for startup work | removed **2027.8** |
| 2026.8 | `MediaSource.async_search_media()` | optional; adds search to the media browser via `SearchMedia` / `SearchMediaQuery` | — |
| 2026.8 | `ButtonEventType` for `EventDeviceClass.BUTTON` | optional and additive: use the standard members (`PRESS_START`, `LONG_PRESS_START`, `MULTI_PRESS_END`, …) in `event_types` rather than your own strings | custom strings still allowed |
| 2026.9 | the `configurator` integration | a config flow and config entries | removed **2027.10** |
| 2026.9 | `battery_level` on the base vacuum entity (`StateVacuumEntity`) | a dedicated battery sensor | **removed** — from the release notes' *Backward-incompatible changes*, which carry no blog post for it |
| 2026.6 | MQTT publish supports `message_expiry_interval` | optional; a second post of the same date as the `qos`/`retain` change | — |
| 2026.10 | the OAuth2 helper raises config-entry exceptions itself | delete the try/except around `ImplementationUnavailableError`, `UnknownImplementationError` and the token-request errors, the hand-rolled `ConfigEntryNotReady`/`ConfigEntryAuthFailed` conversion, and the `oauth2_implementation_unavailable` string | — |
| 2026.10 | `modbus.get_hub` | `async_get_unit(hass, entry, connection_params, unit_id)`, with the connection collected in your own config flow | removed **2027.10** |
| 2026.10 | `lawn_mower`: `LawnMowerEntityFeature.STOP`, `LawnMowerActivity.IDLE` | implement `async_stop`; a mower stopped but neither docked nor paused is `IDLE`, not `PAUSED` or `ERROR` | — |

**`battery_level` is going away platform by platform.** `device_tracker`'s deprecates in
2026.7 and stops working in 2027.7; `vacuum`'s is already removed. If a platform you
implement exposes a battery as an entity property, assume it is on the same path and expose
a `SensorDeviceClass.BATTERY` sensor instead.

---

Testing — the harness prerequisites and what to mock — is `reference/testing.md`.
