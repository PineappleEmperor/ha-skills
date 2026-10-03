# Configurator integration is now deprecated

Fetched from https://developers.home-assistant.io/blog/2026/08/31/deprecate-configurator
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Configurator integration is now deprecated

August 31, 2026 · One min read

Martin Hjelmare

The Configurator integration has been deprecated and will be removed in Home Assistant 2027.10. The integration was originally created to provide a web-based configuration interface for Home Assistant, but it is no longer recommended for use. No core integrations use the Configurator integration anymore, and it is not recommended for custom integrations either.

The modern way to configure integrations in Home Assistant is via config flows and config entries. Config flows provide a user-friendly interface for setting up and configuring integrations, while config entries allow for easy management of integration settings.
