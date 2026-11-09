# Config flows and config entries

Read this when writing or changing a config, options, reauth or reconfigure flow, or migrating
a stored config entry.

**A major version bump with no `async_migrate_entry` fails setup for every existing user, so
ship the handler in the same change.**

## Contents

1. Writing the config flow
2. Step 1: Write `config_flow.py`
3. Cases
4. A config flow that will not open — Step 1
5. Config entry migration — Step 1
6. OAuth2 errors at setup — Step 1
7. A sign-in request that keeps coming back — Step 1

## Writing the config flow

### Step 1: Write `config_flow.py`

- `class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):` — `domain=` is a keyword
  argument, not a class attribute
- Include `OptionsFlow` when the integration has configurable options
- Implement `async_step_reauth` for expired or invalid auth — `reauthentication-flow` in
  `reference/quality-scale.md`
- Implement `async_step_reconfigure` for changing connection settings —
  `reconfiguration-flow` in `reference/quality-scale.md`

| Rule | Value |
|---|---|
| the schema library | `import probatio`, then `probatio.Schema`, `probatio.Required`, `probatio.Optional`, as core writes it, with `data_entry_flow.Required` or `data_entry_flow.Optional` only for a field that takes `visible`; the shipped `pyproject.toml` bans `voluptuous` and `import probatio as vol`, as core's does, and `import probatio` sorts after the `homeassistant` imports, since `homeassistant` is third-party there |
| a `probatio.Schema` in a flow | one entry per line, left to `ruff format` |
| a field shown only while another field has a value | `data_entry_flow.Required(CONF_VERIFY_SSL, default=True, visible={"field": CONF_SSL, "value": True})`, after `from homeassistant import data_entry_flow`; a list of conditions must all match; while hidden, the field is not required and its key, default included, is absent from `user_input` — from 2026.11.0, `Required`, `Optional` and `_strip_hidden_fields` in `homeassistant/data_entry_flow.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.10.0` tag |
| the `# fmt: off` fence | not earned here — a flow schema is a list of entries, not a table; *Alignment a human chose meets `ruff format` — Step 1* in `reference/lint.md` |
| a failure a step knows — the credentials refused, the host unreachable | the standard error that names it, `invalid_auth` or `cannot_connect`, with nothing logged; an unexpected exception, where the step catches one, logged with `_LOGGER.exception()` and shown as `unknown`; an error the user sees never mixes translated text with untranslated text — `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |

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
| a config-entry update listener alongside a reloading method | drop the listener and base the options flow on `OptionsFlowWithReload`, which reloads the entry when the options change; or call `async_update_and_abort()` in place of `async_update_reload_and_abort()` and pass `reload_on_update=False` to `_abort_if_unique_id_configured()` | the integration reloads twice or races; an error from **2026.12** | `async_update_reload_and_abort`, `_abort_if_unique_id_configured` and `OptionsFlowWithReload` in `homeassistant/config_entries.py` |
| `FlowHandler.show_advanced_options`, or the `show_advanced_options` key in `FlowHandler.context` | group the extra fields in a schema `section` | the property returns `True` unconditionally and the context key is already gone; removed **2027.6** | `FlowHandler.show_advanced_options` in `homeassistant/data_entry_flow.py` |
| `CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL`, or any other `CONN_CLASS_*` constant of `homeassistant.config_entries` | delete it; how the integration connects is the manifest's `iot_class`, *Step 4: Write `manifest.json`* in `reference/scaffold.md` | core has not read the constants since 2021.6.0; from 2026.11.0 each logs as deprecated, removed in **2027.5.0** | `_DEPRECATED_CONN_CLASS_LOCAL_POLL` and the five `DeprecatedConstant`s beside it in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| `self._set_confirm_only()` in a discovery confirm step | delete the call; the confirm step's own form asks the user | the `confirm_only` flag it set was never read, and from 2026.11.0 it is a deprecated no-op that logs nothing for a custom integration, with no removal release named | `ConfigFlow._set_confirm_only` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.10.0` tag |
| a `scan_interval`, `update_interval` or other polling-frequency field, in a config or options flow | an interval the integration sets itself — *Step 1: Fetch through a `DataUpdateCoordinator`* in `reference/fetching-data.md` | a polling interval is not user-configurable | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| a field asking for the config entry's name | a title the flow sets, which the user can change later in the UI; a `helper` integration may ask | the name is generated, not asked for | `.claude/skills/ha-integration-knowledge/SKILL.md` in core, at the `.0` tag of the release row in `reference/freshness.md` |
| `async_show_form`, `async_show_menu`, `async_show_progress` or `async_external_step` without `step_id`, in a config, options, subentry or repair flow | `step_id=` the name of the step method it is in, without `async_step_` | the flow manager fills in the step it called, which is wrong when one step calls another; logged as deprecated, and the fallback is removed in **2027.5.0** | `_report_missing_step_id` in `homeassistant/data_entry_flow.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| an extra step, or the form shown again after submit, only to show or hide a few fields | a `visible` condition on the field's marker, from 2026.11.0 | one form does it, and a hidden field is neither required nor saved | https://contributors.home-assistant.io/blog/2026/10/21/form-fields-visible/ |
| a hand-written `SelectSelector` of device-class values | `DeviceClassSelector` | it carries HA's own values, so the hand-written translations for them go too | https://contributors.home-assistant.io/blog/2026/09/04/device-and-state-class-selectors/ |
| a `SelectSelector` of units, built from `DEVICE_CLASS_UNITS`, `STATE_CLASS_UNITS` or the previous step's input | `UnitOfMeasurementSelector(UnitOfMeasurementSelectorConfig(device_classes=…, state_classes=…))`, or `context={"filter_device_class": CONF_DEVICE_CLASS, "filter_state_class": CONF_STATE_CLASS}` naming fields of the same form, a context key never beside its own fixed limit; the flow still checks the unit against the classes the user picked, and returns an error, from 2026.11.0 | it takes its units from the sensor unit tables, and the context filters the frontend only | `UnitOfMeasurementSelector` in `homeassistant/helpers/selector.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, the same file at the `2026.10.0` tag |
| core's own text, copied word for word into an `abort` section of `translations/en.json`, `config_subentries` included, for an abort core translates itself — `reauth_successful` or `reconfigure_successful` from `async_update_reload_and_abort` or `async_update_and_abort` called without `reason`, `already_in_progress` from `async_set_unique_id`, `single_instance_allowed`, `no_devices_found` and `cloud_not_connected` from `single_config_entry` and the discovery and webhook flow helpers, an OAuth2 flow's shared reasons | delete it; to word one your own way, keep your text and pass `reason` to the helper, or `translation_domain=DOMAIN` to an OAuth2 flow's `async_abort` | those aborts carry the `homeassistant` translation domain, so the copy is never read | `async_update_reload_and_abort`, `async_update_and_abort`, `async_set_unique_id` and `ConfigEntriesFlowManager.async_init` in `homeassistant/config_entries.py`, `DiscoveryFlowHandler` and `WebhookFlowHandler` in `homeassistant/helpers/config_entry_flow.py`, and `AbstractOAuth2FlowHandler.async_abort` with `_SHARED_ABORT_REASONS` in `homeassistant/helpers/config_entry_oauth2_flow.py`, at the `.0` tag of the release row in `reference/freshness.md` |

## Cases

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

### Config entry migration — Step 1

Implement `async_migrate_entry` in `__init__.py` whenever the stored `entry.data` schema changes:
```python
# In config flow:
class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow; the version pair says which stored entries need migrating."""

    VERSION = 2  # bump for breaking changes (fails setup if no handler)
    MINOR_VERSION = 1  # bump for compatible changes (setup continues without handler)


# In __init__.py:
async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Bring a stored entry up to the current version."""
    if entry.version == 1:
        new_data = {**entry.data, "new_field": "default"}
        hass.config_entries.async_update_entry(
            entry, data=new_data, version=2, minor_version=1
        )
```

What it returns, and the release that return needs, is the return row of *Step 3: Wire the
entry setup and unload* in `reference/patterns.md`.

| Rule | Value |
|---|---|
| where each row was read | `__async_setup_with_context`, `__async_handle_config_entry_setup_error`, `ConfigEntry.async_migrate`, `_async_process_entry_method_result` and `ConfigEntries.async_retry_migration` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md`; the compatibility floor, `ConfigEntry.async_migrate` there at the `2026.9.0` tag; the `False` row's floor, the same file at the `2026.10.0` tag |
| the compatibility floor | 2026.10.0 for raising from a migration, as the rows below do; below it `ConfigEntry.async_migrate` catches any `Exception` and returns `False`, so `ConfigEntryNotReady` ends in `migration_error` too, and `async_retry_migration` does not exist; the example's `None` return has a floor of its own, the compatibility floor of the return row of *Step 3: Wire the entry setup and unload* in `reference/patterns.md` |
| a failure that may clear on its own — a timeout, a device offline | raise `ConfigEntryNotReady`; the migration is retried on the setup schedule |
| any other failure | raise `ConfigEntryError` with a `translation_key`, which the entry shows as its reason; the entry stops in `migration_error`, as it does for any other exception, which is logged with its traceback and leaves no reason |
| returning `False` | from 2026.11.0, a `ConfigEntryError` logged with its traceback, and the entry stops in `migration_error` with the generic reason *Failed to migrate the config entry.*; below it, nothing is logged and the entry has no reason — either way, raise your own `ConfigEntryError` for a reason that says what failed |
| `ConfigEntryAuthFailed` during migration | logged at WARNING and the entry stops in `migration_error`; no reauth flow starts, since reauth expects a migrated entry |
| the way out of `migration_error` | a repair issue whose fix flow calls `await hass.config_entries.async_retry_migration(entry_id)` — https://contributors.home-assistant.io/blog/2026/09/17/use-config-entry-exc-in-migration/ |
| a major version bump with no `async_migrate_entry` | setup fails for every existing user, so ship the handler in the same change |

### OAuth2 errors at setup — Step 1

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
| `_token_request` overridden on a `LocalOAuth2Implementation`, or an `AuthImplementation` from `application_credentials`, to send the client ID and secret in an HTTP Basic header | `token_auth_method = "client_secret_basic"` on the class, from 2026.11.0; the default, `"client_secret_post"`, sends them in the request body | the helper form-encodes both before base64, as RFC 6749 section 2.3.1 requires, and maps a failed request to the exceptions above | `LocalOAuth2Implementation.token_auth_method` and `_token_request` in `homeassistant/helpers/config_entry_oauth2_flow.py`, and `client_auth` in `homeassistant/helpers/oauth2.py`, at the `.0` tag of the release row in `reference/freshness.md`; the floor, `config_entry_oauth2_flow.py` at the `2026.10.0` tag |

### A sign-in request that keeps coming back — Step 1

**Symptom:** the integration asks the user to sign in again after a sign-in that worked, or
after every outage.

| Scenario | Choice |
|---|---|
| where each row was read | `ConfigEntry.async_start_reauth`, `ConfigFlow.async_update_reload_and_abort` and `ConfigFlow.async_update_and_abort` in `homeassistant/config_entries.py`, at the `.0` tag of the release row in `reference/freshness.md` |
| two requests at once | not possible: no second reauth or reconfigure flow starts for an entry while one is open, so a request that returns was raised after the last one finished |
| `ConfigEntryAuthFailed` raised for a timeout, a server error or a rate limit | every outage asks for a sign-in; raise it only when the service refused the credentials — which exception to raise is *Logging — Step 1* in `reference/fetching-data.md` |
| the new credentials kept anywhere but the entry | a reload sets up from `entry.data`, so pass them to `async_update_reload_and_abort` as `data_updates` |
| `async_update_and_abort` in the reauth step | it writes the entry and does not reload it, so the running code keeps the old credentials and fails again; use `async_update_reload_and_abort` |
| a client built once and kept past a reload — at module level, or in `async_setup` | it keeps the old credentials; build it in `async_setup_entry` and keep it on `entry.runtime_data` |
