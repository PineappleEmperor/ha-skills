# 2026.8: Approachable by design — backward-incompatible changes

Fetched from https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-08-05-release-20268.markdown
Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of home-assistant/home-assistant.io.
Modified: this is the *Backward-incompatible changes* section of the post's own source markdown, cut at the surrounding `##` headings by `scripts/fetch_ha_sources.py`. Nothing inside it has been changed, added or reordered; the rest of the post — the feature write-ups and the patch-release changelogs — is not kept.

## Backward-incompatible changes

We do our best to avoid making changes to existing functionality that might unexpectedly impact your Home Assistant installation. Unfortunately, sometimes it is inevitable.

We always make sure to document these changes to make the transition as easy as possible for you. This release has the following backward-incompatible changes:

{% details "AirNow" %}

The station radius option has been removed. The 2026 AirNow API no longer uses a distance parameter, so the radius had no effect on which reporting station was used. Existing entries are updated automatically, and any radius you had set is discarded. No action is needed.

([@derekcentrico] - [#176740]) ([AirNow documentation])

[@derekcentrico]: https://github.com/derekcentrico
[#176740]: https://github.com/home-assistant/core/pull/176740
[AirNow documentation]: /integrations/airnow/

{% enddetails %}

{% details "Gardena Bluetooth" %}

The valve's `activation_reason` sensor now reports a fixed set of values instead of free-form text. If you have {% term automations %}, {% term scripts %}, or {% term "template" "templates" %} that match on the old text values, update them to match the new ones.

([@elupus] - [#177187])

[@elupus]: https://github.com/elupus
[#177187]: https://github.com/home-assistant/core/pull/177187

{% enddetails %}

{% details "Edifier Infrared" %}

If you set up the Edifier Infrared integration for the R2000DB or R2730DB speakers, some buttons were mapped to the wrong infrared codes (on the R2730DB, power and mute were swapped). The mappings are now corrected and migrated automatically. If you built {% term automations %} or {% term scripts %} around the old, incorrect buttons, update them to match.

([@abmantis] - [#177472]) ([Edifier Infrared documentation])

[#177472]: https://github.com/home-assistant/core/pull/177472
[Edifier Infrared documentation]: /integrations/edifier_infrared/

{% enddetails %}

{% details "Ohme" %}

The Ohme energy sensor has been removed. It reported an estimate of the energy stored in the car's battery rather than the energy delivered by the charger, which caused confusing jumps in the energy dashboard, and the vendor's API no longer provides a useful value.

If you tracked this sensor, use an [Integration - Riemann sum](/integrations/integration/) {% term helper %} on a power sensor to estimate the energy instead.

([@dan-r] - [#174664]) ([Ohme documentation])

[@dan-r]: https://github.com/dan-r
[#174664]: https://github.com/home-assistant/core/pull/174664
[Ohme documentation]: /integrations/ohme/

{% enddetails %}

{% details "Paperless-ngx" %}

Paperless-ngx now requires a newer version of your Paperless-ngx server. The minimum supported server version is raised to 2.19, which also restores compatibility with Paperless-ngx 3.0. If your Paperless-ngx server is on version 2.18 or older, update it before you update Home Assistant.

([@IngmarStein] - [#176889]) ([Paperless-ngx documentation])

[@IngmarStein]: https://github.com/IngmarStein
[#176889]: https://github.com/home-assistant/core/pull/176889
[Paperless-ngx documentation]: /integrations/paperless_ngx/

{% enddetails %}

{% details "Robot vacuums" %}

The deprecated `battery_level` property has been removed from the vacuum {% term entities %} of several integrations. If you use a robot vacuum's battery level in an {% term automation %}, {% term script %}, or on a dashboard, use the vacuum's battery sensor instead.

This affects the following integrations:

- [LG ThinQ]
- [Neato]
- [Romy]
- [Shark IQ]
- [SwitchBot Cloud]
- [Template]
- [TP-Link]
- [Xiaomi Miio]

([@gjohansson-ST] - [#175681], [#175684], [#175685], [#175686], [#175687], [#175688], [#175691], [#175764])

[@gjohansson-ST]: https://github.com/gjohansson-ST
[#175681]: https://github.com/home-assistant/core/pull/175681
[#175684]: https://github.com/home-assistant/core/pull/175684
[#175685]: https://github.com/home-assistant/core/pull/175685
[#175686]: https://github.com/home-assistant/core/pull/175686
[#175687]: https://github.com/home-assistant/core/pull/175687
[#175688]: https://github.com/home-assistant/core/pull/175688
[#175691]: https://github.com/home-assistant/core/pull/175691
[#175764]: https://github.com/home-assistant/core/pull/175764
[LG ThinQ]: /integrations/lg_thinq/
[Neato]: /integrations/neato/
[Romy]: /integrations/romy/
[Shark IQ]: /integrations/sharkiq/
[SwitchBot Cloud]: /integrations/switchbot_cloud/
[Template]: /integrations/template/
[TP-Link]: /integrations/tplink/
[Xiaomi Miio]: /integrations/xiaomi_miio/

{% enddetails %}

{% details "ScreenLogic" %}

The option to configure the {% term polling %} interval has been removed from ScreenLogic. Home Assistant now polls the integration at a fixed interval. If you need a different update frequency, you can [set your own polling interval](/common-tasks/general/#defining-a-custom-polling-interval) or trigger an update with the `homeassistant.update_entity` action.

([@Pinball3D] - [#175576]) ([ScreenLogic documentation])

[@Pinball3D]: https://github.com/Pinball3D
[#175576]: https://github.com/home-assistant/core/pull/175576
[ScreenLogic documentation]: /integrations/screenlogic/

{% enddetails %}

{% details "UniFi Protect" %}

Support for UniFi Protect AI Port devices has been removed. These devices only ever exposed diagnostic sensors, all disabled by default, and are not part of the UniFi Protect public API the integration is moving to. The AI Port device and its sensors are removed automatically when you update. You can still configure the AI Port directly in UniFi Protect.

([@RaHehl] - [#174378]) ([UniFi Protect documentation])

Detection scores are no longer available. The detection binary sensors (motion, person, vehicle, animal, and the smart-audio alarm sensors) now take their state from the UniFi Protect public API, which carries no per-event score, so their `event_score` attribute is gone and automations that filter on it need another condition. The event id and the detected types moved to the new **Motion detection**, **Smart detection**, and **Sound detection** event entities.

([@RaHehl] - [#174948]) ([UniFi Protect documentation])

UniFi Protect 7.1 or newer is now required. On an older console the integration reports that the version is too old instead of setting up. Update UniFi Protect to 7.1 or newer to keep using it.

([@RaHehl] - [#177620]) ([UniFi Protect documentation])

[@RaHehl]: https://github.com/RaHehl
[#174378]: https://github.com/home-assistant/core/pull/174378
[#174948]: https://github.com/home-assistant/core/pull/174948
[#177620]: https://github.com/home-assistant/core/pull/177620
[UniFi Protect documentation]: /integrations/unifiprotect/

{% enddetails %}

{% details "Volvo On Call" %}

The Volvo On Call integration has been removed. If you have a supported Volvo, set up the newer [Volvo](/integrations/volvo/) integration instead.

([@gjohansson-ST] - [#175677])

[#175677]: https://github.com/home-assistant/core/pull/175677

{% enddetails %}

If you are a custom integration developer and want to learn about changes and new features available for your integration: Be sure to follow our [developer blog][devblog]. The following changes are the most notable for this release:

- [Devices are restricted to a single config entry and at most one subentry](https://developers.home-assistant.io/blog/2026/07/21/device-registry-single-config-entry)
- [Introducing the Open Home Foundation AI Policy](https://developers.home-assistant.io/blog/2026/07/20/ai-policy)
- [Media sources can now be searched](https://developers.home-assistant.io/blog/2026/07/03/media-source-search)
- [Modernizing Modbus in Home Assistant](https://developers.home-assistant.io/blog/2026/07/05/modernizing-modbus)
- [Standard event types for button event entities](https://developers.home-assistant.io/blog/2026/07/22/button-standard-event-types)

[devblog]: https://developers.home-assistant.io/blog/
