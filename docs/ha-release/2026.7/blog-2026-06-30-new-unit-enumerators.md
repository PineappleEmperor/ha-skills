# Introducing new unit enumerators

Fetched from https://developers.home-assistant.io/blog/2026/06/30/new-unit-enumerators
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified only in format: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. The wording is the author's, unaltered.

Introducing new unit enumerators

June 30, 2026 · One min read

epenet

As of Home Assistant Core 2026.7, the following unit constants are deprecated and replaced
by a corresponding enum:

UnitOfDensity enumerator replaces mass over volume CONCENTRATION_*** constants
("g/m³", "mg/m³", "μg/m³", "μg/ft³")

UnitOfRatio enumerator replaces unit-less ratio CONCENTRATION_*** constants
("ppm", "ppb")

CONCENTRATION_PARTS_PER_CUBIC_METER was only used by a single integration and is deprecated
without a replacement unit.

Please note that the use of PERCENTAGE constant is also deprecated when used as a unit of
measurement, even if the constant itself is not deprecated.
