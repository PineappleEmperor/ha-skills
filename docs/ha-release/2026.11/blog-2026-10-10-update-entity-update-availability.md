# Update entities can customize update availability

Fetched from https://contributors.home-assistant.io/blog/2026/10/10/update-entity-update-availability/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Update entities can customize update availability

TomerOctober 10, 2026·1 min read

Core and integrations

As of Home Assistant Core 2026.11, update entities can override the new
has_update property to determine whether an update is available.

Previously, update entities determined availability by comparing
installed_version and latest_version. Integrations can still customize that
comparison by overriding version_is_newer, and existing implementations
continue to work unchanged.

Integrations whose device or service provides update availability directly can
now override has_update instead:

Python

@property
def has_update(self) -> bool:
"""Return whether an update is available."""
return self.device.update_available

Home Assistant reads has_update only when both versions are known and differ,
and the latest version has not been skipped. The default implementation calls
version_is_newer, preserving the existing behavior.

For more details, see the
update entity documentation.
