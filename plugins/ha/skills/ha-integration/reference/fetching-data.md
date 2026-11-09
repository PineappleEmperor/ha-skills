# Fetching data, connections and logging

Read this when writing or changing how the integration fetches its data — polling, push, a
dropped connection, an unexpected reply, a blocking call — or what it logs.

**Raise `UpdateFailed` and let the coordinator log, rather than wrapping the fetch in your own
`try`/log.**

## Contents

1. Fetching data
2. Step 1: Fetch through a `DataUpdateCoordinator`
3. Cases
4. Entity push subscriptions — Step 1
5. A connection that drops — Step 1
6. A reply the code does not expect — Step 1
7. A blocking call inside the event loop — Step 1
8. Logging — Step 1

## Fetching data

### Step 1: Fetch through a `DataUpdateCoordinator`
- `update_interval` no shorter than the time the source's data takes to change — the `appropriate-polling` rule, https://contributors.home-assistant.io/core/quality-scale/appropriate-polling/; core sets no minimum
- Set `always_update=False` when API responses support `__eq__` — avoids unnecessary state machine writes
- Raise `ConfigEntryAuthFailed` on auth errors inside `_async_update_data`
- Raise `UpdateFailed` on other errors; use `UpdateFailed(retry_after=60)` for rate-limited APIs — on a later poll it sets the wait before the next poll once
- From 2026.11.0, the `retry_after` of an `UpdateFailed` raised in the first refresh becomes the `retry_after` of the `ConfigEntryNotReady` that `async_config_entry_first_refresh` raises — `_async_config_entry_first_refresh` in `homeassistant/helpers/update_coordinator.py`, at the `.0` tag of the release row in `reference/freshness.md`; the setup retry wait it gives is *A connection that drops — Step 1*
- For push APIs: use `coordinator.async_set_updated_data(data)` instead of adapting to polling

## Cases

### Entity push subscriptions — Step 1
- Subscribe in `async_added_to_hass`, and hand the unsubscribe to `self.async_on_remove` — why is the `async_prepare_to_add_to_hass` row of *Step 1: Write the entity platform files* in `reference/entities.md`
- A subscription keyed on the entity's own `entity_id`: the `async_entity_id_changed` rows of *Step 1: Write the entity platform files* in `reference/entities.md`
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
| a `ConfigEntryNotReady(retry_after=…)`, from 2026.11.0 | the retry waits the longer of that backoff and `retry_after`, which is capped at `SETUP_RETRY_AFTER_MAX_WAIT`, 86400 seconds — `ConfigEntry.async_setup`, through `__async_handle_config_entry_setup_error` |
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

**Fix:** parse the reply where *Step 1: Lay out the files by responsibility* in
`reference/patterns.md` puts the I/O, into fields that may be absent.

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
| where each row was read | the `entity-unavailable` and `dynamic-devices` rules; `_async_refresh` and `async_update_listeners` in `homeassistant/helpers/update_coordinator.py` and `SensorEntity.state` in `homeassistant/components/sensor/entity.py`, at the `.0` tag of the release row in `reference/freshness.md` |
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
