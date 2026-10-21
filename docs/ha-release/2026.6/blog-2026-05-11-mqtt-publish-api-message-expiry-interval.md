# MQTT publish API supports message expiry interval

Fetched from https://contributors.home-assistant.io/blog/2026/05/11/mqtt-publish-api-message-expiry-interval/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

MQTT publish API supports message expiry interval

Jan BouwhuisMay 11, 2026·1 min read

Core and integrations

The MQTT publish API now supports setting a message expiry interval.
Previously, retained messages were stored by the broker until they were replaced or explicitly cleared. With a message_expiry_interval set (in seconds), a published message — including a retained one — will automatically expire after the specified interval.
This option is only supported when using MQTT protocol version 5; it is ignored when using earlier protocol versions.

The new API signatures are:

Python

def publish(
hass: HomeAssistant,
topic: str,
payload: PublishPayloadType,
qos: int = 0,
retain: bool = False,
encoding: str | None = DEFAULT_ENCODING,
*,
message_expiry_interval: int | None = None,
) -> None:
"""Publish message to a MQTT topic."""

and

Python

async def async_publish(
hass: HomeAssistant,
topic: str,
payload: PublishPayloadType,
qos: int = 0,
retain: bool = False,
encoding: str | None = DEFAULT_ENCODING,
*,
message_expiry_interval: int | None = None,
) -> None:
"""Publish message to a MQTT topic."""
