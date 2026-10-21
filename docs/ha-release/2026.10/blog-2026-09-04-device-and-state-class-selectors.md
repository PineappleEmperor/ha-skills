# New device and state class selectors

Fetched from https://contributors.home-assistant.io/blog/2026/09/04/device-and-state-class-selectors/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

New device and state class selectors

Jan BouwhuisSeptember 4, 2026·2 min read

Core and integrations

New selectors are available to choose a device class or sensor state class.

These selectors can be used in config flows and blueprints when requesting a device or state class from the user.

Device class selector

The new DeviceClassSelector is available for selecting device classes in config flows and blueprints. It supports device classes for the following platforms:

Python

Platform.BINARY_SENSOR: BinarySensorDeviceClass
Platform.BUTTON: ButtonDeviceClass
Platform.COVER: CoverDeviceClass
Platform.EVENT: EventDeviceClass
Platform.HUMIDIFIER: HumidifierDeviceClass
Platform.INFRARED: InfraredDeviceClass
Platform.MEDIA_PLAYER: MediaPlayerDeviceClass
Platform.NUMBER: NumberDeviceClass
Platform.SENSOR: SensorDeviceClass
Platform.SWITCH: SwitchDeviceClass
Platform.UPDATE: UpdateDeviceClass
Platform.VALVE: ValveDeviceClass

Device class selector examples

Example of a device class selector that returns a single device class:

Python

vol.Schema(
{
vol.Optional(CONF_DEVICE_CLASS): DeviceClassSelector(
DeviceClassSelectorConfig(domain=Platform.SENSOR)
),
}
)

Example of a device class selector that returns multiple device classes as a list:

Python

vol.Schema(
{
vol.Optional(CONF_DEVICE_CLASS): DeviceClassSelector(
DeviceClassSelectorConfig(
domain=Platform.BINARY_SENSOR,
multiple=True,
)
),
}
)

Sensor state class selector

The new StateClassSelector is available for selecting sensor state classes in config flows and blueprints.

Sensor state class selector examples

Example of a sensor state class selector that returns a single state class:

Python

vol.Schema(
{
vol.Optional(CONF_STATE_CLASS): StateClassSelector(),
}
)

Example of a sensor state class selector that returns a single state class with only a filtered subset of available state classes:

Python

vol.Schema(
{
vol.Optional(CONF_STATE_CLASS): StateClassSelector(
StateClassSelectorConfig(
state_classes=[
SensorStateClass.MEASUREMENT,
SensorStateClass.TOTAL_INCREASING,
],
)
),
}
)

Example of a state class selector that returns multiple state classes as a list:

Python

vol.Schema(
{
vol.Optional(CONF_STATE_CLASS): StateClassSelector(
StateClassSelectorConfig(multiple=True),
),
}
)

Migrating existing device and state class selectors

Unlike using a generic SelectSelector, the DeviceClassSelector allows the frontend to automatically translate device classes into user-friendly names.

Existing implementations that select a device or state class using SelectSelector should be migrated to use DeviceClassSelector or StateClassSelector. After migration, any stale translations related to the old selector values should be removed.

The Selectors documentation has been updated to include the new selectors.
