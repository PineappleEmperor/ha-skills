# New unit of measurement selector

Fetched from https://contributors.home-assistant.io/blog/2026/10/09/uom-selector/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

New unit of measurement selector

Jan BouwhuisOctober 9, 2026·4 min read

Core and integrations

A new UnitOfMeasurementSelector lets users pick a unit of measurement in a config, options, or subentry flow, and in blueprints. Until now, flows had to build a SelectSelector with a hand-made list of units, often rebuilt from the previous step's input. The new selector gets its units from the sensor unit tables, so the options always match what a sensor entity accepts.

Limit the units

The selector config has two optional keys, device_classes and state_classes. Both take a single sensor device class or state class, or a list of them.

Python

import probatio

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT
from homeassistant.helpers.selector import (
UnitOfMeasurementSelector,
UnitOfMeasurementSelectorConfig,
)

DATA_SCHEMA = probatio.Schema(
{
probatio.Required(CONF_UNIT_OF_MEASUREMENT): UnitOfMeasurementSelector(
UnitOfMeasurementSelectorConfig(
device_classes=[SensorDeviceClass.ENERGY],
state_classes=[SensorStateClass.TOTAL_INCREASING],
)
),
}
)

The allowed units follow the rules for sensor entities:

Device classes: the selector allows the units of all the listed device classes, taken from DEVICE_CLASS_UNITS. A non-numeric device class, like date, enum, or timestamp, allows only no unit. A device class without a unit table, like monetary, doesn't limit the units.

State classes: the selector allows the units of all the listed state classes, taken from STATE_CLASS_UNITS, but only those that are also allowed by the device classes. A state class without a unit table, like measurement or total, doesn't limit the units.

No limit: without a device class or state class limit, the selector accepts any string, so the user can enter a custom unit.

The selector returns the unit as a string, or None when the user picks no unit.

Filter the units on other fields

Often the user picks the device class and state class in the same form as the unit, using the device class and state class selectors. Use the context key in the selector config to tell the frontend which fields hold these values. The frontend then narrows the list of units as soon as the user changes one of those fields.

The unit of measurement selector supports these context keys:

Context key
Field selector type

filter_device_class
device_class

filter_state_class
state_class

The value of each key is the name of the field in the same schema.

Python

import probatio

from homeassistant.const import (
CONF_DEVICE_CLASS,
CONF_STATE_CLASS,
CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.helpers.selector import (
DeviceClassSelector,
DeviceClassSelectorConfig,
StateClassSelector,
UnitOfMeasurementSelector,
UnitOfMeasurementSelectorConfig,
)

DATA_SCHEMA = probatio.Schema(
{
probatio.Optional(CONF_DEVICE_CLASS): DeviceClassSelector(
DeviceClassSelectorConfig(domain="sensor")
),
probatio.Optional(CONF_STATE_CLASS): StateClassSelector(),
probatio.Optional(CONF_UNIT_OF_MEASUREMENT): UnitOfMeasurementSelector(
UnitOfMeasurementSelectorConfig(
context={
"filter_device_class": CONF_DEVICE_CLASS,
"filter_state_class": CONF_STATE_CLASS,
}
)
),
}
)

The context is validated with the rest of the selector config. It only accepts the context keys listed above, with a string value. A context key can't be combined with the matching fixed limit: you can't use filter_device_class together with device_classes, or filter_state_class together with state_classes.

The context only affects the frontend. The selector validates the submitted unit against its device_classes and state_classes config, not against the values of the other fields. Your flow still needs to check that the unit is valid for the device class and state class that the user picked, and return an error if it isn't.

Use the selector in blueprints

The selector is also available in blueprints and service descriptions as the unit_of_measurement selector. It takes the same config as in Python: device_classes, state_classes, and context.

Because the context is part of the selector config, it also works in blueprints. The value of each context key is the name of another input of the blueprint. In this example, the units offered for the unit input follow the device class and state class that the user picked in the device_class and state_class inputs:

YAML

blueprint:
name: Sensor with a unit
domain: template
input:
device_class:
name: Device class
selector:
device_class:
domain: sensor
state_class:
name: State class
selector:
state_class:
unit:
name: Unit of measurement
selector:
unit_of_measurement:
context:
filter_device_class: device_class
filter_state_class: state_class

The Selectors documentation will describe the selector once home-assistant.io PR #48587 is merged.

Migrating existing unit of measurement selectors

Flows that let the user pick a unit with a SelectSelector built from DEVICE_CLASS_UNITS or STATE_CLASS_UNITS should be migrated to use UnitOfMeasurementSelector. You no longer need to build the unit list from the previous submission. Instead, add a context so the frontend filters the units for you.

For more information, see core PR #183337 and the data entry flow documentation.
