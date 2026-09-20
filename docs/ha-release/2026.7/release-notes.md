# 2026.7: Automations that speak your language — backward-incompatible changes

Fetched from https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-07-01-release-20267.markdown
Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of home-assistant/home-assistant.io.
Modified: this is the *Backward-incompatible changes* section of the post's own source markdown, cut at the surrounding `##` headings by `scripts/fetch_ha_sources.py`. Nothing inside it has been changed, added or reordered; the rest of the post — the feature write-ups and the patch-release changelogs — is not kept.

## Backward-incompatible changes

We do our best to avoid making changes to existing functionality that might unexpectedly impact your Home Assistant installation. Unfortunately, sometimes it is inevitable.

We always make sure to document these changes to make the transition as easy as possible for you. This release has the following backward-incompatible changes:

{% details "Purpose-specific triggers and conditions" %}

Several entity triggers and conditions, part of the new purpose-specific triggers and conditions, have been renamed so their keys are consistent across all domains. The old keys no longer work.

The following triggers changed:

- `battery.low` is now `battery.became_low`
- `battery.not_low` is now `battery.no_longer_low`
- `lawn_mower.docked` is now `lawn_mower.returned_to_dock`
- `schedule.turned_off` is now `schedule.block_ended`
- `schedule.turned_on` is now `schedule.block_started`
- `timer.time_remaining` is now `timer.remaining_time_reached`
- `update.update_became_available` is now `update.became_available`
- `vacuum.docked` is now `vacuum.returned_to_dock`

The following conditions changed:

- `climate.target_humidity` is now `climate.is_target_humidity`
- `climate.target_temperature` is now `climate.is_target_temperature`

If an automation or script uses one of these, it will stop working until updated. To fix it, open the affected automation or script, re-select the trigger or condition (it now appears under its new name), and save. If you edit in YAML, replace the old key with the new one from the list above.

([@frenck] - [#174463])

[#174463]: https://github.com/home-assistant/core/pull/174463

{% enddetails %}

{% details "BSB-LAN" %}

The BSB-LAN integration has reduced its support for the older version 1 JSON API. If your BSB-LAN device runs very old firmware that only speaks the version 1 API, update it to firmware that supports the version 2 API to keep everything working.

A repair notification will let you know if your device is affected.

([@liudger] - [#172843]) ([BSB-LAN documentation])

[@liudger]: https://github.com/liudger
[#172843]: https://github.com/home-assistant/core/pull/172843
[BSB-LAN documentation]: /integrations/bsblan/

{% enddetails %}

{% details "iCloud" %}

The `battery_level` attribute has been removed from iCloud device tracker entities. Use the dedicated battery sensor in your automations and scripts instead.

([@some-random-climber] - [#174117]) ([iCloud documentation])

[@some-random-climber]: https://github.com/some-random-climber
[#174117]: https://github.com/home-assistant/core/pull/174117
[iCloud documentation]: /integrations/icloud/

{% enddetails %}

{% details "Person" %}

Person entities no longer report the latitude and longitude of the home zone when their location comes from a presence scanner associated with the home zone.

If you have automations or scripts that check the coordinates of a person, adjust them. To check whether a person is in a specific zone, use the new `in_zones` state attribute instead.

([@emontnemery] - [#173042]) ([Person documentation])

[@emontnemery]: https://github.com/emontnemery
[#173042]: https://github.com/home-assistant/core/pull/173042
[Person documentation]: /integrations/person/

{% enddetails %}

{% details "Rabbit Air" %}

The Rabbit Air fan preset mode values changed from title case to lowercase to match Home Assistant's state convention: `Auto` is now `auto`, `Manual` is now `manual`, and `Pollen` is now `pollen`. The user-facing labels stay the same through translations.

Update any automations, scripts, templates, or action calls that reference the old title-case preset values.

([@MagikalUnicorn] - [#172931]) ([Rabbit Air documentation])

[@MagikalUnicorn]: https://github.com/MagikalUnicorn
[#172931]: https://github.com/home-assistant/core/pull/172931
[Rabbit Air documentation]: /integrations/rabbitair/

{% enddetails %}

{% details "Reolink" %}

Reolink Duo PoE and Duo WiFi dual-lens cameras now expose a sub-device per lens. The camera and motion/AI sensor entities that previously had a "lens 0" or "lens 1" suffix in their name are moved to the new lens sub-devices and lose that suffix. Entity IDs and custom names stay the same, so most automations keep working.

If you target these entities through the camera device, update them to use the new lens sub-devices.

([@Markus98] - [#173037]) ([Reolink documentation])

[@Markus98]: https://github.com/Markus98
[#173037]: https://github.com/home-assistant/core/pull/173037
[Reolink documentation]: /integrations/reolink/

{% enddetails %}

{% details "StarLine" %}

The `battery_level` attribute has been removed from StarLine device tracker entities. Use the dedicated battery sensor in your automations and scripts instead.

([@some-random-climber] - [#174118]) ([StarLine documentation])

[#174118]: https://github.com/home-assistant/core/pull/174118
[StarLine documentation]: /integrations/starline/

{% enddetails %}

{% details "Tesla Fleet" %}

The route device tracker (`device_tracker.<vehicle>_route`) no longer reports the active route's destination name as its state. Its state is now derived from your zones like a normal device tracker (`home`, `not_home`, or a zone name), based on the route's coordinates.

The destination name is still available through the new destination sensor (`sensor.<vehicle>_destination`), which is disabled by default. Enable it from the entity settings if you have automations that relied on the destination name, and update any automations that matched the old route tracker state.

([@Bre77] - [#172513]) ([Tesla Fleet documentation])

[@Bre77]: https://github.com/Bre77
[#172513]: https://github.com/home-assistant/core/pull/172513
[Tesla Fleet documentation]: /integrations/tesla_fleet/

{% enddetails %}

{% details "Teslemetry" %}

The route device tracker no longer reports the active route's destination as its state or through a `location_name` attribute. Its state is now derived purely from the route's coordinates (zone-aware, like `home` or `not_home`).

If you relied on the destination name, enable the new **Destination** sensor (`sensor.*_destination`), which is disabled by default and reports the destination name as Tesla provides it.

([@Bre77] - [#172514]) ([Teslemetry documentation])

[#172514]: https://github.com/home-assistant/core/pull/172514
[Teslemetry documentation]: /integrations/teslemetry/

{% enddetails %}

{% details "Tractive" %}

The `battery_level` attribute has been removed from Tractive device tracker entities. Use the dedicated battery sensor in your automations and scripts instead.

([@bieniu] - [#172756]) ([Tractive documentation])

[@bieniu]: https://github.com/bieniu
[#172756]: https://github.com/home-assistant/core/pull/172756
[Tractive documentation]: /integrations/tractive/

{% enddetails %}

{% details "Zeroconf" %}

The legacy `requires_api_password` field has been removed from the Home Assistant zeroconf/mDNS discovery announcement (`_home-assistant._tcp`). It had been hardcoded to `true` since the `http.api_password` authentication mechanism was removed in Home Assistant 2024.7, so it no longer carried any meaning. The official companion apps already ignore it.

Third-party discovery clients that still read this field need to tolerate its absence.

([@agners] - [#173090]) ([Zeroconf documentation]) ([API documentation])

[@agners]: https://github.com/agners
[#173090]: https://github.com/home-assistant/core/pull/173090
[Zeroconf documentation]: /integrations/zeroconf/
[API documentation]: /integrations/api/

{% enddetails %}

{% details "Zone" %}

The state (person count) and `persons` attribute of zone entities are now calculated from the `in_zones` attribute of person entities. As a result, a person can now be counted in more than one zone at the same time. For example, a person who is `home` with `in_zones: ["home", "near_home"]` now counts toward both `zone.home` and `zone.near_home`, where previously they only counted toward `zone.home`.

In addition, the state of position-aware device trackers is now the smallest zone the device is in, instead of the zone whose center it is closest to.

Automations, scripts, or templates that depend on zone person counts or on device tracker zone states may need to be adjusted.

([@emontnemery] - [#172942], [#173106]) ([Zone documentation])

[#172942]: https://github.com/home-assistant/core/pull/172942
[#173106]: https://github.com/home-assistant/core/pull/173106
[Zone documentation]: /integrations/zone/

{% enddetails %}

{% details "Z-Wave JS" %}

This release requires an updated Z-Wave JS server. You need zwave-js-server 3.9.0 or newer (schema 49):

- If you use the Z-Wave JS app, update it to at least version 1.4.0.
- If you use the Z-Wave JS UI Docker container, update it to at least version 11.19.1.
- If you run your own zwave-js-server, update it to at least version 3.9.0.

([@AlCalzone] - [#173309]) ([Z-Wave JS documentation])

[@AlCalzone]: https://github.com/AlCalzone
[#173309]: https://github.com/home-assistant/core/pull/173309
[Z-Wave JS documentation]: /integrations/zwave_js/

{% enddetails %}

If you are a custom integration developer and want to learn about changes and new features available for your integration: Be sure to follow our [developer blog][devblog]. The following changes are the most notable for this release:

- [Changes to device tracker entity models](https://developers.home-assistant.io/blog/2026/06/15/device-tracker-changes)
- [Frontend component updates in 2026.7](https://developers.home-assistant.io/blog/2026/06/23/frontend-component-updates-2026.7)
- [Introducing new unit enumerators](https://developers.home-assistant.io/blog/2026/06/30/new-unit-enumerators)
- [Deprecation of the `home_assistant_start` flag of `async_initialize_triggers`](https://developers.home-assistant.io/blog/2026/06/30/async-initialize-triggers-home-assistant-start-deprecated)

[devblog]: https://developers.home-assistant.io/blog/
