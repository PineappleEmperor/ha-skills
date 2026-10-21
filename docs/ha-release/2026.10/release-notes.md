# 2026.10: You are here 📍 — backward-incompatible changes

Fetched from https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-10-07-release-202610.markdown
Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of home-assistant/home-assistant.io.
Modified: this is the *Backward-incompatible changes* section of the post's own source markdown, cut at the surrounding `##` headings by `scripts/fetch_ha_sources.py`. Nothing inside it has been changed, added or reordered; the rest of the post — the feature write-ups and the patch-release changelogs — is not kept.

## Backward-incompatible changes

We do our best to avoid making changes to existing functionality that might unexpectedly impact your Home Assistant installation. Unfortunately, sometimes it is inevitable.

We always make sure to document these changes to make the transition as easy as possible for you. This release has the following backward-incompatible changes:

{% details "Authentication" %}

The deprecated legacy mode of the Home Assistant authentication provider has been removed. Usernames are now always handled in their normalized form: lowercase, and without spaces at the start or end. If Home Assistant showed you a repair about usernames that are not normalized, change those usernames to match.

([@gjohansson-ST] - [#175613]) ([Authentication documentation])

[@gjohansson-ST]: https://github.com/gjohansson-ST
[#175613]: https://github.com/home-assistant/core/pull/175613
[Authentication documentation]: /docs/authentication/providers/

{% enddetails %}

{% details "easyEnergy" %}

The `hours_priced_equal_or_lower` and `hours_priced_equal_or_higher` sensors are now named **Periods priced equal or lower** and **Periods priced equal or higher**, and no longer have `h` as their unit of measurement. Their values count price periods, not hours.

If you have {% term "template" "templates" %} or dashboard cards that rely on the unit of these sensors, update them to handle a count without a unit. The values, entity IDs, and unique IDs are unchanged, so {% term automations %} that only compare the numbers need no changes.

([@klaasnicolaas] - [#181431]) ([easyEnergy documentation])

[@klaasnicolaas]: https://github.com/klaasnicolaas
[#181431]: https://github.com/home-assistant/core/pull/181431
[easyEnergy documentation]: /integrations/easyenergy/

{% enddetails %}

{% details "EnergyFlip" %}

EnergyFlip shut down the API version the integration used, so the integration has moved to the new version. The new API no longer provides the additional electricity measurements, so only the current power sensor remains for electricity.

([@DieEneSchrodinger] - [#179723]) ([EnergyFlip documentation])

[@DieEneSchrodinger]: https://github.com/DieEneSchrodinger
[#179723]: https://github.com/home-assistant/core/pull/179723
[EnergyFlip documentation]: /integrations/huisbaasje/

{% enddetails %}

{% details "EnergyZero" %}

The `hours_priced_equal_or_lower` electricity sensor is now named **Periods priced equal or lower**, and no longer has `h` as its unit of measurement. Its value counts price periods, not hours.

If you have {% term "template" "templates" %} or dashboard cards that rely on the unit of this sensor, update them to handle a count without a unit. The value, entity ID, and unique ID are unchanged, so {% term automations %} that only compare the number need no changes.

([@klaasnicolaas] - [#181492]) ([EnergyZero documentation])

[#181492]: https://github.com/home-assistant/core/pull/181492
[EnergyZero documentation]: /integrations/energyzero/

{% enddetails %}

{% details "Google Sheets" %}

Reading an empty worksheet now returns `{"range": [[]]}` instead of `{"range": []}`. If you have {% term automations %}, {% term scripts %}, or {% term "template" "templates" %} that check for an empty worksheet, update them to match.

([@JamieMagee] - [#181692]) ([Google Sheets documentation])

[@JamieMagee]: https://github.com/JamieMagee
[#181692]: https://github.com/home-assistant/core/pull/181692
[Google Sheets documentation]: /integrations/google_sheets/

{% enddetails %}

{% details "Google Wifi" %}

The uptime sensor is deprecated and will be removed in a future release. Use the new last restart sensor instead.

([@EReaso] - [#177525]) ([Google Wifi documentation])

[@EReaso]: https://github.com/EReaso
[#177525]: https://github.com/home-assistant/core/pull/177525
[Google Wifi documentation]: /integrations/google_wifi/

{% enddetails %}

{% details "IoTaWatt" %}

Reactive power sensors now use the reactive power device class, which changes their unit of measurement from `VAR` to `var`. You have these sensors if an output on your IoTaWatt is configured with the unit `VAR`.

If such a sensor has recorded {% term "long-term statistics" %}, Home Assistant creates a repair about the changed unit after the update. Pick the offered option to update the statistics to the new unit. No data is lost. In return, these sensors are now shown as reactive power, and you can display them in `mvar`, `var`, or `kvar`.

([@agners] - [#180913]) ([IoTaWatt documentation])

[@agners]: https://github.com/agners
[#180913]: https://github.com/home-assistant/core/pull/180913
[IoTaWatt documentation]: /integrations/iotawatt/

{% enddetails %}

{% details "Libre Hardware Monitor" %}

Libre Hardware Monitor versions older than 0.9.5 are no longer supported. If you run an older version, update Libre Hardware Monitor to keep using the integration.

([@Sab44] - [#181928]) ([Libre Hardware Monitor documentation])

[@Sab44]: https://github.com/Sab44
[#181928]: https://github.com/home-assistant/core/pull/181928
[Libre Hardware Monitor documentation]: /integrations/libre_hardware_monitor/

{% enddetails %}

{% details "Linode and Tank Utility" %}

The Linode and Tank Utility {% term integrations %} have been disabled and no longer start.

Both depend on Python libraries that have not been maintained for years (the Linode one was last updated in 2018, the Tank Utility one in 2023) and no longer work with current Python packaging tools. Keeping them running meant holding back those tools for every other integration, so they have been switched off instead.

If you use either integration, you can remove it from your configuration. If the underlying libraries are updated, or replaced with maintained alternatives, the integrations can be activated again. Community contributions to make this happen are very welcome.

([@frenck] - [#182842]) ([Linode documentation]) ([Tank Utility documentation])

[#182842]: https://github.com/home-assistant/core/pull/182842
[Linode documentation]: /integrations/linode/
[Tank Utility documentation]: /integrations/tank_utility/

{% enddetails %}

{% details "Mealie" %}

Mealie 3.2 or newer is now required. Version 3.2 was released in September 2025, and the Mealie {% term app %} and official container are already well past it, so most of you don't need to do anything. If your Mealie server runs an older version, update it before you update Home Assistant.

([@andrew-codechimp] - [#180609]) ([Mealie documentation])

[@andrew-codechimp]: https://github.com/andrew-codechimp
[#180609]: https://github.com/home-assistant/core/pull/180609
[Mealie documentation]: /integrations/mealie/

{% enddetails %}

{% details "MQTT" %}

The `mqtt.publish` and `mqtt.dump` actions now require an administrator account, just like `mqtt.reload` already did.

{% term Automations %}, {% term scripts %}, and {% term scenes %} that publish on their own are not affected, because they run without a user context. What changes is a call a non-admin user makes themselves: from a dashboard button, from the developer tools, or by starting a script or automation by hand. Those now fail with "Unauthorized". If a non-admin user needs to be able to publish, let the automation run on its own trigger instead of having that user start it.

([@frenck] - [#182045]) ([MQTT documentation])

[#182045]: https://github.com/home-assistant/core/pull/182045
[MQTT documentation]: /integrations/mqtt/

{% enddetails %}

{% details "OpenEVSE" %}

The **Charging status** sensor now reports a fixed set of states in snake_case, such as `charging`, `not_connected`, and `gfci_self_test_failure`, instead of the raw values from the charger, such as `Charging` or `not connected`. If you have {% term automations %} or {% term scripts %} that check for the old values, update them to match the new ones.

([@firstof9] - [#180329]) ([OpenEVSE documentation])

[@firstof9]: https://github.com/firstof9
[#180329]: https://github.com/home-assistant/core/pull/180329
[OpenEVSE documentation]: /integrations/openevse/

{% enddetails %}

{% details "Proxmox VE" %}

The **Uptime** sensor of nodes, virtual machines, and containers now shows a timestamp of when it started, instead of the time since it started in seconds. If you have {% term automations %}, {% term scripts %}, or {% term "template" "templates" %} that use the number of seconds, update them to work with the timestamp.

([@erwindouna] - [#169704]) ([Proxmox VE documentation])

[#169704]: https://github.com/home-assistant/core/pull/169704
[Proxmox VE documentation]: /integrations/proxmoxve/

{% enddetails %}

{% details "Rejseplanen" %}

Rejseplanen now uses version 2.0 of the Rejseplanen API, which requires an API key. You can [apply for an API key](https://labs.rejseplanen.dk/hc/en-us/articles/21553113674909-Adgang-til-data-fra-Labs) with Rejseplanen Labs. The integration is now set up from the UI instead of {% term YAML %}.

All extra attributes have been removed from the sensors. If you have {% term "template" "templates" %} or dashboard cards that use them, you need to update them.

([@Jawar19] - [#152200]) ([Rejseplanen documentation])

[#152200]: https://github.com/home-assistant/core/pull/152200
[Rejseplanen documentation]: /integrations/rejseplanen/

{% enddetails %}

{% details "Sofar" %}

Sofar inverters that report no energy meter no longer get these six energy sensors: **Load consumption today**, **Load consumption total**, **Import energy today**, **Import energy total**, **Export energy today**, and **Export energy total**.

They never held real readings on those inverters. The inverter itself marks those values as invalid, and on a <abbr title="photovoltaic">PV</abbr>-only inverter, **Load consumption total** simply repeated the solar generation total. If you used these sensors on your Energy dashboard, or in {% term "template" "templates" %} or {% term automations %}, remove them. Hybrid inverters and PV inverters with a meter keep all six.

([@darkrain-nl] - [#181729]) ([Sofar documentation])

[@darkrain-nl]: https://github.com/darkrain-nl
[#181729]: https://github.com/home-assistant/core/pull/181729
[Sofar documentation]: /integrations/sofar/

{% enddetails %}

{% details "State conditions" %}

State {% term conditions %} that combine the `for` option with a state attribute, a list of states, or a state taken from another entity now fail validation. These combinations don't support a duration, so you get an error when the configuration is checked, instead of a condition that doesn't do what you expect.

([@emontnemery] - [#174083])

[@emontnemery]: https://github.com/emontnemery
[#174083]: https://github.com/home-assistant/core/pull/174083

{% enddetails %}

{% details "Synology DSM" %}

The `synology_dsm.reboot` and `synology_dsm.shutdown` actions now require an administrator account.

{% term Automations %} and {% term scripts %} that run on their own triggers are not affected, because they run without a user context. What changes is a call a non-admin user makes themselves: from a dashboard button, from the developer tools, or by starting a script or automation by hand. Those now fail with "Unauthorized". If a non-admin user needs to be able to restart or shut down the NAS, let the automation run on its own trigger instead of having that user start it.

([@frenck] - [#182050]) ([Synology DSM documentation])

[#182050]: https://github.com/home-assistant/core/pull/182050
[Synology DSM documentation]: /integrations/synology_dsm/

{% enddetails %}

{% details "Telegram bot" %}

When you pass a `directory_path` to the `telegram_bot.download_file` action, that directory now has to be in your `allowlist_external_dirs`. If the action starts failing, add the directory to your configuration:

```yaml
homeassistant:
  allowlist_external_dirs:
    - /media/telegram
```

If you leave out `directory_path`, nothing changes. Files are still saved to the `telegram_bot` folder in your configuration directory, without an allowlist entry.

([@frenck] - [#182460]) ([Telegram bot documentation])

[#182460]: https://github.com/home-assistant/core/pull/182460
[Telegram bot documentation]: /integrations/telegram_bot/

{% enddetails %}

{% details "Teslemetry" %}

Vehicles that stream their data no longer get the {% term entities %} that can only be updated by {% term polling %}. Updating those required a paid API call, which most people did not expect.

([@Bre77] - [#181351]) ([Teslemetry documentation])

[@Bre77]: https://github.com/Bre77
[#181351]: https://github.com/home-assistant/core/pull/181351
[Teslemetry documentation]: /integrations/teslemetry/

{% enddetails %}

{% details "UniFi Network" %}

You can no longer reconfigure the UniFi Network {% term integration %} by adding the same site again through **Add integration**. Use the dedicated **Reconfigure** option of the integration instead.

([@robinsiep] - [#182201]) ([UniFi Network documentation])

[@robinsiep]: https://github.com/robinsiep
[#182201]: https://github.com/home-assistant/core/pull/182201
[UniFi Network documentation]: /integrations/unifi/

{% enddetails %}

{% details "UpCloud" %}

The option to configure the {% term polling %} interval has been removed from UpCloud. The integration now always polls every 60 seconds. If you had set a longer interval, this means more API calls: a 300 second interval, for example, becomes five times as many calls.

If you need a different update frequency, you can [set your own polling interval](/common-tasks/general/#defining-a-custom-polling-interval).

([@KingLizard1020] - [#181327]) ([UpCloud documentation])

[@KingLizard1020]: https://github.com/KingLizard1020
[#181327]: https://github.com/home-assistant/core/pull/181327
[UpCloud documentation]: /integrations/upcloud/

{% enddetails %}

{% details "Xbox" %}

The **Subscribed to Xbox Game Pass** {% term "binary sensor" %} has been removed, because it never worked. The Xbox API always reported `false`, whether you or your friends were subscribed to Game Pass or not.

([@tr4nt0r] - [#182734]) ([Xbox documentation])

[#182734]: https://github.com/home-assistant/core/pull/182734
[Xbox documentation]: /integrations/xbox/

{% enddetails %}

If you are a custom integration developer and want to learn about changes and new features available for your integration: Be sure to follow our [developer blog][devblog]. The following changes are the most notable for this release:

- [`DeviceEntry.config_entries` deprecation is now enforced](https://developers.home-assistant.io/blog/2026/09/15/device-entry-config-entries-deprecation)
- [Deprecating `modbus.get_hub` in favor of `async_get_unit`](https://developers.home-assistant.io/blog/2026/09/02/modbus-get-hub-deprecation)
- [LLM tools return a ToolResult and declare their integration](https://developers.home-assistant.io/blog/2026/09/26/llm-tool-result)
- [New device and state class selectors](https://developers.home-assistant.io/blog/2026/09/04/device-and-state-class-selectors)
- [New stop action and idle activity for lawn mowers](https://developers.home-assistant.io/blog/2026/09/11/lawn-mower-stop-action-idle-activity)
- [OAuth2 error handling moved into the helper](https://developers.home-assistant.io/blog/2026/09/07/oauth2-central-error-handling)
- [Probatio is our validation engine](https://developers.home-assistant.io/blog/2026/09/30/probatio-validation-engine)
- [Shared config flow abort reasons are translated centrally](https://developers.home-assistant.io/blog/2026/09/28/central-config-flow-abort-reasons)
- [Use Config Entry exceptions in integration migration method](https://developers.home-assistant.io/blog/2026/09/17/Use-config-entry-exc-in-migration)

[devblog]: https://developers.home-assistant.io/blog/
