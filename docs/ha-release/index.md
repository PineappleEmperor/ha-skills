# The sources for Home Assistant 2026.6, 2026.7, 2026.8, 2026.9

Fetched by `scripts/fetch_ha_sources.py`, last on 2026-09-19. Every file below
is a **secondary** source: it says what changed and why, and never how an API is
spelled — core at the release tag says that, and the paragraph beginning *A post is
not the source of record* under *When the release row goes red* in
`plugins/ha/skills/ha-integration/reference/freshness.md` says why.

The governance gate refuses a patch to a file under
`plugins/ha/skills/ha-integration/reference/` that names one of the releases below
until it has served that release's own files. Any release with no non-empty folder
here is not demanded, because nothing here could settle it — one older than the
oldest fetched, a gap inside the span, or a removal release a year out. The single
exception is the minor immediately after the newest below: that is the one a pass is
about to write about, so an absent folder there means the fetch was skipped, and the
gate says so. This list is what "open every source" means in practice; re-run the
script to add a release.

**The window is a net, not a claim.** Posts are gathered by publication date, between
one release and the next, and a post published in the days before a release usually
describes the release *after* it — the beta was cut a week earlier. The 2026.9 window
caught a configurator-deprecation post dated two days before 2026.9 shipped, and
`configurator/__init__.py` at the `2026.9.0` tag carries no deprecation at all. Which
release a change is actually in is core's to answer, never the post's. The net has a
hole of its own at the far end: the developer blog's feed carries a fixed number of
entries, so a backfill reaching further back than the feed does collects only the
posts still in it.

Each file opens with its own source URL and the terms the host publishes it under,
and the `sha256` below is the first twelve characters of that file's hash — the
suite compares them, so a source emptied or altered in place stops matching the line
that says what it is.

| Source | sha256 | What it is |
|---|---|---|
| `docs/ha-release/2026.6/release-notes.md` | `0f5687745bbf` | [2026.6: Pick a card, any card](https://www.home-assistant.io/blog/2026/06/03/release-20266/) |
| `docs/ha-release/2026.6/blog-2026-05-07-config-entry-listener-together-with-reloading-methods.md` | `6cbbaa4a84b3` | [Deprecating config entry listener with reloading methods in config flow](https://developers.home-assistant.io/blog/2026/05/07/config-entry-listener-together-with-reloading-methods) |
| `docs/ha-release/2026.6/blog-2026-05-11-format-entity-name-helper.md` | `b527aa563056` | [Format entity names in custom cards](https://developers.home-assistant.io/blog/2026/05/11/format-entity-name-helper) |
| `docs/ha-release/2026.6/blog-2026-05-11-mqtt-publish-api-changes.md` | `f9b4a78988bd` | [MQTT publish API changes](https://developers.home-assistant.io/blog/2026/05/11/mqtt-publish-api-changes) |
| `docs/ha-release/2026.6/blog-2026-05-11-mqtt-publish-api-message-expiry-interval.md` | `306fad8a0c13` | [MQTT publish API supports message expiry interval](https://developers.home-assistant.io/blog/2026/05/11/mqtt-publish-api-message-expiry-interval) |
| `docs/ha-release/2026.6/blog-2026-05-13-condition-script-api-changes.md` | `efb022f7fa1c` | [Changes to the condition and script APIs](https://developers.home-assistant.io/blog/2026/05/13/condition-script-api-changes) |
| `docs/ha-release/2026.6/blog-2026-05-20-browse-media-source-root-class.md` | `7cc95438736f` | [BrowseMediaSource: domain is now required](https://developers.home-assistant.io/blog/2026/05/20/browse-media-source-root-class) |
| `docs/ha-release/2026.6/blog-2026-05-26-advanced-mode-config-flow-deprecation.md` | `b3795caee354` | [Deprecation of advanced mode in data entry flow](https://developers.home-assistant.io/blog/2026/05/26/advanced-mode-config-flow-deprecation) |
| `docs/ha-release/2026.6/blog-2026-05-27-custom-card-suggestions.md` | `ffabb3e52e24` | [Custom card suggestions in the card picker](https://developers.home-assistant.io/blog/2026/05/27/custom-card-suggestions) |
| `docs/ha-release/2026.6/blog-2026-05-27-frontend-component-updates-2026-6.md` | `ebc52da48128` | [Frontend component updates in 2026.6](https://developers.home-assistant.io/blog/2026/05/27/frontend-component-updates-2026.6) |
| `docs/ha-release/2026.7/release-notes.md` | `9f63ca58eac4` | [2026.7: Automations that speak your language](https://www.home-assistant.io/blog/2026/07/01/release-20267/) |
| `docs/ha-release/2026.7/blog-2026-06-15-device-tracker-changes.md` | `c7d0f895311a` | [Changes to device tracker entity models](https://developers.home-assistant.io/blog/2026/06/15/device-tracker-changes) |
| `docs/ha-release/2026.7/blog-2026-06-23-frontend-component-updates-2026-7.md` | `8392e7354312` | [Frontend component updates in 2026.7](https://developers.home-assistant.io/blog/2026/06/23/frontend-component-updates-2026.7) |
| `docs/ha-release/2026.7/blog-2026-06-30-async-initialize-triggers-home-assistant-start-deprecated.md` | `f4d774a799a6` | [Deprecation of the home_assistant_start flag of async_initialize_triggers](https://developers.home-assistant.io/blog/2026/06/30/async-initialize-triggers-home-assistant-start-deprecated) |
| `docs/ha-release/2026.7/blog-2026-06-30-new-unit-enumerators.md` | `6c84f3b52c79` | [Introducing new unit enumerators](https://developers.home-assistant.io/blog/2026/06/30/new-unit-enumerators) |
| `docs/ha-release/2026.8/release-notes.md` | `8a58e75ed8a5` | [2026.8: Approachable by design](https://www.home-assistant.io/blog/2026/08/05/release-20268/) |
| `docs/ha-release/2026.8/blog-2026-07-03-media-source-search.md` | `54191366b9a7` | [Media sources can now be searched](https://developers.home-assistant.io/blog/2026/07/03/media-source-search) |
| `docs/ha-release/2026.8/blog-2026-07-05-modernizing-modbus.md` | `27ca2f1ef523` | [Modernizing Modbus in Home Assistant](https://developers.home-assistant.io/blog/2026/07/05/modernizing-modbus) |
| `docs/ha-release/2026.8/blog-2026-07-20-ai-policy.md` | `8c2127768e70` | [Introducing the Open Home Foundation AI Policy](https://developers.home-assistant.io/blog/2026/07/20/ai-policy) |
| `docs/ha-release/2026.8/blog-2026-07-21-device-registry-single-config-entry.md` | `9fb264a82d29` | [Devices are restricted to a single config entry and at most one subentry](https://developers.home-assistant.io/blog/2026/07/21/device-registry-single-config-entry) |
| `docs/ha-release/2026.8/blog-2026-07-22-button-standard-event-types.md` | `7859b17dfa0a` | [Standard event types for button event entities](https://developers.home-assistant.io/blog/2026/07/22/button-standard-event-types) |
| `docs/ha-release/2026.8/blog-2026-07-31-frontend-component-updates-2026-8.md` | `fa2ccb3241ab` | [Frontend component updates in 2026.8](https://developers.home-assistant.io/blog/2026/07/31/frontend-component-updates-2026.8) |
| `docs/ha-release/2026.9/release-notes.md` | `f1a3bdec0859` | [2026.9: There's room on this bus](https://www.home-assistant.io/blog/2026/09/02/release-20269/) |
| `docs/ha-release/2026.9/blog-2026-07-05-modernizing-modbus.md` | `27ca2f1ef523` | [Modernizing Modbus in Home Assistant](https://developers.home-assistant.io/blog/2026/07/05/modernizing-modbus) |
| `docs/ha-release/2026.9/blog-2026-08-19-device-registry-websocket-api-changes.md` | `dfa2c23ff672` | [Device registry WebSocket API changes](https://developers.home-assistant.io/blog/2026/08/19/device-registry-websocket-api-changes) |
| `docs/ha-release/2026.9/blog-2026-08-24-device-registry-follow-up-changes.md` | `b7fc6788923d` | [More device registry deprecations, new helpers and validation](https://developers.home-assistant.io/blog/2026/08/24/device-registry-follow-up-changes) |
| `docs/ha-release/2026.9/blog-2026-08-31-deprecate-configurator.md` | `c70333d9e9fb` | [Configurator integration is now deprecated](https://developers.home-assistant.io/blog/2026/08/31/deprecate-configurator) |
| `docs/ha-release/2026.9/blog-2026-09-02-modbus-get-hub-deprecation.md` | `71846148a04c` | [Deprecating modbus.get_hub in favor of async_get_unit](https://developers.home-assistant.io/blog/2026/09/02/modbus-get-hub-deprecation) |
