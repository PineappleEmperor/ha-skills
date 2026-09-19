# Deprecating config entry listener with reloading methods in config flow

Fetched from https://developers.home-assistant.io/blog/2026/05/07/config-entry-listener-together-with-reloading-methods
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Deprecating config entry listener with reloading methods in config flow

May 7, 2026 · One min read

G Johansson

As of Home Assistant Core 2026.6, using a config entry listener together with any reloading methods in a config flow is deprecated and will result in an error from 2026.12.

Background​

Using a config entry listener together with any reloading methods in a config flow can cause the integration to reload twice and/or create a race condition.

Possible solutions​

Remove the config entry listener and rely only on the reloading methods in your config flow.

Use async_update_and_abort() instead of async_update_reload_and_abort().

Set reload_on_update=False when calling _abort_if_unique_id_configured().

More details can be found in the core PR.
