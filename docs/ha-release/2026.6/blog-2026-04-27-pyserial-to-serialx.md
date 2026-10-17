# Serious about serial: migrating from pyserial to serialx

Fetched from https://contributors.home-assistant.io/blog/2026/04/27/pyserial-to-serialx/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Serious about serial: migrating from pyserial to serialx

Nikita NikishinApril 27, 2026·1 min read

Core and integrations

Existing integrations and libraries communicating with serial ports should migrate from pyserial, pyserial-asyncio, and pyserial-asyncio-fast to serialx. This new library features native asyncio support on all platforms and will allow your integrations and libraries to take advantage of ESPHome serial proxies in Home Assistant, and includes critical fixes for asyncio event loop stability.

Background

pyserial has been the de facto serial library in Python for many years and has broad support for all popular platforms. Its API, however, predates asyncio in Python and is sync-only. The pyserial-asyncio package was eventually released to bridge pyserial with asyncio. Unfortunately, pyserial-asyncio development never reached 1.0 stability or cross-platform support, and neither pyserial nor pyserial-asyncio have had PyPI releases in almost five years. We forked pyserial-asyncio and released pyserial-asyncio-fast to fix outstanding issues affecting Core event loop stability.

We developed serialx from the ground up as a modern Python serial library with native sync and async APIs. It is import-compatible with the serial, serial_asyncio, and serial_asyncio_fast modules and allows existing packages to migrate with very minimal changes, if any.

Migration

The serialx documentation has an extensive migration guide that goes into more detail.

Most packages just need to replace pyserial, pyserial-asyncio, and pyserial-asyncio-fast with serialx in their setup.py or pyproject.toml file and update exception handling to replace broad catching of SerialException with more granular error handling (such as OSError and TimeoutError).

Packages directly constructing a sync serial.Serial() object should migrate to using the serialx.serial_for_url() helper to ensure automatic compatibility with all supported protocols.

Prompt for your agent

The migration itself is mechanical, paste the following instructions into your agent of choice:

Migrate my code from pyserial, pyserial-asyncio, and pyserial-asyncio-fast to serialx using
https://raw.githubusercontent.com/puddly/serialx/refs/heads/dev/docs/how-to/pyserial-migration.md
