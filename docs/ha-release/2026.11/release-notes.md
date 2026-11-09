# 2026.11: A lot in store! — backward-incompatible changes

Fetched from https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-11-04-release-202611.markdown
Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of home-assistant/home-assistant.io.
Modified: this is the *Backward-incompatible changes* section of the post's own source markdown, cut at the surrounding `##` headings by `scripts/fetch_ha_sources.py`. Nothing inside it has been changed, added or reordered; the rest of the post — the feature write-ups and the patch-release changelogs — is not kept.

## Backward-incompatible changes

We do our best to avoid making changes to existing functionality that might unexpectedly impact your Home Assistant installation. Unfortunately, sometimes it is inevitable.

We always make sure to document these changes to make the transition as easy as possible for you. This release has the following backward-incompatible changes:

{% details "AdGuard Home" %}

The **Query log** switch of the AdGuard Home integration now requires AdGuard Home v0.107.30 or newer. On older versions, the switch becomes unavailable.

If AdGuard Home forces HTTPS while the integration is set up without SSL, setup now fails instead of following the redirect to HTTPS. To fix this, remove the integration and add it again with SSL enabled.

([@frenck] - [#184349]) ([AdGuard Home documentation])

[#184349]: https://github.com/home-assistant/core/pull/184349
[AdGuard Home documentation]: /integrations/adguard/

{% enddetails %}

{% details "Alert card" %}

The Alert card now shows its color and its pulse only while the {% term entity %} is in an alert state, and it supports alarm control panel, binary sensor, cover, and lock entities. The `color` option is renamed to `alert_color`, and a new `clear_color` option sets the color for the rest of the time. Without an `alert_color`, the card is red during an alert. Set `alert_color: none` to leave it uncolored.

The card was made for the home and security dashboards, which are not affected. If you added it to a dashboard in {% term YAML %} yourself, update it to the new options.

([@timmo001] - [frontend#54880])

[frontend#54880]: https://github.com/home-assistant/frontend/pull/54880

{% enddetails %}

{% details "Apple iCloud" %}

Completed reminders are no longer fetched by default. The iCloud integration used to include completed reminders in every Reminders fetch, which on accounts with a very large history could block startup for a long time.

To keep the old behavior, enable **Include completed reminders** during setup or afterward in the integration options under **Settings** > **Devices & services** > **Apple iCloud** > **Options**.

([@timlaing] - [#186175]) ([Apple iCloud documentation])

[@timlaing]: https://github.com/timlaing
[#186175]: https://github.com/home-assistant/core/pull/186175
[Apple iCloud documentation]: /integrations/icloud/

{% enddetails %}

{% details "Auth" %}

When you reach Home Assistant at an IP address that is not on a local network, such as a public address, a global IPv6 address, or a Tailscale address (`100.64.0.0/10`), the address in your browser now has to match the address Home Assistant sees the request coming in on. Scheme, host, and port all have to match. If they do not, logging in fails with "Invalid client id". Previously, such an address was accepted without that check as soon as it had a port, because of a bug in the check.

Most setups are not affected. Opening Home Assistant directly at such an address keeps working, and so does a reverse proxy that you have set up as a trusted proxy in the [HTTP](/integrations/http/) integration, because Home Assistant then uses the forwarded scheme and host. Domain names and local network IP addresses are accepted the same way as before.

If you do run into "Invalid client id", add your proxy to the trusted proxies of the [HTTP](/integrations/http/) integration, or reach Home Assistant through a domain name.

([@elupus] - [#186537]) ([@elupus] - [#186543]) ([Auth documentation])

[#186537]: https://github.com/home-assistant/core/pull/186537
[#186543]: https://github.com/home-assistant/core/pull/186543
[Auth documentation]: /integrations/auth/

{% enddetails %}

{% details "Besen" %}

The Besen **Charging status** sensor now reports `scheduled` instead of `canceled` while a scheduled start is pending. Update {% term automations %}, {% term scripts %}, and {% term templates %} that check for `canceled` to use `scheduled`. The old name incorrectly described a pending reservation as canceled.

([@moryoav] - [#186968]) ([Besen documentation])

[@moryoav]: https://github.com/moryoav
[#186968]: https://github.com/home-assistant/core/pull/186968
[Besen documentation]: /integrations/besen/

{% enddetails %}

{% details "Bitcoin" %}

If you set Bitcoin up in {% term "`configuration.yaml`" %}, setup now moves to the UI. On the first restart after this update, Home Assistant reads the `currency` from your YAML and creates the integration for you. Your sensors keep the names and entity IDs they had.

The `display_options` option is no longer supported, so all 21 sensors are created, even if you previously selected only some of them. This does not add API requests, because all sensors use the same two calls.

Entity IDs created with `entity_namespace` are not preserved. For example, `sensor.wallet_exchange_rate_1_btc` becomes `sensor.exchange_rate_1_btc`.

([@Nihvel] - [#180515]) ([Bitcoin documentation])

[#180515]: https://github.com/home-assistant/core/pull/180515
[Bitcoin documentation]: /integrations/bitcoin/

{% enddetails %}

{% details "Bluesound" %}

The deprecated `bluesound.join` and `bluesound.unjoin` {% term actions %} have been removed. Update {% term automations %} and {% term scripts %} to use `media_player.join` and `media_player.unjoin`.

([@LouisChrist] - [#184755]) ([Bluesound documentation])

[@LouisChrist]: https://github.com/LouisChrist
[#184755]: https://github.com/home-assistant/core/pull/184755
[Bluesound documentation]: /integrations/bluesound/

{% enddetails %}

{% details "Calendar and Sun" %}

Sun {% term triggers %} (`sun.*`) and the `calendar.event_started` and `calendar.event_ended` triggers used to default to `offset_type: before`, so a positive `offset` fired before the event. The sign of the offset now decides instead: negative fires before the event, positive fires after. If you wrote one of these triggers in {% term YAML %} with an `offset` but without `offset_type`, flip the sign of the offset.

This is an edge case: the UI always wrote `offset_type`, so triggers created in the UI are not affected.

([@piitaya] - [#184855]) ([Calendar documentation]) ([Sun documentation])

[@piitaya]: https://github.com/piitaya
[#184855]: https://github.com/home-assistant/core/pull/184855
[Calendar documentation]: /integrations/calendar/
[Sun documentation]: /integrations/sun/

{% enddetails %}

{% details "Control4" %}

The Control4 integration no longer lets you set the {% term polling %} interval in its options. The integration now always polls the controller every 5 seconds, which was already the default. If you had set a different interval, it is no longer used.

If you need a different polling interval, you can disable polling for the integration in its system options and create an automation that calls the `homeassistant.update_entity` action on your own schedule.

([@gjohansson-ST] - [#185879]) ([Control4 documentation])

[#185879]: https://github.com/home-assistant/core/pull/185879
[Control4 documentation]: /integrations/control4/

{% enddetails %}

{% details "Device tracker" %}

Device trackers from integrations that scan your network, such as FRITZ!Box Tools, UniFi Network, NETGEAR, and Nmap Tracker, now always have a {% term device %}. If you renamed one of these tracker entities, its name now starts with the device name.

New trackers from these integrations are now always added disabled. Before, they were enabled when another integration already knew the MAC address of the device. Existing trackers keep their enabled or disabled state.

([@emontnemery] - [#188883]) ([Device tracker documentation])

[#188883]: https://github.com/home-assistant/core/pull/188883
[Device tracker documentation]: /integrations/device_tracker/

{% enddetails %}

{% details "DoorBird" %}

DoorBird events now include the matching image entity as `entity_id`: the last ring image for doorbell events, and the last motion image for motion events. Previously, every event included `camera.<name>_last_motion`. Other events no longer include an entity. If an automation uses the `entity_id` from a DoorBird event, update it to the image entity.

([@mattias-arrelid] - [#186147]) ([DoorBird documentation])

[@mattias-arrelid]: https://github.com/mattias-arrelid
[#186147]: https://github.com/home-assistant/core/pull/186147
[DoorBird documentation]: /integrations/doorbird/

{% enddetails %}

{% details "Electra Smart" %}

`climate.turn_on` on Electra Smart now resumes the mode the air conditioner was last running in, instead of always switching it to heat.

If you relied on `turn_on` selecting heat mode, select it explicitly with `climate.set_hvac_mode` instead.

For units that don't report a previous mode, `turn_on` falls back to cooling rather than heat.

([@noamokman] - [#184595]) ([Electra Smart documentation])

[@noamokman]: https://github.com/noamokman
[#184595]: https://github.com/home-assistant/core/pull/184595
[Electra Smart documentation]: /integrations/electrasmart/

{% enddetails %}

{% details "Entity names" %}

Entity names are now composed from the entity name and its context, which is usually the name of its device. Names you gave an entity yourself are migrated and follow the same rules. Where the full name of an entity changes because of this, the old name is kept as an alias for your voice assistants, and in the `friendly_name` attribute until the name is changed.

Cards, badges, and rows on dashboards that don't have a name set now show the device name followed by the entity name, instead of the friendly name. For example, an entity you named "Off-peak consumption" on the "Power meter" device now shows as "Power meter Off-peak consumption". To keep a short name, rename the device and turn on **Main entity of the device** for the entity, or set a name on the card.

Using custom cards? We worked with the creators of dozens of popular custom cards and sent them updates, so they show names the same way as the built-in cards. Many have already added them, so update your custom cards first. If a card still shows a name you don't expect, set a name in the card, or let its creator know. <!-- TODO before final: check the custom card PRs in frontend#51686 and update this if more (or all) are merged -->

Entity IDs, automations, and scripts are not affected. In {% term templates %}, use `entity_name()`, `device_name()`, and `area_name()` instead of the `friendly_name` attribute, which is going to be deprecated.

([@arturpragacz] - [#184340]) ([@arturpragacz] - [#184341]) ([@piitaya] - [frontend#54725])

[#184340]: https://github.com/home-assistant/core/pull/184340
[#184341]: https://github.com/home-assistant/core/pull/184341
[frontend#54725]: https://github.com/home-assistant/frontend/pull/54725

{% enddetails %}

{% details "Flow-it" %}

The Flow-it {% term integration %} is now called **AriaQ**, because the manufacturer is bringing its products together under that brand. Your {% term devices %} and {% term entities %} keep working and keep their IDs. Only the name you see in Home Assistant changes.

([@albertogeniola] - [#187082]) ([AriaQ documentation])

[@albertogeniola]: https://github.com/albertogeniola
[#187082]: https://github.com/home-assistant/core/pull/187082
[AriaQ documentation]: /integrations/flow_it/

{% enddetails %}

{% details "Frontend" %}

The Home Assistant frontend now requires Chrome 67, Safari 15.4 (iOS and iPadOS 15.4), or Firefox 98 or newer. An older browser now shows a message on the launch screen instead of loading forever.

The new requirements affect the following devices and browsers:

- iPad Air 1, iPad mini 2, iPad mini 3, iPhone 5s, iPhone 6, iPhone 6 Plus, and iPod touch 6, which can't be updated past iOS 12 and can no longer open Home Assistant in a browser or the Home Assistant app.
- Safari on Macs that can't run macOS 10.15 Catalina or newer, as Safari 15.4 needs Catalina. You can still open Home Assistant with Chrome or Firefox if it meets the minimum browser version listed above.
- Fire tablets that still use Amazon WebView 59: the 2015 and 2016 Fire 7, Fire HD 8, and Fire HD 10 on Fire OS 5, and any Fire tablet on Fire OS 6.3.0.1. This includes kiosk browsers such as Fully Kiosk, which use the same WebView. Tablets on Fire OS 5.6.4 or newer (2017 models), Fire OS 6.3.1.2 or newer, or Fire OS 7 keep working, so check for a Fire OS update first.

The first generation Chromecast is not affected.

([@maartenla] - [frontend#55138]) ([Frontend documentation])

[@maartenla]: https://github.com/maartenla
[frontend#55138]: https://github.com/home-assistant/frontend/pull/55138
[Frontend documentation]: /integrations/frontend/

{% enddetails %}

{% details "General Transit Feed Specification (GTFS)" %}

GTFS stop times are in the agency's local time. Previously, when the time zone configured in your Home Assistant instance differed from the GTFS feed time zone, you could use the `offset` parameter to match the time zones. The integration now automatically applies an offset, so a manual offset is no longer required and may overcorrect the feed stop times.

([@raman325] - [#187429]) ([General Transit Feed Specification (GTFS) documentation])

[@raman325]: https://github.com/raman325
[#187429]: https://github.com/home-assistant/core/pull/187429
[General Transit Feed Specification (GTFS) documentation]: /integrations/gtfs/

{% enddetails %}

{% details "Hayward Omnilogic" %}

The Hayward Omnilogic integration no longer lets you set the {% term polling %} interval in its options. A previously configured interval is ignored, and the default is used.

([@tr4nt0r] - [#184380]) ([Hayward Omnilogic documentation])

[#184380]: https://github.com/home-assistant/core/pull/184380
[Hayward Omnilogic documentation]: /integrations/omnilogic/

{% enddetails %}

{% details "Hive" %}

The Hive integration no longer lets you set a custom {% term polling %} interval. If you configured one, it is ignored and the default interval is used.

([@tr4nt0r] - [#184251]) ([Hive documentation])

[#184251]: https://github.com/home-assistant/core/pull/184251
[Hive documentation]: /integrations/hive/

{% enddetails %}

{% details "Holiday and Workday" %}

The `holidays` library no longer counts ordinary Sundays as holidays in Sweden. The Holiday calendar for Sweden no longer shows a "Söndag" event every Sunday. Named holidays that fall on a Sunday, such as Easter Sunday (Påskdagen) and Whit Sunday (Pingstdagen), are still included.

This also affects the Workday integration for Sweden if you have added Sunday to the workdays and relied on the holidays to exclude it. In that case, ordinary Sundays are now reported as workdays. To keep the previous behavior, add Sunday to the excluded days in the Workday options. The default Workday configuration already excludes Sunday and is not affected.

([@gjohansson-ST] - [#187605]) ([Holiday documentation]) ([Workday documentation])

[#187605]: https://github.com/home-assistant/core/pull/187605
[Holiday documentation]: /integrations/holiday/
[Workday documentation]: /integrations/workday/

{% enddetails %}

{% details "Honeywell Total Connect Comfort (Europe)" %}

The following deprecated {% term actions %} and preset have been removed from the Evohome integration:

- The `evohome.reset_system` action: Use the controller's **Reset** button.
- The `evohome.clear_zone_override` action: Use the zone's **Reset** button.
- The **Reset** preset of the controller's {% term climate "climate entity" %}: Use the controller's **Reset** button.

Update any {% term automations %} or {% term scripts %} that still use these.

([@zxdavb] - [#185704]) ([Honeywell Total Connect Comfort (Europe) documentation])

[@zxdavb]: https://github.com/zxdavb
[#185704]: https://github.com/home-assistant/core/pull/185704
[Honeywell Total Connect Comfort (Europe) documentation]: /integrations/evohome/

Calls to `evohome.set_system_mode` without an `entity_id` are no longer supported. Include the entity ID of the Evohome controller's climate entity.

([@zxdavb] - [#185705]) ([Honeywell Total Connect Comfort (Europe) documentation])

[#185705]: https://github.com/home-assistant/core/pull/185705

{% enddetails %}

{% details "iRobot Roomba and Braava" %}

The **Continuous** and **Delay** options of the iRobot Roomba and Braava integration have been removed. Home Assistant now always keeps one connection open to the robot and reconnects on its own. The underlying library no longer has the periodic connection mode these options controlled.

If you had turned **Continuous** off so the iRobot app could connect to the robot locally, the app now connects through the iRobot cloud while Home Assistant is connected. This is the same behavior as with the default setting. No action is needed.

([@johnnyh1975] - [#184198]) ([iRobot Roomba and Braava documentation])

[@johnnyh1975]: https://github.com/johnnyh1975
[#184198]: https://github.com/home-assistant/core/pull/184198
[iRobot Roomba and Braava documentation]: /integrations/roomba/

{% enddetails %}

{% details "Keenetic NDMS2 Router" %}

The Keenetic NDMS2 Router integration no longer lets you set a custom {% term polling %} interval. If you configured one, it is ignored and the default interval is used.

([@tr4nt0r] - [#184257]) ([Keenetic NDMS2 Router documentation])

[#184257]: https://github.com/home-assistant/core/pull/184257
[Keenetic NDMS2 Router documentation]: /integrations/keenetic_ndms2/

{% enddetails %}

{% details "Kraken" %}

The Kraken integration no longer lets you set a custom {% term polling %} interval. If you configured one, it is ignored and the default interval is used.

([@tr4nt0r] - [#184381]) ([Kraken documentation])

[#184381]: https://github.com/home-assistant/core/pull/184381
[Kraken documentation]: /integrations/kraken/

{% enddetails %}

{% details "Matter" %}

Matter concentration sensors now use the unit the device reports instead of a fixed one. Before, a device measuring in another unit was shown with the wrong unit, for example a <abbr title="total volatile organic compounds">TVOC</abbr> sensor measuring in ppb was shown as ppm.

This affects existing TVOC, carbon monoxide, nitrogen dioxide, and ozone sensors whose device reports a unit other than ppm:

- If the device's unit converts to the old one (for example ppb), the sensor keeps its old unit and the value is now converted, so it changes: a TVOC sensor reporting 189 ppb now shows 0.189 ppm instead of 189 ppm, and the history shows a jump. To get the previous numbers back with the correct unit, set the sensor's unit to the device's unit (here ppb) in its entity settings. Otherwise, update automations, scripts, and templates that use the value. Sensors added from now on use the device's unit directly.
- TVOC sensors reporting µg/m³ or mg/m³ keep their value but switch to the "Volatile organic compounds" device class, which changes their default name (the entity ID stays the same). Their old statistics can't be converted: in **Settings** > **Tools** > **Statistics**, either update the old unit without converting or delete the old statistics.

([@valeronm] - [#167177]) ([Matter documentation])

[@valeronm]: https://github.com/valeronm
[#167177]: https://github.com/home-assistant/core/pull/167177
[Matter documentation]: /integrations/matter/

---

Matter climate entities now resume their last supported non-off HVAC mode when turned on from Home Assistant, including through dashboard controls and voice commands. For example, an air conditioner turned off while cooling will resume cooling when turned on again. Calling `climate.turn_on` on an entity that is already running now leaves its mode unchanged.

Previously, `climate.turn_on` ignored the previous mode and selected heat/cool, then heat, then cool, depending on what the device supports. Automations or scripts that relied on that behavior should call `climate.set_hvac_mode` with the desired mode instead of `climate.turn_on`.

Devices with a separate power switch, such as Matter room air conditioners, are now switched on by `climate.turn_on`. Previously, Home Assistant only changed the mode, so a device that was switched off stayed off. If the device kept its mode while switched off, only the power is switched on and the mode is left unchanged.

If no previous supported mode is known, the earlier fallback order is still used.

([@wardmatter] - [#181458]) ([Matter documentation])

[@wardmatter]: https://github.com/wardmatter
[#181458]: https://github.com/home-assistant/core/pull/181458

---

Matter covers that can only tilt, without moving up and down, such as tilt-only blind controllers, are now shown as tilt covers. Before, their state was always unknown.

They now use the `cover.open_cover_tilt`, `cover.close_cover_tilt`, `cover.stop_cover_tilt`, and `cover.toggle_cover_tilt` actions, instead of `cover.open_cover`, `cover.close_cover`, `cover.stop_cover`, and `cover.toggle`. Update automations, scripts, and device actions that use the old actions on these covers. Voice assistants that open or close these covers may also no longer work for them. Covers that can move up and down are not affected.

([@TheJulianJES] - [#188787]) ([Matter documentation])

[#188787]: https://github.com/home-assistant/core/pull/188787

{% enddetails %}

{% details "MQTT" %}

MQTT entities without a `unique_id` no longer use their `device` configuration. These entities could not be linked to a device, but a `via_device` in their `device` configuration still created a device in the device registry. That device is no longer created. To link an MQTT entity to a device, add a `unique_id` to the entity.

([@jbouwh] - [#187856]) ([MQTT documentation])

[@jbouwh]: https://github.com/jbouwh
[#187856]: https://github.com/home-assistant/core/pull/187856
[MQTT documentation]: /integrations/mqtt/

{% enddetails %}

{% details "Nanoleaf" %}

The deprecated Nanoleaf touch gesture device triggers have been removed. Automations using a Nanoleaf device trigger (single tap, double tap, swipe up/down/left/right) will no longer work. Use the **Touch gesture** {% term "event entity" %} of your Nanoleaf device instead, for example with an `event.received` trigger on the event entity filtered by its `event_type` attribute.

The device triggers were deprecated in Home Assistant 2024.7 and scheduled for removal in 2025.1.

([@MartinHjelmare] - [#188656]) ([Nanoleaf documentation])

[@MartinHjelmare]: https://github.com/MartinHjelmare
[#188656]: https://github.com/home-assistant/core/pull/188656
[Nanoleaf documentation]: /integrations/nanoleaf/

{% enddetails %}

{% details "NINA" %}

The NINA attributes that were deprecated in Home Assistant 2026.5 have been removed. Each one has an {% term entity %} or an {% term action %} that takes its place:

- `headline`: the **Headline** sensor
- `description`: the `nina.get_details` action
- `sender`: the **Sender** sensor
- `severity`: the **Severity** sensor
- `recommended_actions`: the `nina.get_details` action
- `affected_areas`: the **Affected areas** sensor for the shortened list, or the `nina.get_details` action for the full one
- `web`: the **More information URL** sensor
- `sent`: the **Sent** sensor
- `start`: the **Start** sensor
- `expires`: the **Expires** sensor

Update {% term automations %}, {% term scripts %}, {% term templates %}, and dashboard cards that read one of these attributes.

([@DeerMaximum] - [#188355]) ([NINA documentation])

[@DeerMaximum]: https://github.com/DeerMaximum
[#188355]: https://github.com/home-assistant/core/pull/188355
[NINA documentation]: /integrations/nina/

{% enddetails %}

{% details "Philips Hue" %}

The `"None"` light effect has been removed. It was deprecated in Home Assistant 2025.4 in favor of `"off"`, and the mapping that kept the old value working is now gone. Update {% term automations %} and {% term scripts %} that set the effect to `"None"` so that they use `"off"` instead.

([@MartinHjelmare] - [#188867]) ([Philips Hue documentation])

[#188867]: https://github.com/home-assistant/core/pull/188867
[Philips Hue documentation]: /integrations/hue/

{% enddetails %}

{% details "Plaato" %}

The Plaato integration no longer lets you set a custom {% term polling %} interval. If you configured one, it is ignored and the default interval is used.

([@tr4nt0r] - [#184376]) ([Plaato documentation])

[#184376]: https://github.com/home-assistant/core/pull/184376
[Plaato documentation]: /integrations/plaato/

{% enddetails %}

{% details "Python dependencies" %}

Home Assistant no longer installs Python packages into the `deps` folder of your configuration directory. This only affects {% term "Home Assistant Core" %} installations that run outside a virtual environment, which is where that folder was used. Run Home Assistant Core in a virtual environment, as the installation instructions describe, and the packages are installed there instead.

{% term "Home Assistant Operating System" %}, {% term "Home Assistant Supervised" %}, and {% term "Home Assistant Container" %} are not affected. Once you have updated, you can remove the `deps` folder from your configuration directory.

([@emontnemery] - [#168155])

[#168155]: https://github.com/home-assistant/core/pull/168155

{% enddetails %}

{% details "Ring" %}

Several Ring entities that were deprecated in Home Assistant 2024.9, and originally scheduled for removal in Home Assistant 2025.4, have now been removed:

- The ding and motion binary sensors, and the last ding and last motion sensors. Use the event entities instead.
- The volume sensors, including the doorbell, microphone, and voice volume sensors. Use the number entities instead, which also let you change the volume.
- The siren switch. Use the siren entity instead.

If you use any of these entities in an automation, script, or dashboard, update it to use its replacement.

([@tr4nt0r] - [#187592]) ([@tr4nt0r] - [#187596]) ([@tr4nt0r] - [#188108]) ([Ring documentation])

[#187592]: https://github.com/home-assistant/core/pull/187592
[#187596]: https://github.com/home-assistant/core/pull/187596
[#188108]: https://github.com/home-assistant/core/pull/188108
[Ring documentation]: /integrations/ring/

{% enddetails %}

{% details "Risco" %}

The Risco integration no longer lets you set a custom {% term polling %} interval. If you configured one, it is ignored and the default interval is used.

([@tr4nt0r] - [#184386]) ([Risco documentation])

[#184386]: https://github.com/home-assistant/core/pull/184386
[Risco documentation]: /integrations/risco/

{% enddetails %}

{% details "Rituals Perfume Genie" %}

The **Fill** sensor of Rituals Perfume Genie diffusers now reports a percentage, instead of a range as text like "70-80%". If you use it in automations or scripts, compare it against a number instead. When there is no measurement, it is unknown instead of "No measurement available".

The **Perfume** sensor is now unknown when no cartridge is inserted, instead of showing "Cartridge is not loaded". Use the new **Cartridge** binary sensor to tell whether a cartridge is inserted.

([@frenck] - [#186995]) ([Rituals Perfume Genie documentation])

[#186995]: https://github.com/home-assistant/core/pull/186995
[Rituals Perfume Genie documentation]: /integrations/rituals_perfume_genie/

{% enddetails %}

{% details "SMTP" %}

When an attachment cannot be read, the SMTP notify action now reports an error instead of sending the message without it. Before, a missing file was only logged as a warning and the rest of the email went out, so a wrong path could go unnoticed for a long time.

If one of your {% term automations %} or {% term scripts %} attaches a file that is not always there, such as a camera snapshot, check the path, or build the list of attachments so that it only contains files that exist.

([@tr4nt0r] - [#188876]) ([SMTP documentation])

[#188876]: https://github.com/home-assistant/core/pull/188876
[SMTP documentation]: /integrations/smtp/

{% enddetails %}

{% details "Telegram" %}

The legacy **Telegram** notify platform (`notify` with `platform: telegram` in YAML), deprecated in 2025.11, has been removed. Its `notify.<name>` actions no longer exist.

Use the notify entities of the [Telegram bot](/integrations/telegram_bot/#notifiers) integration instead: add each chat ID as a subentry of your Telegram bot and send messages with the `notify.send_message` action, or use the `telegram_bot` actions for photos, documents, keyboards, and other options. Remove the `platform: telegram` entries from the `notify` section of your {% term "`configuration.yaml`" %} file. If the configuration is still present, Home Assistant shows a repair issue.

([@jbouwh] - [#188196]) ([Telegram documentation])

[#188196]: https://github.com/home-assistant/core/pull/188196
[Telegram documentation]: /integrations/telegram_bot/

{% enddetails %}

{% details "Telldus Live" %}

The `tellduslive` {% term YAML %} configuration is no longer imported. If you still have a `tellduslive:` entry in your {% term "`configuration.yaml`" %}, remove it. Home Assistant raises a repair issue to remind you.

This should not affect anyone in practice: YAML has been imported into a config entry since December 2018, when the config flow was added. Any existing YAML setup was converted long ago and keeps working, and a YAML entry has had no effect since the config entry was created.

([@gjohansson-ST] - [#185838]) ([Telldus Live documentation])

[#185838]: https://github.com/home-assistant/core/pull/185838
[Telldus Live documentation]: /integrations/tellduslive/

{% enddetails %}

{% details "Tomorrow.io" %}

The Tomorrow.io integration now has one entry per API key instead of one per location. Each location is a subentry of the entry for its API key. Existing setups migrate automatically and no action is required: locations, entities, devices, and their history are preserved, and per-location "timestep" options carry over. Two things change if you had multiple locations: locations sharing an API key now live under a single config entry, and each location gets its own device. The nowcast timestep is now changed by selecting **Reconfigure** on a location instead of the integration options.

([@raman325] - [#177911]) ([Tomorrow.io documentation])

[#177911]: https://github.com/home-assistant/core/pull/177911
[Tomorrow.io documentation]: /integrations/tomorrowio/

{% enddetails %}

{% details "Tuya" %}

Multi-channel Tuya devices now put the {% term entities %} of each channel on their own **Channel** {% term device %}, as a child device of the main one.

Entity IDs and history are kept, and a {% term trigger %}, {% term condition %}, or {% term action %} that targets the main device still covers the channel entities. What changes is the name. An entity called "Socket 1" becomes "Socket" on the "Channel 1" device, and its `friendly_name` attribute is now built from that channel device, so it reads "Channel 1 Socket" instead of the name of the main device followed by "Socket 1". Single-channel devices go from "Socket 1" to "Socket" as well.

Update {% term templates %}, dashboard cards, and notifications that use `friendly_name` or the old entity name.

([@epenet] - [#184915]) ([@epenet] - [#188169]) ([@epenet] - [#188237]) ([@epenet] - [#188255]) ([@epenet] - [#188258]) ([@epenet] - [#188674]) ([@epenet] - [#188675]) ([Tuya documentation])

[#184915]: https://github.com/home-assistant/core/pull/184915
[#188169]: https://github.com/home-assistant/core/pull/188169
[#188237]: https://github.com/home-assistant/core/pull/188237
[#188255]: https://github.com/home-assistant/core/pull/188255
[#188258]: https://github.com/home-assistant/core/pull/188258
[#188674]: https://github.com/home-assistant/core/pull/188674
[#188675]: https://github.com/home-assistant/core/pull/188675
[Tuya documentation]: /integrations/tuya/

{% enddetails %}

{% details "UniFi Protect" %}

The deprecated UniFi Protect HDR mode switch is removed. It was deprecated in 2024.4 because it cannot represent the auto HDR mode. Use the HDR mode select instead. If an enabled switch is still used in an automation or script, a repair lists the automations and scripts that use it.

([@RaHehl] - [#184425]) ([UniFi Protect documentation])

[@RaHehl]: https://github.com/RaHehl
[#184425]: https://github.com/home-assistant/core/pull/184425
[UniFi Protect documentation]: /integrations/unifiprotect/

---

The read-only UniFi Protect UP Sense setting entities deprecated in 2026.9 are removed. Use the matching switch or the "Motion sensitivity" number instead. A repair lists automations and scripts that still use a removed entity.

([@RaHehl] - [#184473]) ([UniFi Protect documentation])

[#184473]: https://github.com/home-assistant/core/pull/184473

{% enddetails %}

{% details "Uptime Kuma" %}

Support for Uptime Kuma versions earlier than 2.0.0 has been dropped. Version 2.0.0 was released more than a year ago. Update Uptime Kuma before updating Home Assistant if you use an older version.

([@tr4nt0r] - [#187418]) ([Uptime Kuma documentation])

[#187418]: https://github.com/home-assistant/core/pull/187418
[Uptime Kuma documentation]: /integrations/uptime_kuma/

{% enddetails %}

{% details "Watergate" %}

The **Water meter volume** (`sensor.<name>_water_meter_volume`) and **Water meter duration** (`sensor.<name>_water_meter_duration`) sensors of Watergate Sonic now report the _positive_ meter (water flowing in the normal direction) instead of the _positive minus negative_ difference. Entity IDs, unique IDs, and long-term statistics are unchanged.

- **Who is affected:** only devices that have ever recorded reverse flow (backflow). The value steps _up_ once, by the device's lifetime backflow, at the first update after upgrading. Because these sensors are `total_increasing`, Home Assistant records that step as consumption, so the Energy dashboard and statistics show a one-time spike. Devices with no recorded backflow see no change.
- **How to recover:** adjust the spike away with **Adjust a statistic** in {% my developer_statistics title="**Settings** > **Tools** > **Statistics**" %}, or ignore it. Nothing needs to be reconfigured.
- **Why:** the old value silently hid reverse flow and was not the monotonically increasing total the state class promises. The new **Water meter negative volume/duration** sensors expose the reverse reading separately.

On firmware that only reports a single (differential) meter, **Water meter volume/duration** keep reporting that differential and the new negative sensors are unavailable.

([@adam-the-hero] - [#186035]) ([Watergate documentation])

[@adam-the-hero]: https://github.com/adam-the-hero
[#186035]: https://github.com/home-assistant/core/pull/186035
[Watergate documentation]: /integrations/watergate/

{% enddetails %}

{% details "Xiaomi BLE" %}

The high and low frequency values of the S400 impedance sensors were swapped. This release corrects the mapping. Entities are not migrated: the scale overwrites its impedance values on every weigh-in, for whichever profile steps on it, so past readings are not tied to a specific user and keeping their history has little value.

After updating:

- The entity previously exposed as `impedance` is no longer updated and can be removed.
- `impedance_low` now reports the actual low frequency value. It previously reported the high frequency one.
- `impedance_high` is a new sensor.

Check {% term automations %}, {% term templates %}, and dashboards that rely on these entities.

([@dckiller51] - [#173260]) ([Xiaomi BLE documentation])

[@dckiller51]: https://github.com/dckiller51
[#173260]: https://github.com/home-assistant/core/pull/173260
[Xiaomi BLE documentation]: /integrations/xiaomi_ble/

{% enddetails %}

{% details "Xiaomi Home" %}

Xiaomi Miio light, switch, and fan actions now require an explicit target. Previously, calling them without an `entity_id` acted on every matching Xiaomi Miio device. Calls without a target now fail with a validation error.

Existing calls that specify `entity_id` still work. To act on all matching entities, use `entity_id: all`.

This affects these actions in the `xiaomi_miio` {% term domain %}:

- Light: `light_set_scene`, `light_set_delayed_turn_off`, `light_reminder_on`, `light_reminder_off`, `light_night_light_mode_on`, `light_night_light_mode_off`, `light_eyecare_mode_on`, `light_eyecare_mode_off`
- Switch: `switch_set_wifi_led_on`, `switch_set_wifi_led_off`, `switch_set_power_mode`, `switch_set_power_price`
- Fan: `fan_reset_filter`, `fan_set_extra_features`

([@balloob] - [#179544]) ([Xiaomi Home documentation])

[#179544]: https://github.com/home-assistant/core/pull/179544
[Xiaomi Home documentation]: /integrations/xiaomi_miio/

{% enddetails %}

{% details "Z-Wave" %}

With this release, you will need to update your zwave-js-server instance. You must use zwave-js-server 3.11.0 or greater (schema 51).

- If you use the Z-Wave JS {% term app %}, you need at least version 1.9.0.
- If you use the Z-Wave JS UI Docker container, you need at least version [zwave-js/zwave-js-ui@v11.24.2 (release)](https://github.com/zwave-js/zwave-js-ui/releases/tag/v11.24.2).
- If you run your own Docker container or some other installation method, you will need to update your zwave-js-server instance to at least 3.11.0.

([@MartinHjelmare] - [#184901]) ([Z-Wave documentation])

[#184901]: https://github.com/home-assistant/core/pull/184901
[Z-Wave documentation]: /integrations/zwave_js/

---

Entities for features on non-root endpoints of multi-endpoint Z-Wave devices now live on their own child {% term devices %} of the main device, when the Z-Wave JS device database describes those endpoints as separate parts. Only devices with that information are affected: endpoints that carry a label, or that belong to an endpoint group.

Because the name of an {% term entity %} is built from the device it belongs to, the name of the main device no longer appears in it. A thermostat with three temperature sensors used to be one device with "Air temperature (2)", "Air temperature (3)", and "Air temperature (4)". It is now a main device with one child device per sensor, each named after its endpoint label, such as "Room Sensor", and each with a single "Air temperature" entity. A multi-clamp energy meter becomes the main device plus one child device per clamp.

Entity IDs stay the same, and {% term automations %} and {% term scripts %} that target the main device keep working, because targeting a device also targets the entities of its child devices.

One entity does disappear: the redundant endpoint-2 "slat" value of the Fibaro FGR223 and the Shelly Qubino Wave Shutter (QNSH-001P10) is no longer created. If you had enabled that cover entity, it is gone.

([@MartinHjelmare] - [#185985]) ([Z-Wave documentation])

[#185985]: https://github.com/home-assistant/core/pull/185985

{% enddetails %}

{% details "Zigbee Home Automation" %}

Each ZHA {% term group %} that has group {% term entities %} now gets its own {% term device %}, named after the group, and those entities move there from the coordinator device. Entity IDs and settings are kept, and a name or {% term area %} you set yourself moves along, so {% term automations %}, {% term scripts %}, and dashboards that use the group entities keep working.

Two things need your attention:

- If you target the **coordinator device** to control your groups, target the group entities or the new group devices instead. The device page of the coordinator no longer lists the group entities.
- If you relied on the group entities being in the area of the coordinator device, give the new group devices or their entities an area of their own.

([@TheJulianJES] - [#188830]) ([Zigbee Home Automation documentation])

[@TheJulianJES]: https://github.com/TheJulianJES
[#188830]: https://github.com/home-assistant/core/pull/188830
[Zigbee Home Automation documentation]: /integrations/zha/

{% enddetails %}

If you are a {% term "custom integration" %} developer and want to learn about changes and new features available for your integration: Be sure to follow the [blog on our contributors site][contributors-blog]. The following changes are the most notable for this release:

- [A new home for every contributor](https://contributors.home-assistant.io/blog/2026/10/16/a-new-home-for-every-contributor/)
- [A Python console inside Home Assistant](https://contributors.home-assistant.io/blog/2026/10/17/debug-console/)
- [Always pass a step_id to flow results](https://contributors.home-assistant.io/blog/2026/10/23/flow-results-require-step-id/)
- [Auth providers now opt in to multi-factor authentication](https://contributors.home-assistant.io/blog/2026/10/19/auth-providers-opt-in-mfa/)
- [Backup agents can now be renamed](https://contributors.home-assistant.io/blog/2026/10/25/rename-backup-agents/)
- [Climate entities now expose their temperature unit](https://contributors.home-assistant.io/blog/2026/10/08/climate-native-temperature/)
- [Config entry functions now return None](https://contributors.home-assistant.io/blog/2026/10/23/config-entry-methods-return-none/)
- [Custom section strategies in the dashboard editor](https://contributors.home-assistant.io/blog/2026/10/28/custom-section-strategies-in-the-dashboard-editor/)
- [DeviceInfo is now a dataclass](https://contributors.home-assistant.io/blog/2026/10/13/device-info-class/)
- [Frontend component updates in 2026.11](https://contributors.home-assistant.io/blog/2026/10/28/frontend-component-updates-2026.11/)
- [Integrations have categories now](https://contributors.home-assistant.io/blog/2026/10/20/integration-categories/)
- [Introducing child devices](https://contributors.home-assistant.io/blog/2026/10/22/child-devices/)
- [New entity lifecycle hooks](https://contributors.home-assistant.io/blog/2026/10/12/new-entity-lifecycle-hooks/)
- [New unit of measurement selector](https://contributors.home-assistant.io/blog/2026/10/09/uom-selector/)
- [Repair issues can belong to a config entry, and be refreshed](https://contributors.home-assistant.io/blog/2026/10/28/issue-registry-refresh/)
- [ScannerEntity now handles devices like other entities](https://contributors.home-assistant.io/blog/2026/10/28/scanner-entity-devices/)
- [Show form fields based on other fields](https://contributors.home-assistant.io/blog/2026/10/21/form-fields-visible/)
- [Two-way audio for camera entities](https://contributors.home-assistant.io/blog/2026/10/24/camera-two-way-audio/)
- [Undefined sentinel changes](https://contributors.home-assistant.io/blog/2026/11/01/undefined-helper/)
- [Update entities can customize update availability](https://contributors.home-assistant.io/blog/2026/10/10/update-entity-update-availability/)
- [Water heater entities now expose their temperature unit](https://contributors.home-assistant.io/blog/2026/10/08/water-heater-native-temperature/)

[contributors-blog]: https://contributors.home-assistant.io/blog/
