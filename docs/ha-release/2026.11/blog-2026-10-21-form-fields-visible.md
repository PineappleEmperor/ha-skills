# Show form fields based on other fields

Fetched from https://contributors.home-assistant.io/blog/2026/10/21/form-fields-visible/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Show form fields based on other fields

Paul BotteinOctober 21, 2026·1 min read

Core and integrations

As of Home Assistant Core 2026.11, config flows, options flows, and blueprints can show a field only while other fields have certain values. You no longer need an extra step, or to show the form again after submit, just to show or hide a few fields. Flows and blueprints use the same visible condition.

Config and options flows

Give the Required or Optional marker from homeassistant.data_entry_flow a visible condition:

Python

from homeassistant import data_entry_flow
from homeassistant.helpers.selector import BooleanSelector

DATA_SCHEMA = probatio.Schema(
{
probatio.Required(CONF_SSL, default=False): BooleanSelector(),
data_entry_flow.Required(
CONF_VERIFY_SSL,
default=True,
visible={"field": CONF_SSL, "value": True},
): BooleanSelector(),
}
)

The Verify SSL certificate checkbox only shows when Use SSL is checked. While it is hidden, it is not required and its value is not saved.

Read fields that show based on another field for the available conditions and how hidden fields behave.

Blueprints

Blueprint inputs and input sections take the same visible key, next to default and collapsed:

YAML

blueprint:
name: Motion light
domain: automation
input:
dim_mode:
name: Dimming
default: none
selector:
select:
options:
- none
- fixed
brightness:
name: Brightness
default: 50
visible:
field: dim_mode
value: fixed
selector:
number:
min: 1
max: 100

Brightness only shows when Dimming is set to fixed. A hidden input does not need a value. The automation then gets the input's default (50 here), or None when it has no default, even if a value was entered before the input was hidden. Setting visible on an input section hides the whole section and its inputs.

Read showing inputs based on other inputs in the user documentation for the details.
