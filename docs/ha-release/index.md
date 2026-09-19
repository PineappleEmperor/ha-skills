# The sources for Home Assistant 2026.9

Fetched by `scripts/fetch_ha_sources.py` on 2026-09-19. Every file below is a
**secondary** source: it says what changed and why, and never how an API is spelled —
core at the release tag says that, per *A post is not the source of record* in
`plugins/ha/skills/ha-integration/reference/freshness.md`.

The governance gate refuses a patch to `plugins/ha/skills/ha-integration/reference/`
that names a release until it has served every file named here, so this list is what
"open every source" means in practice. Re-run the script to move the window.

**The window is a net, not a claim.** Posts are gathered by publication date, between
one release and the next, and a post published in the days before a release usually
describes the release *after* it — the beta was cut a week earlier. The 2026.9 window
caught a configurator-deprecation post dated three days before 2026.9 shipped, and
`configurator/__init__.py` at the `2026.9.0` tag carries no deprecation at all. Which
release a change is actually in is core's to answer, never the post's.

| Source | What it is |
|---|---|
| `docs/ha-release/2026.9/release-notes.md` | [2026.9: There's room on this bus](https://www.home-assistant.io/blog/2026/09/02/release-20269/) |
| `docs/ha-release/2026.9/blog-2026-08-19-device-registry-websocket-api-changes.md` | [Device registry WebSocket API changes](https://developers.home-assistant.io/blog/2026/08/19/device-registry-websocket-api-changes) |
| `docs/ha-release/2026.9/blog-2026-08-24-device-registry-follow-up-changes.md` | [More device registry deprecations, new helpers and validation](https://developers.home-assistant.io/blog/2026/08/24/device-registry-follow-up-changes) |
| `docs/ha-release/2026.9/blog-2026-08-31-deprecate-configurator.md` | [Configurator integration is now deprecated](https://developers.home-assistant.io/blog/2026/08/31/deprecate-configurator) |
| `docs/ha-release/2026.9/blog-2026-09-02-modbus-get-hub-deprecation.md` | [Deprecating modbus.get_hub in favor of async_get_unit](https://developers.home-assistant.io/blog/2026/09/02/modbus-get-hub-deprecation) |
