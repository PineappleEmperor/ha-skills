# Integrations that serve a custom panel

Read this when building or fixing an integration that ships a Lit/TS panel. How the panel
should *look* — type scale, colour, spacing, touch targets — is the `ha-panel-design` skill.

**Verify each step by hand: what CI reports is a warning at most, and the browser reports
nothing at all.**

## Contents

1. Shipping a panel from an integration
2. Step 1: Build the bundle and commit it
3. Step 2: Pin `home-assistant-frontend` in `requirements.test.txt`
4. Step 3: Register the static path and the panel in `async_setup`
5. Step 4: Say whether the panel handles the safe area
6. Step 5: Export the presentation helpers so a test can reach them
7. Cases
8. A panel that reads devices reads them by config entry — Step 3

## Shipping a panel from an integration

### Step 1: Build the bundle and commit it

Run `npm run build` and commit the output into `custom_components/<domain>/panel/`. HACS
ships the repo as-is and runs no build step on the user's machine, so the esbuild output has
to be inside the package to reach the release zip. The `frontend/` templates and the
`panel-bundle.yml` caller come from ha-panel-ci's README.

> **Note:** a Lovelace *card* repo attaches the built `.js` as a release asset instead. An
> integration cannot: the asset is not in the zip HACS installs.

**Symptom:** a stale committed bundle warns rather than fails the panel check, and reads as
"the fix I made isn't there" to whoever opens the committed file.

> **Note:** what users install is always a fresh build — `release.yml` under *Implementation
> notes* in ha-integration-ci's README rebuilds the bundle before packing the zip.

### Step 2: Pin `home-assistant-frontend` in `requirements.test.txt`

Take the pin from core's own manifest for your HA version, never from PyPI latest:

```bash
curl -s https://raw.githubusercontent.com/home-assistant/core/<ha-version>/homeassistant/components/frontend/manifest.json
```

A panel declares `frontend` (usually `panel_custom` too) in manifest `dependencies`, and the
frontend *component* has its own pip requirement that `pip install homeassistant` does not
pull in — component requirements are installed by HA at runtime. Gate-enforced, per *What
the audit checks now* in ha-integration-ci's README.

**Symptom:** every setup test fails in CI with `No module named 'hass_frontend'`, surfacing
as `'MockConfigEntry' object has no attribute 'runtime_data'`.

### Step 3: Register the static path and the panel in `async_setup`

Once per process, for the reason `reference/patterns.md` gives under *Register
integration-global resources in `async_setup`, not `async_setup_entry` — Step 2*.

| Rule | Value |
|---|---|
| claim the registered flag in `hass.data` | before the `await`, or two entries setting up in parallel both register |
| cache-bust the module URL with the integration version | otherwise a browser serves the previous panel after an update |

Both traps are marked by their comments in the snippet:

  ```python
  from pathlib import Path

  from homeassistant.components import frontend, panel_custom
  from homeassistant.components.http import StaticPathConfig
  from homeassistant.core import HomeAssistant
  from homeassistant.helpers.typing import ConfigType
  from homeassistant.loader import async_get_integration

  from .const import DOMAIN


  async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
      """Serve the panel bundle; registration itself is option-gated below."""
      await hass.http.async_register_static_paths(
          [
              StaticPathConfig(
                  f"/{DOMAIN}_panel/editor.js",
                  str(Path(__file__).parent / "panel" / "editor.js"),
                  False,
              )
          ]
      )
      return True


  async def _refresh_panel(hass: HomeAssistant) -> None:  # from async_setup_entry
      if _panel_wanted(hass) and not hass.data.get(f"{DOMAIN}_panel"):
          hass.data[f"{DOMAIN}_panel"] = True  # claim BEFORE the await: setups race
          integration = await async_get_integration(hass, DOMAIN)
          await panel_custom.async_register_panel(
              hass,
              frontend_url_path=DOMAIN,
              webcomponent_name=f"{DOMAIN}-panel",
              module_url=f"/{DOMAIN}_panel/editor.js?v={integration.version}",  # else cached
              sidebar_title="...",
              sidebar_icon="mdi:view-grid",
              require_admin=True,
          )


  # last unload: frontend.async_remove_panel(hass, DOMAIN)
  ```

### Step 4: Say whether the panel handles the safe area

Custom panels and add-on iframes get safe-area padding by default, so content stays clear of
notches, status bars and home indicators. Set the parameter either way rather than taking
the default: a panel drawn edge-to-edge looks broken without the padding, and one that
insets itself looks doubly inset with it.

| Rule | Value |
|---|---|
| what it is | `handle_safe_area: bool = False`, a parameter of `panel_custom.async_register_panel`, which writes it into `config["_panel_custom"]` itself |
| the YAML spelling | `handle_safe_area: true` under a `panel_custom:` entry — the same argument arriving through `async_setup` |
| the compatibility floor | **2026.8.2** — absent from `homeassistant/components/panel_custom/__init__.py` at the `2026.8.0` and `2026.8.1` tags, present at `2026.8.2`, and read at `2026.9.0` for the behaviour described here |
| an iframe-based panel | gets the resolved insets forwarded in as the `--safe-area-inset-top`/`-right`/`-bottom`/`-left` CSS variables instead |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `handle_safe_area` inside the `config` dict passed to `async_register_panel` | the keyword argument | the function overwrites `config["_panel_custom"]`, so the panel keeps the padding and nobody is told | Step 4 |
| `handle_safe_area:` under a `panel_custom:` entry on 2026.8.0 or 2026.8.1 | upgrade first | the per-panel schema rejects an unknown key, so the entry fails config validation rather than being ignored | Step 4 |

```python
async def _register(hass: HomeAssistant, module_url: str) -> None:
    """Register the panel, taking responsibility for the safe-area insets."""
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=DOMAIN,
        webcomponent_name=f"{DOMAIN}-panel",
        module_url=module_url,
        handle_safe_area=True,  # this panel insets itself; skip HA's padding
    )
```

### Step 5: Export the presentation helpers so a test can reach them

**Export the pure presentation helpers** rather than inlining them in `render()`; a panel
that inlines everything has nothing for a test to import.

```ts
// panel.ts — exported, so a test can reach them
export function isNamed(item: Pick<Set, "name">): boolean { ... }
export function displayName(item: Pick<Set, "name">): string { ... }   // "{?}" -> "Name tbd"
```

**What is worth testing** — the cases where the vendor's data is not what you would draw:

- A placeholder standing in for an unannounced name.
- A missing price.
- A date that has already passed.
- A sort comparator.
- A unit formatter.
- The outgoing service call, captured and asserted on its shape.

| Rule | Value |
|---|---|
| the runner | ha-panel-ci's `frontend/package.json` ships `vitest` and a `test` script; its README says where the tests go |
| what it costs users | nothing — `frontend/` is not in the release zip (*The three workflows* in ha-integration-ci's README), so it is CI-time weight only |
| `callService` | takes `Record<string, unknown>`, so omitting a `vol.Required` field type-checks cleanly and fails at runtime in the browser |

## Cases

### A panel that reads devices reads them by config entry — Step 3

A panel is a client of the device registry WebSocket API, which changed under the same
rewrite `reference/patterns.md` describes in *Devices belong to one config entry — Step 2*.
Read at the `2026.9.0` tag, `homeassistant/helpers/device_registry.py` and
`homeassistant/components/config/device_registry.py`.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| reading `config_entries` or `config_entries_subentries` off a device in `config/device_registry/list` | `config_entry_id` and `config_subentry_id` | both are derived from the single entry, and the comment beside `DeviceEntry.dict_repr` says they **can be removed in 2027.8** | Step 3 |
| reading `primary_config_entry` | `config_entry_id` | it is that same value, and **core states no removal release for it** | Step 3 |
| indexing a device's hardware fields without first checking what kind of entry it is | branch on `parent_device_id`, which is present and non-null only on a child device | a child device carries 12 of the 25 keys `DeviceEntry.dict_repr` has, and a table that indexes the rest blindly breaks | Step 3 |
| `config/device_registry/remove_config_entry`, which needs both ids | `config/device_registry/remove`, with `device_id` alone | the old command logs a warning naming its own removal in **2027.9** | Step 3 |

**The thirteen keys a child device omits:** `config_entries`, `config_entries_subentries`,
`configuration_url`, `connections`, `entry_type`, `hw_version`, `manufacturer`, `model`,
`model_id`, `primary_config_entry`, `serial_number`, `sw_version`, `via_device_id`.

**Two commands for a panel that stored device ids of its own**, both registered at the
`2026.9.0` tag with no removal release stated:

- `config/device_registry/list_linked_devices` — the siblings sharing a connection or
  identifier with a device, across config entries.
- `config/device_registry/list_composite_splits` — every pre-migration composite device id,
  mapped to the split devices that replaced it.
