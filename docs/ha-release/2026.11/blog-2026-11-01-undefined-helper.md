# Undefined sentinel changes

Fetched from https://contributors.home-assistant.io/blog/2026/11/01/undefined-helper/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Undefined sentinel changes

Marc MuellerNovember 1, 2026·1 min read

Core and integrations

As of Home Assistant Core 2026.12, the UNDEFINED and UndefinedType helpers are deprecated in favor of just Undefined.

Python

# old
from homeassistant.helpers.typing import UNDEFINED, UndefinedType

def some_function(
variable: str | UndefinedType | None = UNDEFINED,
) -> None:
...

Python

# new
from homeassistant.helpers.typing import Undefined

def some_function(
variable: str | Undefined | None = Undefined,
) -> None:
...
