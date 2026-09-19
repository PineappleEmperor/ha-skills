# Format entity names in custom cards

Fetched from https://developers.home-assistant.io/blog/2026/05/11/format-entity-name-helper
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified only in format: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. The wording is the author's, unaltered.

Format entity names in custom cards

May 11, 2026 · One min read

Paul Bottein

As of Home Assistant 2026.4, the hass object exposes a formatEntityName helper. It is the same function used by the built-in cards (tile card, entity rows, ...) to compute the display name of an entity from its registry context (entity, device, area, floor). Custom cards can use it to produce names that stay consistent with the rest of the dashboard.

Given a temperature sensor named Temperature on a device named Thermostat:

const stateObj = hass.states["sensor.living_room_thermostat_temperature"];

hass.formatEntityName(

stateObj,

[{ type: "device" }, { type: "entity" }],

{ separator: " · " }

); // "Thermostat · Temperature"

The frontend also ships an entity_name selector. If your card uses the built-in form editor, you can offer users the same name picker the built-in cards use — accepting either a free-form string or a composition of registry items.

Take a look at the updated data documentation for the full reference and more examples.
