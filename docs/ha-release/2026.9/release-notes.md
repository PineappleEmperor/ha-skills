# 2026.9: There's room on this bus — backward-incompatible changes

Fetched from https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/source/_posts/2026-09-02-release-20269.markdown
Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of home-assistant/home-assistant.io.
Modified: this is the *Backward-incompatible changes* section of the post's own source markdown, cut at the surrounding `##` headings by `scripts/fetch_ha_sources.py`. Nothing inside it has been changed, added or reordered; the rest of the post — the feature write-ups and the patch-release changelogs — is not kept.

## Backward-incompatible changes

We do our best to avoid making changes to existing functionality that might unexpectedly impact your Home Assistant installation. Unfortunately, sometimes it is inevitable.

We always make sure to document these changes to make the transition as easy as possible for you. This release has the following backward-incompatible changes:

{% details "Flexit Nordic (BACnet)" %}

The deprecated fireplace mode switch entity has been removed. If you have {% term automations %} or {% term scripts %} that use `switch.<device>_fireplace_mode`, use the `climate.set_preset_mode` action on the Flexit climate entity with `preset_mode: fireplace` instead.

([@magnusoverli] - [#179272]) ([Flexit Nordic (BACnet) documentation])

[@magnusoverli]: https://github.com/magnusoverli
[#179272]: https://github.com/home-assistant/core/pull/179272
[Flexit Nordic (BACnet) documentation]: /integrations/flexit_bacnet/

{% enddetails %}

{% details "KNX" %}

KNX exposes no longer send an entity's first value to the KNX bus. Previously, this depended on timing: if the entity already had a value when the expose was set up, nothing was sent, but if the value arrived later, it was sent to the bus right away.

Now, both cases behave the same way. The first value is adopted locally without sending a telegram, but stays available for read requests and periodic sending. Later value changes are still sent as before.

To send the first value right away, turn on **Send on initialization** for the expose in the KNX panel, or set `send_on_init: true` in your YAML configuration.

([@Kolbi] - [#178793]) ([KNX documentation])

[@Kolbi]: https://github.com/Kolbi
[#178793]: https://github.com/home-assistant/core/pull/178793
[KNX documentation]: /integrations/knx/

{% enddetails %}

{% details "LLM APIs" %}

LLM tool names are now prefixed with the domain of the integration that offers them. For example, `GetLiveContext` becomes `homeassistant__GetLiveContext` and `HassTurnOn` becomes `intent__HassTurnOn`. If you have a custom prompt that names a tool directly, update it to use the new prefixed name.

([@balloob] - [#179938])

[#179938]: https://github.com/home-assistant/core/pull/179938

{% enddetails %}

{% details "Persistent Notification" %}

Updating a persistent notification that already exists now triggers an `update_type` of `updated` instead of `added`. If you have an {% term automation %} that triggers on an `update_type` of `added` to catch every new or changed notification, add `updated` to the list of types it triggers on.

([@davidlang42] - [#171067]) ([Persistent Notification documentation])

[@davidlang42]: https://github.com/davidlang42
[#171067]: https://github.com/home-assistant/core/pull/171067
[Persistent Notification documentation]: /integrations/persistent_notification/

{% enddetails %}

{% details "UniFi Protect" %}

The smart detection switches (for example Detections: Person, Detections: Vehicle, and the audio alarm toggles) are no longer hidden while recording is disabled. They now stay available and follow the same public API as the other camera configuration switches. Their entity IDs and what happens when you toggle them are unchanged.

([@RaHehl] - [#174963]) ([UniFi Protect documentation])

UniFi Protect 7.2.105 or newer is now required. On an older version, the integration stops setting up and tells you to update. Update UniFi Protect, then {% term reload %} the integration.

([@RaHehl] - [#179954]) ([UniFi Protect documentation])

[@RaHehl]: https://github.com/RaHehl
[#174963]: https://github.com/home-assistant/core/pull/174963
[#179954]: https://github.com/home-assistant/core/pull/179954
[UniFi Protect documentation]: /integrations/unifiprotect/

{% enddetails %}

{% details "Update" %}

Installing an {% term update %}, skipping an update, and clearing a skipped update now require an administrator account. These are configuration-level actions, so they are now restricted to admins, like other sensitive actions in Home Assistant.

{% term Automations %} are not affected, because they run without a user context. A {% term script %} runs in the context of the user who started it, so a script that installs or skips an update now fails when a non-admin user starts it. Trigger it from an automation instead, or start it as an admin.

([@balloob] - [#178232]) ([Update documentation])

[#178232]: https://github.com/home-assistant/core/pull/178232
[Update documentation]: /integrations/update/

{% enddetails %}

{% details "Vacuum" %}

The deprecated `battery_level` property has been removed from the base vacuum entity. All core vacuum integrations were already migrated in Home Assistant 2026.8. If a custom integration still sets this property, it no longer reports a battery level; add a separate battery sensor instead.

([@gjohansson-ST] - [#175682]) ([Vacuum documentation])

[@gjohansson-ST]: https://github.com/gjohansson-ST
[#175682]: https://github.com/home-assistant/core/pull/175682
[Vacuum documentation]: /integrations/vacuum/

{% enddetails %}

{% details "Z-Wave JS" %}

The Z-Wave actions to manage lock users and credentials (`set_user`, `delete_user`, `delete_all_users`, `set_credential`, `delete_credential`, and `delete_all_credentials`) now require an administrator account.

([@balloob] - [#177300]) ([Z-Wave JS documentation])

[#177300]: https://github.com/home-assistant/core/pull/177300
[Z-Wave JS documentation]: /integrations/zwave_js/

{% enddetails %}

If you are a custom integration developer and want to learn about changes and new features available for your integration: Be sure to follow our [developer blog][devblog]. The following changes are the most notable for this release:

- [Configurator integration is now deprecated](https://developers.home-assistant.io/blog/2026/08/31/deprecate-configurator)
- [Device registry WebSocket API changes](https://developers.home-assistant.io/blog/2026/08/19/device-registry-websocket-api-changes)
- [More device registry deprecations, new helpers and validation](https://developers.home-assistant.io/blog/2026/08/24/device-registry-follow-up-changes)

[devblog]: https://developers.home-assistant.io/blog/
