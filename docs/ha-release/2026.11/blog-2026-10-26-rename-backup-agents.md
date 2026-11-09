# Backup agents can now be renamed

Fetched from https://contributors.home-assistant.io/blog/2026/10/25/rename-backup-agents/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Backup agents can now be renamed

Josef ZweckOctober 26, 2026·1 min read

Core and integrations

As of Home Assistant Core 2026.11, an integration can rename a backup agent with async_rename_agent.

Use it when your integration changes how it builds the unique_id of an agent, which changes the ID of the agent. Users then keep their backup settings for the agent, and don't have to set it up again.

Python

from homeassistant.components.backup import async_get_manager

async_get_manager(hass).async_rename_agent(
f"{DOMAIN}.{old_agent_unique_id}", f"{DOMAIN}.{new_agent_unique_id}"
)

Add backup to after_dependencies in your manifest.json. Read more in rename an agent.
