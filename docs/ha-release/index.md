# The sources for Home Assistant 2026.6, 2026.7, 2026.8, 2026.9, 2026.10

Fetched by `scripts/fetch_ha_sources.py`, last on 2026-10-17. Every file below
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
change is actually in is core's to answer at the tag, never the post's. A release's
notes link the posts that shipped with it, so a post the feed omits is still caught.

Each file opens with its own source URL and the terms the host publishes it under,
and the `sha256` below is the first twelve characters of that file's hash — the
suite compares them, so a source emptied or altered in place stops matching the line
that says what it is.

| Source | sha256 | What it is |
|---|---|---|
| `docs/ha-release/2026.6/release-notes.md` | `e48d0c7bfbd6` | [2026.6: Pick a card, any card — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-06-03-release-20266.markdown) |
| `docs/ha-release/2026.6/blog-2026-04-27-pyserial-to-serialx.md` | `6a5f13d96299` | [Serious about serial: migrating from pyserial to serialx](https://contributors.home-assistant.io/blog/2026/04/27/pyserial-to-serialx/) |
| `docs/ha-release/2026.6/blog-2026-05-04-frontend-component-updates-2026-5.md` | `266ff04dd0af` | [Frontend component updates in 2026.5](https://contributors.home-assistant.io/blog/2026/05/04/frontend-component-updates-2026.5/) |
| `docs/ha-release/2026.6/blog-2026-05-04-frontend-context-groups-decorators.md` | `df58798dc78f` | [Frontend context groups, new context decorators and deprecated contexts](https://contributors.home-assistant.io/blog/2026/05/04/frontend-context-groups-decorators/) |
| `docs/ha-release/2026.6/blog-2026-05-07-config-entry-listener-together-with-reloading-methods.md` | `aa9267218624` | [Deprecating config entry listener with reloading methods in config flow](https://contributors.home-assistant.io/blog/2026/05/07/config-entry-listener-together-with-reloading-methods/) |
| `docs/ha-release/2026.6/blog-2026-05-11-format-entity-name-helper.md` | `cb4847855e82` | [Format entity names in custom cards](https://contributors.home-assistant.io/blog/2026/05/11/format-entity-name-helper/) |
| `docs/ha-release/2026.6/blog-2026-05-11-mqtt-publish-api-changes.md` | `90affe8dd1f2` | [MQTT publish API changes](https://contributors.home-assistant.io/blog/2026/05/11/mqtt-publish-api-changes/) |
| `docs/ha-release/2026.6/blog-2026-05-11-mqtt-publish-api-message-expiry-interval.md` | `0a73aecebf06` | [MQTT publish API supports message expiry interval](https://contributors.home-assistant.io/blog/2026/05/11/mqtt-publish-api-message-expiry-interval/) |
| `docs/ha-release/2026.6/blog-2026-05-13-condition-script-api-changes.md` | `c4c2401d91c2` | [Changes to the condition and script APIs](https://contributors.home-assistant.io/blog/2026/05/13/condition-script-api-changes/) |
| `docs/ha-release/2026.6/blog-2026-05-20-browse-media-source-root-class.md` | `610482cb0b8f` | [BrowseMediaSource: domain is now required](https://contributors.home-assistant.io/blog/2026/05/20/browse-media-source-root-class/) |
| `docs/ha-release/2026.6/blog-2026-05-26-advanced-mode-config-flow-deprecation.md` | `756b7c2e4be5` | [Deprecation of advanced mode in data entry flow](https://contributors.home-assistant.io/blog/2026/05/26/advanced-mode-config-flow-deprecation/) |
| `docs/ha-release/2026.6/blog-2026-05-27-custom-card-suggestions.md` | `31011e657b24` | [Custom card suggestions in the card picker](https://contributors.home-assistant.io/blog/2026/05/27/custom-card-suggestions/) |
| `docs/ha-release/2026.6/blog-2026-05-27-frontend-component-updates-2026-6.md` | `b0519044bc23` | [Frontend component updates in 2026.6](https://contributors.home-assistant.io/blog/2026/05/27/frontend-component-updates-2026.6/) |
| `docs/ha-release/2026.7/release-notes.md` | `e5980a5812bf` | [2026.7: Automations that speak your language — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-07-01-release-20267.markdown) |
| `docs/ha-release/2026.7/blog-2026-06-15-device-tracker-changes.md` | `f0bbb0fb03ff` | [Changes to device tracker entity models](https://contributors.home-assistant.io/blog/2026/06/15/device-tracker-changes/) |
| `docs/ha-release/2026.7/blog-2026-06-23-frontend-component-updates-2026-7.md` | `88e5ad2fbdbd` | [Frontend component updates in 2026.7](https://contributors.home-assistant.io/blog/2026/06/23/frontend-component-updates-2026.7/) |
| `docs/ha-release/2026.7/blog-2026-06-30-async-initialize-triggers-home-assistant-start-deprecated.md` | `b57c38f17dd7` | [Deprecation of the home_assistant_start flag of async_initialize_triggers](https://contributors.home-assistant.io/blog/2026/06/30/async-initialize-triggers-home-assistant-start-deprecated/) |
| `docs/ha-release/2026.7/blog-2026-06-30-new-unit-enumerators.md` | `d3c76c7b6e30` | [Introducing new unit enumerators](https://contributors.home-assistant.io/blog/2026/06/30/new-unit-enumerators/) |
| `docs/ha-release/2026.8/release-notes.md` | `6f5dca184588` | [2026.8: Approachable by design — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-08-05-release-20268.markdown) |
| `docs/ha-release/2026.8/blog-2026-07-03-media-source-search.md` | `185c399ca8f6` | [Media sources can now be searched](https://contributors.home-assistant.io/blog/2026/07/03/media-source-search/) |
| `docs/ha-release/2026.8/blog-2026-07-05-modernizing-modbus.md` | `1e4ec856c912` | [Modernizing Modbus in Home Assistant](https://contributors.home-assistant.io/blog/2026/07/05/modernizing-modbus/) |
| `docs/ha-release/2026.8/blog-2026-07-20-ai-policy.md` | `129199da776f` | [Introducing the Open Home Foundation AI Policy](https://contributors.home-assistant.io/blog/2026/07/20/ai-policy/) |
| `docs/ha-release/2026.8/blog-2026-07-21-device-registry-single-config-entry.md` | `b0df16f55dfd` | [Devices are restricted to a single config entry and at most one subentry](https://contributors.home-assistant.io/blog/2026/07/21/device-registry-single-config-entry/) |
| `docs/ha-release/2026.8/blog-2026-07-22-button-standard-event-types.md` | `6bbfda772f2e` | [Standard event types for button event entities](https://contributors.home-assistant.io/blog/2026/07/22/button-standard-event-types/) |
| `docs/ha-release/2026.8/blog-2026-07-31-frontend-component-updates-2026-8.md` | `6175991fb44f` | [Frontend component updates in 2026.8](https://contributors.home-assistant.io/blog/2026/07/31/frontend-component-updates-2026.8/) |
| `docs/ha-release/2026.9/release-notes.md` | `28cf520bc5f9` | [2026.9: There's room on this bus — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-09-02-release-20269.markdown) |
| `docs/ha-release/2026.9/blog-2026-08-19-device-registry-websocket-api-changes.md` | `cbacadc67fd7` | [Device registry WebSocket API changes](https://contributors.home-assistant.io/blog/2026/08/19/device-registry-websocket-api-changes/) |
| `docs/ha-release/2026.9/blog-2026-08-24-device-registry-follow-up-changes.md` | `6e72d5852ee6` | [More device registry deprecations, new helpers and validation](https://contributors.home-assistant.io/blog/2026/08/24/device-registry-follow-up-changes/) |
| `docs/ha-release/2026.9/blog-2026-08-31-deprecate-configurator.md` | `4bb40486f390` | [Configurator integration is now deprecated](https://contributors.home-assistant.io/blog/2026/08/31/deprecate-configurator/) |
| `docs/ha-release/2026.9/blog-2026-09-02-modbus-get-hub-deprecation.md` | `1faeabbc3849` | [Deprecating modbus.get_hub in favor of async_get_unit](https://contributors.home-assistant.io/blog/2026/09/02/modbus-get-hub-deprecation/) |
| `docs/ha-release/2026.10/release-notes.md` | `c2f5d01127fc` | [2026.10: You are here 📍 — backward-incompatible changes](https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-10-07-release-202610.markdown) |
| `docs/ha-release/2026.10/blog-2026-09-04-device-and-state-class-selectors.md` | `be174dc64583` | [New device and state class selectors](https://contributors.home-assistant.io/blog/2026/09/04/device-and-state-class-selectors/) |
| `docs/ha-release/2026.10/blog-2026-09-07-oauth2-central-error-handling.md` | `2cc7be2db657` | [OAuth2 error handling moved into the helper](https://contributors.home-assistant.io/blog/2026/09/07/oauth2-central-error-handling/) |
| `docs/ha-release/2026.10/blog-2026-09-11-lawn-mower-stop-action-idle-activity.md` | `a881f9ee8cee` | [New stop action and idle activity for lawn mowers](https://contributors.home-assistant.io/blog/2026/09/11/lawn-mower-stop-action-idle-activity/) |
| `docs/ha-release/2026.10/blog-2026-09-15-device-entry-config-entries-deprecation.md` | `eba5f9691ac0` | [`DeviceEntry.config_entries` deprecation is now enforced](https://contributors.home-assistant.io/blog/2026/09/15/device-entry-config-entries-deprecation/) |
| `docs/ha-release/2026.10/blog-2026-09-17-use-config-entry-exc-in-migration.md` | `74090363a73d` | [Use Config Entry exceptions in integration migration method](https://contributors.home-assistant.io/blog/2026/09/17/Use-config-entry-exc-in-migration/) |
| `docs/ha-release/2026.10/blog-2026-09-26-llm-tool-result.md` | `a225dc69eaf7` | [LLM tools return a ToolResult and declare their integration](https://contributors.home-assistant.io/blog/2026/09/26/llm-tool-result/) |
| `docs/ha-release/2026.10/blog-2026-09-28-central-config-flow-abort-reasons.md` | `4e604c191b2f` | [Shared config flow abort reasons are translated centrally](https://contributors.home-assistant.io/blog/2026/09/28/central-config-flow-abort-reasons/) |
| `docs/ha-release/2026.10/blog-2026-09-30-probatio-validation-engine.md` | `68f915302de5` | [Probatio is our validation engine](https://contributors.home-assistant.io/blog/2026/09/30/probatio-validation-engine/) |
| `docs/ha-release/2026.10/blog-2026-10-06-restore-state-last-states-removal.md` | `a009beaa4ef2` | [Removal of RestoreStateData.last_states](https://contributors.home-assistant.io/blog/2026/10/06/restore-state-last-states-removal/) |
