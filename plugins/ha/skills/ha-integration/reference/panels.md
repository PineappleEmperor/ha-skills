# Integrations that serve a custom panel

Traps specific to shipping a Lit/TS panel from an integration. For how the panel should look, use the `ha-panel-design` skill.

- Register the static path and the panel in `async_setup`
- The bundle must be committed
- `home-assistant-frontend` must be pinned in `requirements.test.txt`
- Registration has two traps
- Home Assistant pads the panel for the safe area
- A panel that reads devices reads them by config entry
- Testability is a design property, not a tooling one

Seven things are non-obvious here, and each fails silently.

### Register the static path and the panel in `async_setup`
Once per process, for the reason `reference/patterns.md` gives under *Register integration-global resources in `async_setup`, not `async_setup_entry`*; the snippet carries both traps the section below names.

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

### The bundle must be committed

HACS ships the repo as-is and runs no build step on the user's machine, so the esbuild output has to live inside `custom_components/<domain>/panel/` to reach the release zip. The `frontend/` templates and the `panel-bundle.yml` caller come from ha-panel-ci's README. **This differs from a Lovelace *card* repo**, which attaches the built `.js` as a release asset — an integration cannot, because the asset isn't in the zip HACS installs.

What users install is always a fresh build — `release.yml` under *Implementation notes* in ha-integration-ci's README says why — and a stale committed bundle draws a warning from the panel check, which ha-panel-ci's README says why it warns rather than fails. It is still worth avoiding: it makes the repo lie about what its source produces, and the symptom is "the fix I made isn't there" when someone reads the committed file. Run `npm run build` and commit the result.

### `home-assistant-frontend` must be pinned in `requirements.test.txt`

A panel declares `frontend` (usually `panel_custom` too) in manifest `dependencies`. The frontend *component* has its own pip requirement that `pip install homeassistant` does **not** pull in — component requirements are installed by HA at runtime. Without the pin every setup test fails in CI with `No module named 'hass_frontend'`, while typically **passing locally** because a dev machine already has the package. Worse, the failures read as `'MockConfigEntry' object has no attribute 'runtime_data'`, pointing at the integration rather than the missing dependency. Pin from **core's own manifest** for your HA version, not from PyPI latest:
```bash
curl -s https://raw.githubusercontent.com/home-assistant/core/<ha-version>/homeassistant/components/frontend/manifest.json
```
Gate-enforced, per *What the audit checks now* in ha-integration-ci's README.

### Registration has two traps
Both are in the snippet above, marked by their comments: claim the registered flag **before** the `await`, or two entries setting up in parallel both register; and cache-bust the module URL with the integration version, or a browser serves the previous panel after an update.

### Home Assistant pads the panel for the safe area

Since **2026.8** custom panels and add-on iframes get safe-area padding by default, so
content stays clear of notches, status bars and home indicators.

**The opt-out is a keyword argument, and it lands in 2026.9.** Read at the `2026.9.0` tag,
`homeassistant/components/panel_custom/__init__.py`: `handle_safe_area: bool = False` is a
parameter of `async_register_panel`, which writes it into `config["_panel_custom"]` itself.
Passing it *inside* the `config` dict does nothing — the function overwrites that key — so a
panel that opts out that way keeps the padding and nobody is told. The YAML spelling
(`handle_safe_area: true` under a `panel_custom:` entry) is the same argument arriving
through `async_setup`, and its per-panel schema is strict, so on 2026.8 that key fails
config validation rather than being ignored.

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

Say which you want explicitly rather than inheriting a default nobody chose: a panel drawn
edge-to-edge on a phone looks broken without the padding, and one that already insets itself
looks doubly inset with it.

### A panel that reads devices reads them by config entry

The device registry WebSocket API changed under the same rewrite `reference/patterns.md`
describes in *Devices belong to one config entry*, and a panel is a client of it:

- **2026.8** — every device in `config/device_registry/list` gains `config_entry_id` and
  `config_subentry_id`. Read those. `config_entries` and `config_entries_subentries` are
  deprecated and removed in **2027.8**; `primary_config_entry` runs to **2027.10**, per the
  comments beside `DeviceEntry.dict_repr`.
- **2026.9** — the list can contain **child devices**, which carry a `parent_device_id` and
  omit *thirteen* fields, not the four a panel is most likely to index: `connections`,
  `manufacturer`, `model`, `model_id`, `sw_version`, `hw_version`, `serial_number`,
  `via_device_id`, `configuration_url`, `entry_type`, and the three deprecated
  `config_entries`, `config_entries_subentries` and `primary_config_entry`. Counted as the
  difference between `DeviceEntry.dict_repr` (25 keys) and `ChildDeviceEntry.dict_repr` (12)
  at the `2026.9.0` tag. A client must not assume any of them is present — including the
  deprecated three, which the bullet above still allows you to read until their removal.
  Rendering a device table that indexes them blindly is how this breaks.
- **2026.9** — `config/device_registry/remove` removes a device by `device_id` alone and
  replaces `config/device_registry/remove_config_entry`, which needed both ids and is
  removed in **2027.9**. Verified by reading `components/config/device_registry.py` at both
  tags: `remove` is absent at `2026.8.0` and registered at `2026.9.0`.
- **2026.8** — `config/device_registry/list_linked_devices` returns siblings sharing
  connections or identifiers across config entries, and
  `config/device_registry/list_composite_splits` maps a pre-migration composite device id to
  the split devices that replaced it. Useful if a panel stored device ids of its own. The
  post assigns these no release; both are registered at the `2026.8.0` tag.

### Testability is a design property, not a tooling one

A panel transforms vendor data
before drawing it, and that logic is reachable from nothing else in the stack: `tsc --noEmit`
proves a helper returns a string, not that it returns the right one; the Python suite cannot
see it; and the bundle-staleness check proves the JS matches its source, not that the source
is correct. So **export the pure presentation helpers** rather than inlining them in
`render()` — a panel that inlines everything has nothing to import, and no test runner fixes
that.

```ts
// panel.ts — exported, so a test can reach them
export function isNamed(item: Pick<Set, "name">): boolean { ... }
export function displayName(item: Pick<Set, "name">): string { ... }   // "{?}" -> "Name tbd"
```

The cases worth testing are the ones where the vendor's data is not what you would draw:
a placeholder standing in for an unannounced name, a missing price, a date that has already
passed, a sort comparator, a unit formatter. ha-panel-ci's `frontend/package.json` ships
`vitest` and a `test` script for this, and its README says where the tests go. The runner
never reaches users: what the release zip holds is *The three workflows* in
ha-integration-ci's README, and `frontend/` is not in it, so it is CI-time weight and
nothing more.

The same reasoning applies to anything the panel sends. A service call built in TypeScript
against a schema declared in Python has no shared definition and no compiler to link them —
`callService` takes `Record<string, unknown>`, so omitting a `vol.Required` field type-checks
cleanly and fails only at runtime, in the browser, where nobody is watching. A test that
captures the outgoing call and asserts its shape is the only thing that catches it.

> **Panel *styling* — sizing, type, colour, spacing — is the `ha-panel-design` skill, not this one.** This section covers only how the TypeScript reaches the user and how the integration registers it.
