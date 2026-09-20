# 2026.6: Pick a card, any card — backward-incompatible changes

Fetched from https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-06-03-release-20266.markdown
Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of home-assistant/home-assistant.io.
Modified: this is the *Backward-incompatible changes* section of the post's own source markdown, cut at the surrounding `##` headings by `scripts/fetch_ha_sources.py`. Nothing inside it has been changed, added or reordered; the rest of the post — the feature write-ups and the patch-release changelogs — is not kept.

## Backward-incompatible changes

We do our best to avoid making changes to existing functionality that might unexpectedly impact your Home Assistant installation. Unfortunately, sometimes it is inevitable.

We always make sure to document these changes to make the transition as easy as possible for you. This release has the following backward-incompatible changes:

{% details "Purpose-specific triggers (Labs)" %}

The behavior options for the Labs purpose-specific triggers have been renamed to better match what they do: `any` is now `each`, and `last` is now `all`. The default is now `each`.

If you have automations that use these triggers from the Labs preview at {% my labs title="**Settings** > **System** > **Labs**" %}, open them in the automation editor and re-pick the behavior option. Any YAML you wrote against the old keys needs to be updated to the new names.

([@emontnemery] - [#172348])

[@emontnemery]: https://github.com/emontnemery
[#172348]: https://github.com/home-assistant/core/pull/172348

{% enddetails %}

{% details "Bluetooth" %}

The default Bluetooth scanning mode has changed to Auto, which dynamically switches between active and passive scanning depending on what is happening. This saves around 95-96% of the battery used for Bluetooth scanning while keeping the same functionality for most setups.

If you run into issues after the upgrade, you can switch your Bluetooth adapter back to Active scanning. Go to {% my integrations title="**Settings** > **Devices & services**" %}, open the **Bluetooth** integration, and select **Configure** on your adapter to change the scanning mode.

([@bdraco] - [#171985]) ([Bluetooth documentation])

[@bdraco]: https://github.com/bdraco
[#171985]: https://github.com/home-assistant/core/pull/171985
[Bluetooth documentation]: /integrations/bluetooth/

{% enddetails %}

{% details "Certificate Expiry" %}

The `error` attribute on the certificate expiry sensor now returns a proper `None` value instead of the string `"None"` when there is no error.

If you use this attribute in templates, update your comparisons from `== "None"` to `is none`.

([@TomFilsell] - [#170878]) ([Certificate Expiry documentation])

[@TomFilsell]: https://github.com/TomFilsell
[#170878]: https://github.com/home-assistant/core/pull/170878
[Certificate Expiry documentation]: /integrations/cert_expiry/

{% enddetails %}

{% details "ESPHome" %}

The default Bluetooth proxy scanning mode for ESPHome devices is now Auto. Devices that were previously set to Active are automatically migrated to Auto, while devices set to Passive keep their setting.

If you need Active scanning for a specific device, change it back in the device options under {% my integrations title="**Settings** > **Devices & services**" %}.

([@bdraco] - [#171996]) ([ESPHome documentation])

[#171996]: https://github.com/home-assistant/core/pull/171996
[ESPHome documentation]: /integrations/esphome/

{% enddetails %}

{% details "HDMI-CEC" %}

Calling the `turn_off` action on HDMI-CEC switch or media player entities now sends the standard CEC standby command instead of a vendor-specific power-off command. This works more reliably across devices from different manufacturers.

If you relied on the previous behavior, you can send the original command using the `hdmi_cec.send_command` action with keypress `0x44` followed by `0x6c`.

([@pattyland] - [#170206]) ([HDMI-CEC documentation])

[@pattyland]: https://github.com/pattyland
[#170206]: https://github.com/home-assistant/core/pull/170206
[HDMI-CEC documentation]: /integrations/hdmi_cec/

{% enddetails %}

{% details "IronOS" %}

The uptime sensor for IronOS soldering irons has changed from a duration sensor (reporting seconds) to a timestamp sensor that reports when the device was started.

Update any automations or dashboards that read this sensor to work with the new timestamp format.

([@tr4nt0r] - [#169699]) ([IronOS documentation])

[@tr4nt0r]: https://github.com/tr4nt0r
[#169699]: https://github.com/home-assistant/core/pull/169699
[IronOS documentation]: /integrations/iron_os/

{% enddetails %}

{% details "ONVIF" %}

When you call the `onvif.ptz` action with `continuous_duration: 0`, the integration no longer sends a Stop command after the ContinuousMove. This lets you start a continuous movement and stop it later with a separate call.

If your automations rely on the camera stopping automatically, set `continuous_duration` to the desired duration in seconds.

([@yoxcu] - [#163173]) ([ONVIF documentation])

[@yoxcu]: https://github.com/yoxcu
[#163173]: https://github.com/home-assistant/core/pull/163173
[ONVIF documentation]: /integrations/onvif/

{% enddetails %}

{% details "Shelly" %}

Shelly devices used as Bluetooth scanners now support the new Auto scanning mode. Existing devices set to Active are automatically migrated to Auto for better battery and performance.

You can change the scanning mode back in the device options under {% my integrations title="**Settings** > **Devices & services**" %}.

([@bdraco] - [#172008]) ([Shelly documentation])

[#172008]: https://github.com/home-assistant/core/pull/172008
[Shelly documentation]: /integrations/shelly/

{% enddetails %}

{% details "SmartThings" %}

The `source` attribute on SmartThings media players is now normalized to standard Home Assistant values. For example, `D.IN` is now reported as `digital_input` and `BT` as `bluetooth`.

If you use the `source` attribute in automations, dashboards, or templates, update them to match the new values.

([@felipecrs] - [#160034]) ([SmartThings documentation])

[@felipecrs]: https://github.com/felipecrs
[#160034]: https://github.com/home-assistant/core/pull/160034
[SmartThings documentation]: /integrations/smartthings/

{% enddetails %}

{% details "Template entities" %}

The legacy template platform syntax under the individual platform keys has been removed. This syntax was deprecated in Home Assistant 2025.12 and has now reached the end of its 6-month deprecation period.

This affects the following platforms:

- `alarm_control_panel`
- `binary_sensor`
- `cover`
- `fan`
- `light`
- `lock`
- `sensor`
- `switch`
- `vacuum`
- `weather`

Move your template entities to the modern `template:` syntax. A step-by-step migration guide is available in the [Removal of legacy template entities](https://community.home-assistant.io/t/removal-of-legacy-template-entities-in-2026-6/1011847) forum thread.

([@Petro31] - [#169608], [#169610], [#169611], [#169613], [#169615], [#169725], [#169728], [#169730], [#169732], [#169734]) ([Template documentation])

[@Petro31]: https://github.com/Petro31
[#169608]: https://github.com/home-assistant/core/pull/169608
[#169610]: https://github.com/home-assistant/core/pull/169610
[#169611]: https://github.com/home-assistant/core/pull/169611
[#169613]: https://github.com/home-assistant/core/pull/169613
[#169615]: https://github.com/home-assistant/core/pull/169615
[#169725]: https://github.com/home-assistant/core/pull/169725
[#169728]: https://github.com/home-assistant/core/pull/169728
[#169730]: https://github.com/home-assistant/core/pull/169730
[#169732]: https://github.com/home-assistant/core/pull/169732
[#169734]: https://github.com/home-assistant/core/pull/169734
[Template documentation]: /integrations/template/

{% enddetails %}

{% details "Tuya" %}

The unit of measurement provided by the Tuya API now takes precedence over the default unit assigned by Home Assistant. This makes the reported value match what the Tuya app shows.

If your device reports an invalid or unexpected unit, please submit a bug report with the device details and the unit it reports and adjust it accordingly.

([@epenet] - [#170338]) ([Tuya documentation])

[@epenet]: https://github.com/epenet
[#170338]: https://github.com/home-assistant/core/pull/170338
[Tuya documentation]: /integrations/tuya/

{% enddetails %}

{% details "Velux" %}

The deprecated `velux.reboot_gateway` action has been removed. Use the reboot button entity on your Velux gateway instead.

([@wollew] - [#169796]) ([Velux documentation])

[@wollew]: https://github.com/wollew
[#169796]: https://github.com/home-assistant/core/pull/169796
[Velux documentation]: /integrations/velux/

{% enddetails %}

If you are a custom integration developer and want to learn about changes and new features available for your integration: Be sure to follow our [developer blog][devblog]. The following changes are the most notable for this release:

- [BrowseMediaSource: domain is now required](https://developers.home-assistant.io/blog/2026/05/20/browse-media-source-root-class)
- [Changes to the condition and script APIs](https://developers.home-assistant.io/blog/2026/05/13/condition-script-api-changes)
- [Custom card suggestions in the card picker](https://developers.home-assistant.io/blog/2026/05/27/custom-card-suggestions)
- [Deprecating config entry listener with reloading methods in config flow](https://developers.home-assistant.io/blog/2026/05/07/config-entry-listener-together-with-reloading-methods)
- [Deprecation of advanced mode in data entry flow](https://developers.home-assistant.io/blog/2026/05/26/advanced-mode-config-flow-deprecation)
- [Format entity names in custom cards](https://developers.home-assistant.io/blog/2026/05/11/format-entity-name-helper)
- [Frontend component updates in 2026.6](https://developers.home-assistant.io/blog/2026/05/27/frontend-component-updates-2026.6)
- [MQTT publish API changes](https://developers.home-assistant.io/blog/2026/05/11/mqtt-publish-api-changes)
- [MQTT publish API supports message expiry interval](https://developers.home-assistant.io/blog/2026/05/11/mqtt-publish-api-message-expiry-interval)

[devblog]: https://developers.home-assistant.io/blog/
