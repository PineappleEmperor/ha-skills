# Integrations that serve a custom panel

Traps specific to shipping a Lit/TS panel from an integration. For how the panel should look, use the `ha-panel-design` skill.

- Register the static path and the panel in `async_setup`
- The bundle must be committed
- `home-assistant-frontend` must be pinned in `requirements.test.txt`
- Registration has two traps
- Testability is a design property, not a tooling one

Five things are non-obvious here, and each fails silently.

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

What users install is always a fresh build — ha-integration-ci's README says why under `release.yml` — and a stale committed bundle draws a warning from the panel check, which ha-panel-ci's README says why it warns rather than fails. It is still worth avoiding: it makes the repo lie about what its source produces, and the symptom is "the fix I made isn't there" when someone reads the committed file. Run `npm run build` and commit the result.

### `home-assistant-frontend` must be pinned in `requirements.test.txt`

A panel declares `frontend` (usually `panel_custom` too) in manifest `dependencies`. The frontend *component* has its own pip requirement that `pip install homeassistant` does **not** pull in — component requirements are installed by HA at runtime. Without the pin every setup test fails in CI with `No module named 'hass_frontend'`, while typically **passing locally** because a dev machine already has the package. Worse, the failures read as `'MockConfigEntry' object has no attribute 'runtime_data'`, pointing at the integration rather than the missing dependency. Pin from **core's own manifest** for your HA version, not from PyPI latest:
```bash
curl -s https://raw.githubusercontent.com/home-assistant/core/<ha-version>/homeassistant/components/frontend/manifest.json
```
Gate-enforced: a manifest depending on `frontend`/`panel_custom` with no pin fails the audit.

### Registration has two traps
Both are in the snippet above, marked by their comments: claim the registered flag **before** the `await`, or two entries setting up in parallel both register; and cache-bust the module URL with the integration version, or a browser serves the previous panel after an update.

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
never reaches users: the release zip holds `custom_components/<domain>/` only, so
`frontend/` is CI-time weight and nothing more.

The same reasoning applies to anything the panel sends. A service call built in TypeScript
against a schema declared in Python has no shared definition and no compiler to link them —
`callService` takes `Record<string, unknown>`, so omitting a `vol.Required` field type-checks
cleanly and fails only at runtime, in the browser, where nobody is watching. A test that
captures the outgoing call and asserts its shape is the only thing that catches it.

> **Panel *styling* — sizing, type, colour, spacing — is the `ha-panel-design` skill, not this one.** This section covers only how the TypeScript reaches the user and how the integration registers it.
