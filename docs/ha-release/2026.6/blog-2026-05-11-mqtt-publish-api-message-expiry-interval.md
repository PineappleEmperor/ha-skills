# MQTT publish API supports message expiry interval

Fetched from https://developers.home-assistant.io/blog/2026/05/11/mqtt-publish-api-message-expiry-interval
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified only in format: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. The wording is the author's, unaltered.

MQTT publish API supports message expiry interval

May 11, 2026 · One min read

Jan Bouwhuis

The MQTT publish API now supports setting a message expiry interval.
Previously, retained messages were stored by the broker until they were replaced or explicitly cleared. With a message_expiry_interval set (in seconds), a published message — including a retained one — will automatically expire after the specified interval.
This option is only supported when using MQTT protocol version 5; it is ignored when using earlier protocol versions.

The new API signatures are:

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
