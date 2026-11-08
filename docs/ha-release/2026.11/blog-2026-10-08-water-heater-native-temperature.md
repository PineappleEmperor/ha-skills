# Water heater entities now expose their temperature unit

Fetched from https://contributors.home-assistant.io/blog/2026/10/08/water-heater-native-temperature/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Water heater entities now expose their temperature unit

Erik MontnémeryOctober 8, 2026·2 min read

Core and integrations

As of Home Assistant Core 2026.11, water heater entities have a new temperature_unit state attribute, and the temperature properties integrations implement have been renamed with a native_ prefix.

Background

The water heater entity converts all temperatures it writes to the state machine to the unit system configured by the user. Until now, the unit was not part of the state, so anyone reading the state had to know that water heater temperatures follow the configured unit system. This is inconsistent with other entities, such as sensor, number and weather, which expose the unit next to the value.

The temperature_unit state attribute

The temperature_unit state attribute holds the unit of the temperatures in the state, which is the temperature unit of the user's configured unit system. It's set by the WaterHeaterEntity base class and can't be overridden by integrations.

Renamed properties

Integrations specify temperatures in the unit used by the device, and the base class converts them. To make that clear, and to match how sensor, number and weather entities name native values, the following properties and their _attr_ shorthand attributes have been renamed:

Old name
New name

current_temperature
native_current_temperature

target_temperature
native_target_temperature

target_temperature_high
native_target_temperature_high

target_temperature_low
native_target_temperature_low

temperature_unit
native_temperature_unit

The old names keep working, but implementing them, setting the _attr_ attributes or reading them logs a warning. Support for the old names will be removed in Home Assistant Core 2027.11.

min_temp, max_temp and target_temperature_step are not renamed, and are still specified in the native unit.

More details can be found in the water heater entity documentation.

Example

Old:

Python

class MyWaterHeaterEntity(WaterHeaterEntity):
_attr_temperature_unit = UnitOfTemperature.CELSIUS

@property
def current_temperature(self) -> float | None:
return self.device.temperature

async def async_update(self) -> None:
self._attr_target_temperature = await self.device.get_setpoint()

New:

Python

class MyWaterHeaterEntity(WaterHeaterEntity):
_attr_native_temperature_unit = UnitOfTemperature.CELSIUS

@property
def native_current_temperature(self) -> float | None:
return self.device.temperature

async def async_update(self) -> None:
self._attr_native_target_temperature = await self.device.get_setpoint()
