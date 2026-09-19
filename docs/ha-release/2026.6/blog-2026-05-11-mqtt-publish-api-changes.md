# MQTT publish API changes

Fetched from https://developers.home-assistant.io/blog/2026/05/11/mqtt-publish-api-changes
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified only in format: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. The wording is the author's, unaltered.

MQTT publish API changes

May 11, 2026 · One min read

Jan Bouwhuis

In the future, the MQTT publish API will require explicit values for qos and retain. Passing None for either argument will no longer be supported.
Custom integrations should update their code to accept the defaults, or pass valid typed arguments.
The fallbacks of None to a valid value for qos and retain will stop working with HA Core 2027.6.

The new API signatures are:

def publish(

hass: HomeAssistant,

topic: str,

payload: PublishPayloadType,

qos: int = 0,

retain: bool = False,

encoding: str | None = DEFAULT_ENCODING,

) -> None:

"""Publish message to a MQTT topic."""

hass.create_task(async_publish(hass, topic, payload, qos, retain, encoding))

and

async def async_publish(

hass: HomeAssistant,

topic: str,

payload: PublishPayloadType,

qos: int = 0,

retain: bool = False,

encoding: str | None = DEFAULT_ENCODING,

) -> None:

"""Publish message to a MQTT topic."""
