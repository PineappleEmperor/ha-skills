# New stop action and idle activity for lawn mowers

Fetched from https://contributors.home-assistant.io/blog/2026/09/11/lawn-mower-stop-action-idle-activity/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

New stop action and idle activity for lawn mowers

Paul BotteinSeptember 11, 2026·1 min read

Core and integrations

As of Home Assistant Core 2026.10, LawnMowerEntity supports a stop action and an IDLE activity.

stop cancels the current mowing task without returning the mower to the dock. It differs from pause, which keeps the task so it can be resumed, and from dock, which sends the mower home. To support it, add LawnMowerEntityFeature.STOP to the supported features and implement stop or async_stop.

LawnMowerActivity.IDLE describes a mower that is stopped, but neither docked nor paused. Integrations that mapped such a state to PAUSED or ERROR should now use IDLE.

More details can be found in the documentation.

Example

Python

class MyLawnMower(LawnMowerEntity):
_attr_supported_features = (
LawnMowerEntityFeature.START_MOWING
| LawnMowerEntityFeature.DOCK
| LawnMowerEntityFeature.STOP
)

async def async_stop(self) -> None:
"""Stop the mower and cancel the current task."""
await self.mower.stop()
self._attr_activity = LawnMowerActivity.IDLE
self.async_write_ha_state()
