# The sources for Home Assistant 2026.6, 2026.7, 2026.8, 2026.9

Fetched by `scripts/fetch_ha_sources.py`, last on 2026-09-20. Every file below
is a **secondary** source: it says what changed and why, and never how an API is
spelled — core at the release tag says that, and the core rule of
`docs/release-refresh.md` says why.

The governance gate reads this directory and demands these files before it will let
a reference file make a claim about one of the releases below. What exactly it
demands, and what it does not, is `unread_sources` in `scripts/governance_gate.py`,
which is the only place that rule is stated; re-run the script to add a release.

**The window is a net, not a claim.** Posts are gathered by publication date, between
one release and the next, so a post published in the days before a release may well
describe the release *after* it — the beta was cut a week earlier. Which release a
change is actually in is core's to answer at the tag, never the post's. The net has a
hole of its own at the far end: the developer blog's feed carries a fixed number of
entries, so a backfill reaching further back than the feed does collects only the
posts still in it.

Each file opens with its own source URL and the terms the host publishes it under,
and the `sha256` below is the first twelve characters of that file's hash — the
suite compares them, so a source emptied or altered in place stops matching the line
that says what it is.

| Source | sha256 | What it is |
|---|---|---|
| `docs/ha-release/2026.6/release-notes.md` | `e48d0c7bfbd6` | [2026.6: Pick a card, any card — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-06-03-release-20266.markdown) |
| `docs/ha-release/2026.6/blog-2026-05-07-config-entry-listener-together-with-reloading-methods.md` | `b422447bdded` | [Deprecating config entry listener with reloading methods in config flow](https://developers.home-assistant.io/blog/2026/05/07/config-entry-listener-together-with-reloading-methods) |
| `docs/ha-release/2026.6/blog-2026-05-11-format-entity-name-helper.md` | `484d4f8a4221` | [Format entity names in custom cards](https://developers.home-assistant.io/blog/2026/05/11/format-entity-name-helper) |
| `docs/ha-release/2026.6/blog-2026-05-11-mqtt-publish-api-changes.md` | `ae7360055256` | [MQTT publish API changes](https://developers.home-assistant.io/blog/2026/05/11/mqtt-publish-api-changes) |
| `docs/ha-release/2026.6/blog-2026-05-11-mqtt-publish-api-message-expiry-interval.md` | `4eadb51419ff` | [MQTT publish API supports message expiry interval](https://developers.home-assistant.io/blog/2026/05/11/mqtt-publish-api-message-expiry-interval) |
| `docs/ha-release/2026.6/blog-2026-05-13-condition-script-api-changes.md` | `c1135efcf5c7` | [Changes to the condition and script APIs](https://developers.home-assistant.io/blog/2026/05/13/condition-script-api-changes) |
| `docs/ha-release/2026.6/blog-2026-05-20-browse-media-source-root-class.md` | `455200923fe2` | [BrowseMediaSource: domain is now required](https://developers.home-assistant.io/blog/2026/05/20/browse-media-source-root-class) |
| `docs/ha-release/2026.6/blog-2026-05-26-advanced-mode-config-flow-deprecation.md` | `89130e039194` | [Deprecation of advanced mode in data entry flow](https://developers.home-assistant.io/blog/2026/05/26/advanced-mode-config-flow-deprecation) |
| `docs/ha-release/2026.6/blog-2026-05-27-custom-card-suggestions.md` | `2620f29dab8a` | [Custom card suggestions in the card picker](https://developers.home-assistant.io/blog/2026/05/27/custom-card-suggestions) |
| `docs/ha-release/2026.6/blog-2026-05-27-frontend-component-updates-2026-6.md` | `c282823c508f` | [Frontend component updates in 2026.6](https://developers.home-assistant.io/blog/2026/05/27/frontend-component-updates-2026.6) |
| `docs/ha-release/2026.7/release-notes.md` | `e5980a5812bf` | [2026.7: Automations that speak your language — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-07-01-release-20267.markdown) |
| `docs/ha-release/2026.7/blog-2026-06-15-device-tracker-changes.md` | `804ac25a3863` | [Changes to device tracker entity models](https://developers.home-assistant.io/blog/2026/06/15/device-tracker-changes) |
| `docs/ha-release/2026.7/blog-2026-06-23-frontend-component-updates-2026-7.md` | `097bf6d66e67` | [Frontend component updates in 2026.7](https://developers.home-assistant.io/blog/2026/06/23/frontend-component-updates-2026.7) |
| `docs/ha-release/2026.7/blog-2026-06-30-async-initialize-triggers-home-assistant-start-deprecated.md` | `15cef753f560` | [Deprecation of the home_assistant_start flag of async_initialize_triggers](https://developers.home-assistant.io/blog/2026/06/30/async-initialize-triggers-home-assistant-start-deprecated) |
| `docs/ha-release/2026.7/blog-2026-06-30-new-unit-enumerators.md` | `d242622cc332` | [Introducing new unit enumerators](https://developers.home-assistant.io/blog/2026/06/30/new-unit-enumerators) |
| `docs/ha-release/2026.8/release-notes.md` | `6f5dca184588` | [2026.8: Approachable by design — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-08-05-release-20268.markdown) |
| `docs/ha-release/2026.8/blog-2026-07-03-media-source-search.md` | `e077ca6ed91b` | [Media sources can now be searched](https://developers.home-assistant.io/blog/2026/07/03/media-source-search) |
| `docs/ha-release/2026.8/blog-2026-07-05-modernizing-modbus.md` | `945642139859` | [Modernizing Modbus in Home Assistant](https://developers.home-assistant.io/blog/2026/07/05/modernizing-modbus) |
| `docs/ha-release/2026.8/blog-2026-07-20-ai-policy.md` | `cf8ea73c8240` | [Introducing the Open Home Foundation AI Policy](https://developers.home-assistant.io/blog/2026/07/20/ai-policy) |
| `docs/ha-release/2026.8/blog-2026-07-21-device-registry-single-config-entry.md` | `f878c0e21910` | [Devices are restricted to a single config entry and at most one subentry](https://developers.home-assistant.io/blog/2026/07/21/device-registry-single-config-entry) |
| `docs/ha-release/2026.8/blog-2026-07-22-button-standard-event-types.md` | `9fb1ce05fd2e` | [Standard event types for button event entities](https://developers.home-assistant.io/blog/2026/07/22/button-standard-event-types) |
| `docs/ha-release/2026.8/blog-2026-07-31-frontend-component-updates-2026-8.md` | `f1bcda264b21` | [Frontend component updates in 2026.8](https://developers.home-assistant.io/blog/2026/07/31/frontend-component-updates-2026.8) |
| `docs/ha-release/2026.9/release-notes.md` | `28cf520bc5f9` | [2026.9: There's room on this bus — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-09-02-release-20269.markdown) |
| `docs/ha-release/2026.9/blog-2026-08-19-device-registry-websocket-api-changes.md` | `8eba6e1eac62` | [Device registry WebSocket API changes](https://developers.home-assistant.io/blog/2026/08/19/device-registry-websocket-api-changes) |
| `docs/ha-release/2026.9/blog-2026-08-24-device-registry-follow-up-changes.md` | `e120b085e4d3` | [More device registry deprecations, new helpers and validation](https://developers.home-assistant.io/blog/2026/08/24/device-registry-follow-up-changes) |
| `docs/ha-release/2026.9/blog-2026-08-31-deprecate-configurator.md` | `5fbf2c0963e6` | [Configurator integration is now deprecated](https://developers.home-assistant.io/blog/2026/08/31/deprecate-configurator) |
| `docs/ha-release/2026.9/blog-2026-09-02-modbus-get-hub-deprecation.md` | `1b2a3ec7fb5c` | [Deprecating modbus.get_hub in favor of async_get_unit](https://developers.home-assistant.io/blog/2026/09/02/modbus-get-hub-deprecation) |
