# 2026.9: There's room on this bus

Fetched from https://www.home-assistant.io/blog/2026/09/02/release-20269/
Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of home-assistant/home-assistant.io.
Modified only in format: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. The wording is the author's, unaltered.

Home Assistant 2026.9! 🎉

I’ll be honest: Modbus has never been the flashiest part of Home Assistant. It quietly powers solar inverters, heat pumps, and energy meters, but only if you’re comfortable hand-writing your own register map in YAML, a real wall that’s kept a huge category of devices out of reach. This release finally makes room on the bus: integrations that already know how a device talks over Modbus, sharing a single connection instead of fighting over it, so you simply pick your device in the UI like anything else in Home Assistant. It won’t show up in a screenshot, but modernizing Modbus is hands-down my favorite change this release. 🔧

I’m also really looking forward to jumping on the new Cloud voice processing myself and putting it through its paces. We’re a household with a non-English main language, and if you’ve ever run a private voice assistant in one, you know exactly how fast accents and background noise trip things up. This new speech-to-text engine specifically targets those pain points, so I’m very curious to see how it holds up against my own accent. 😉

And there’s plenty more: active alerts and favorites for the Security dashboard, a shared Sources panel for History and Activity, Activity that finally explains why something changed, a brand new network map for Matter, charts you can now navigate by keyboard and sound, and 13 new integrations! 🚀

One more thing before you dive in: we’re at IFA Berlin this weekend! It’s one of the largest consumer electronics expos out there, running September 4 to 8, 2026, and the Open Home Foundation has its own booth in the Smart Home hall: Hall 1.2, stand 1.2-153. If you’re around, come find us and say hi. 👋

Enjoy the release!

../Frenck

Home Assistant Cloud

Seeing through the Cloud

Test the new voice processing

Float in to be a Cloud subscriber

Active alerts and favorites for the Security dashboard

A new Sources pane for History and Activity

From what changed to why it changed

Insights into your Matter world

New tile card features

Modernizing Modbus

Integrations

New integrations

Noteworthy improvements to existing integrations

Integration quality scale achievements

Now available to set up from the UI

Farewell to the following

Other noteworthy changes

Golden hour, blue hour, and polar sun automations

Accessibility for charts!

Serial and MQTT panels

How full is your network storage?

Patch releases

2026.9.1 - September 5

2026.9.2 - September 11

2026.9.3 - September 18

Need help? Join the community

Backward-incompatible changes

All changes

A huge thank you to all the contributors who made this release possible! And a special shout-out to @googanhiem and @piitaya who helped write these release notes. Also, @Diegorro98, @jan-tdy, @RaHehl, and @farmio for putting effort into tweaking its contents. Thanks to them, these release notes are in great shape. ❤️

Home Assistant Cloud

Home Assistant Cloud is an essential part of funding the Open Home Foundation. We’re so thankful for all the support from our subscribers, and from the start we’ve always been clear: this isn’t just a donation to Home Assistant, we want it to provide real benefits to subscribers. Together with Nabu Casa, we’ve been constantly working to make Cloud better, and here are some useful recent additions.

Seeing through the Cloud

A new addition that should help security-conscious Home Assistant Cloud subscribers is the ability to better see who is attempting to log into your instance. In the past, they all looked like local requests, and you may have seen the 127.0.0.1 invalid login attempt message, which wasn’t that helpful. Now the proper IP address gets passed through, so whether that’s you mixing up your passwords when logging in, or some bot trying their luck, you’ll now know better where it’s coming from.

A side benefit of this change is that it’s now possible to use IP banning to make it harder for these malicious actors, which was added to the UI in the previous release. In conjunction with setting up multi-factor authentication (2FA) in Home Assistant, you can add a little extra peace of mind to your home, but that’s not the only Cloud benefit being improved this month.

Test the new voice processing

When we launched Home Assistant Voice Preview Edition, a good amount of the community jumped into running their own private voice assistants in their homes. Building something to rival big tech is still a work-in-progress, but every year we get closer. Today, we’re again asking for our Cloud subscribers to help us test another awesome step forward.

Our friends at Nabu Casa are testing a new speech-to-text engine for Home Assistant Cloud, and it significantly improves the three common places voice processing gets tripped up: accents, background noise, and non-English languages. Many of us around the Foundation have been using it and finding it works great with our sometimes unique accents even in noisy environments.

There are several big changes under the hood, including switching to a new provider Soniox, so it needs to be tested. You’ll still get the same privacy guarantee of no logging, storing, or training on your audio. It’ll be available to test via Labs, with the normal caveat that it may not be a permanent addition, so provide your feedback on the Labs page if it’s the right step forward.

If you’re a Home Assistant Cloud subscriber, you can toggle this on right now by heading to Settings > System > Labs. If you’re not a subscriber, there is a 31-day trial. Speaking of which, there are some big improvements on signing up coming as well.

Float in to be a Cloud subscriber

Signing up for Home Assistant Cloud now begins on a clearer start page: one obvious button to Start your free trial, and a link to Sign in if you already have an account. It also finally shows what you would actually be getting. The old page left you to guess what was behind that button, which, fair enough, didn’t help anyone. Now the features are listed right there, before you even start the trial.

Now confirming your email will automatically log you in to Home Assistant Cloud, so you can immediately set up remote access, voice, and backupsHome Assistant has built-in functionality to create files containing a copy of your configuration. This can be used to restore your Home Assistant as well as migrate to a new system. The backup feature is available for all installation types. [Learn more]. No more logging in after signing up! And as always, the one-month trial requires no payment details.

Home Assistant Cloud is built and run by Nabu Casa, a commercial partner of the Open Home Foundation. Every subscription funds the foundation directly, and with it, the full-time development of Home Assistant, this release included. 😊

In return, you get secure remote access with no port forwarding or VPN, encrypted off-site backupsHome Assistant has built-in functionality to create files containing a copy of your configuration. This can be used to restore your Home Assistant as well as migrate to a new system. The backup feature is available for all installation types. [Learn more] ready to restore your whole system the moment you need them, faster and more accurate speech-to-text and text-to-speech for your own voice assistant, native Amazon Alexa and Google Assistant support, and more. It’s all built with the same respect for your privacy as Home Assistant itself: no ads, no data harvesting, just a service that keeps Home Assistant independent.

If you have been thinking about a subscription, there has never been an easier moment to try it.

Active alerts and favorites for the Security dashboard

The built-in Security dashboard is getting more love, and this release adds two things people kept asking for, both managed from the same editor.

The new Active alerts section only shows up when something actually needs your attention, like a door left open or a smoke detector going off. You choose which entitiesAn entity represents a sensor, actor, or function in Home Assistant. Entities are used to monitor physical properties or to control other entities. An entity is usually part of a device or a service. [Learn more] can trigger it, and how serious each one is, as an Alert or a Warning, so a window left open doesn’t get the same red treatment as an actual smoke alarm. Nothing going on? The section stays out of the way entirely.

Right alongside it, a new Favorites section lets you pin the entities you check most, so your most important doors, locks, or sensorsSensors return information about a thing, for instance the level of water in a tank. [Learn more] sit at the top of the dashboard instead of wherever they happen to fall.

This started as a community-designed concept from @ricardoantoniocm, right down to the severity colors and the pulsing animation for anything that needs attention. It’s part of an Open Home Foundation roadmap opportunity to bring severity to the Security dashboard, and there’s more to come: surfacing these same alerts on the Home dashboard is still on the list for a future release.

A new Sources pane for History and Activity

Browsing and finding what you’re looking for in History and Activity can be daunting, so… we made it better! Both pages now share a single Sources panel on the left side that merges target picking (floorsA floor in Home Assistant is a logical grouping of areas that are meant to match the physical floors in your home. Devices & entities are not assigned to floors but to areas. Floors can be used in automations and scripts as a target for actions. For example, to turn off all the lights on the downstairs floor when you go to bed. [Learn more], areasAn area in Home Assistant is a logical grouping of devices and entities that represents a room or space in your home, such as the living room, kitchen, or garage. [Learn more], devicesA device is a model representing a physical or logical unit that contains entities., and entitiesAn entity represents a sensor, actor, or function in Home Assistant. Entities are used to monitor physical properties or to control other entities. An entity is usually part of a device or a service. [Learn more]) with filtering by domainEach integration in Home Assistant has a unique identifier: The domain. It is often shown as the first part (before the dot) of entity IDs., device class, and integrationIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more], so you can narrow a whole area down to, say, just its motion sensors. The panel docks to the side and opens automatically on wider screens, and tucks away as a pull-up sheet on narrower ones. Whatever you filter on is remembered the next time you come back.

The two pages still behave the way they always have, on purpose: History waits for you to pick something before it draws a chart, since showing everything at once wouldn’t be very useful (or fast in that regard 😅). Activity keeps showing everything by default, and you can narrow it down with filters alone, no target required.

A couple of smaller improvements come along for the ride: the date range picker is now a single pill with previous and next arrows, and long entity names on the History timeline draw above their bar and truncate to fit, instead of being cut off. Always nice to see the attention to detail.

This follows an Open Home Foundation design discussion on giving History and Activity a shared layout.

From what changed to why it changed

Open Activity and you can see exactly what changed: a light turned on, a door unlocked, a blind closed. What you couldn’t see was why. Figuring that out meant guessing which automationAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more] was responsible, opening it, digging into its trace, and working backward to the entityAn entity represents a sensor, actor, or function in Home Assistant. Entities are used to monitor physical properties or to control other entities. An entity is usually part of a device or a service. [Learn more] that actually triggered it. It got harder still after a recent redesign of the log rows, which traded the sentence that used to explain where an entry came from for showing an entity’s area and device instead, so even that small hint disappeared.

Selecting any row in Activity now opens a details dialog that lays out the full story, read top to bottom: what started it (a person, a state change, a schedule, an integrationIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more], or a restart), the automationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more] or scriptsScripts are components that allow you to specify a sequence of actions to be executed by Home Assistant when turned on. [Learn more] it passed through, and finally the entity’s own change. Every step in that chain is clickable, opening the entity behind it or, for automations, its trace directly. Timestamps go down to the millisecond, so even events that landed in the same second keep their correct order.

Insights into your Matter world

Zigbee (through ZHA), Z-Wave, and Bluetooth have shown you a map of how their devices connect to each other for a while now. 🗺️ MatterMatter is an open-source standard that defines how to control smart home devices on a Wi-Fi or Thread network. [Learn more] never got the same treatment in Home Assistant, even though the data existed all along, just not here: the Matter Server has its own working network map, tucked away in a separate web interface most people never open.

The Matter panel now has a Show map button that brings that same picture right into Home Assistant, using the same graph experience you already know from the other protocols. It shows the full picture: which devices talk over ThreadThread is a low-power mesh networking standard that is specifically designed for smart home applications. It is a protocol that defines how devices communicate. [Learn more] and which over Wi-Fi, which ones are routers or “border routers”A Thread border router forwards data packets between your local network and the Thread network. This enables smart home devices within a Thread network to communicate with IPv6-capable devices in your local network. A Thread border router is connected to your network either via Wi-Fi or Ethernet and uses its radio frequency (RF) radio to communicate with the Thread mesh network. In case of Matter, the data that is forwarded is encrypted. Examples of Thread border routers are the Nest Hub (2nd gen), the HomePod mini, and the Home Assistant Connect ZBT-2 together with the OpenThread Border Router app. [Learn more] versus battery-powered end devices, and the path from Home Assistant to each one. Border routers and access points are named from things you’d actually recognize, like their network host name or Wi-Fi network name, instead of a serial number. Link color tells you the transport, Thread or Wi-Fi, and the thickness and direction reflect the signal strength on each side of the connection.

If your Matter server is a bit older and doesn’t support this yet, the page tells you so instead of just failing, so you know to update rather than assume something’s broken.

This closes out an Open Home Foundation roadmap opportunity to bring Matter’s network map in line with the other protocols.

New tile card features

The tile card keeps gaining more ways to control an entityAn entity represents a sensor, actor, or function in Home Assistant. Entities are used to monitor physical properties or to control other entities. An entity is usually part of a device or a service. [Learn more] without opening its more-info dialog, and this release adds three, all from the same contributor.

Lights get a new Light effect feature, so you can pick and preview an effect, like Rainbow, directly from the tile.

Vacuums get a new Vacuum fan speed feature, so you can switch between fan speeds, like min, medium, high, or max, right alongside the existing start, stop, and dock commands.

And the existing Target humidity feature, previously limited to humidifiers, now also works with ClimateThe Climate entity allows you to control and monitor HVAC (heating, ventilating, and air conditioning) devices and thermostats. [Learn more] entities that support humidity control, using the step size your device reports instead of a fixed one.

All three come with matching tile card suggestions, so Home Assistant offers to add them automatically when they make sense for an entity.

Thanks to @pcan08 for all three!

One more tile card fix: with the Feature position set to Inline, only the first feature used to show up, and the rest were silently dropped. Now the first one sits next to the entity name as before, and the others appear below it in two columns.

Thanks to @JulianHock for that one!

Modernizing Modbus

Modbus devices, like solar inverters, energy meters, and heat pumps, have long been supported in Home Assistant through the YAMLYAML is a human-readable data serialization language. It is used to store and transmit data in a structured format. In Home Assistant, YAML is used for configuration, for example in the configuration.yaml or automations.yaml files. [Learn more]-based Modbus integration, where you hand-write a register map for your device yourself. That still works and isn’t going anywhere, but it puts the burden of understanding a device’s protocol on every user. This release lays the groundwork for a different way: integrations that already know how a device talks over Modbus, so you pick your device in the UI, the same as any other integration.

The first integrations built this way are already here: Fronius gained optional Modbus TCP (SunSpec) support, adding per-string solar data — current, voltage, power, and lifetime energy for each MPP tracker — that its existing local HTTP API doesn’t expose. It shares its connection with anything else talking to the same inverter, which matters in practice: some Fronius models only accept a handful of simultaneous Modbus sessions. Sofar Inverter Modbus and Flexit are built the same way.

For the full story, including the new standalone modbus-connection library and how to build your own integration on top of it, read Modernizing Modbus in Home Assistant on the developer blog. Underneath, it talks to devices through tmodbus, a modern, fully typed Modbus library.

Thanks to Paulus (@balloob) for pushing this forward, @wlcrs for tmodbus, the library it’s built on, @farmio for Fronius, @darkrain-nl for Sofar Inverter Modbus, and @troelde for Flexit!

Integrations

Thanks to our community for keeping pace with the new integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] and improvements to existing ones! You’re all awesome 🥰

New integrations

We welcome the following new integrations in this release:

Besen, added by @moryoav

Connect Besen EV chargers to Home Assistant over Bluetooth Low Energy, using Home Assistant’s built-in Bluetooth support or an ESPHome Bluetooth proxy. It works with the Besen BS20 charging station and other Besen chargers that use the same protocol.

Collection image, added by @karwosts

Turn a folder from a media source into a dynamic image entity. Home Assistant picks a random picture from the folder, so you can show a changing image on a dashboard or use it as a view background.

Flow-it, added by @albertogeniola

Monitor and control your Flow-it ventilation system from Home Assistant. Adjust the fan speed, switch between preset modes such as Auto and Boost, and bring it into your automations alongside your other smart home devices. The integration connects to the device on your local network and supports automatic discovery.

Hot Spring, added by @Moustachauve, launching at 🏆 platinum quality

Monitor and control a Hot Spring spa equipped with the HotSpring Connected Spa Kit 2 module, directly over your local network.

ISEO Argo BLE, added by @FezVrasta

Control an ISEO Argo Bluetooth smart lock, common on armored doors in Italy and Switzerland, syncing its access log into the Home Assistant logbook and managing its users through actions. Home Assistant appears to the lock as its own gateway, polling it locally over Bluetooth.

LibreNMS, added by @mib1185

Bring your LibreNMS network monitoring instance into Home Assistant. This initial release adds a binary sensor for the online status of each monitored device, with alerts and more sensor data planned for later.

NexBlue, added by @nexblue-maintainer

Connect a NexBlue EV charger account to Home Assistant. It discovers the chargers on your account and provides read-only sensors for charging state, power, session and lifetime energy, and other electrical and diagnostic values. Charging controls are planned for a future release.

Ridder HortiMaX Pro, added by @wildekek

Bring measurements from a Ridder HortiMaX Pro greenhouse controller into Home Assistant, including temperatures, humidity, vent and screen positions, irrigation volumes, and energy use. The integration is read-only, so your growing decisions stay fully in the controller’s hands. It’s the same kind of controller running the greenhouses at Amsterdam’s Hortus Botanicus, one of the oldest botanical gardens in the world, which we visited earlier Read the full story in our newsletter.

Samsung TV via ExLink, added by @balloob, launching at 🥈 silver quality

Control Samsung TVs through their RS-232 serial port, which Samsung markets as ExLink, using a serial cable, a USB-to-serial adapter, or an ESPHome-based serial proxy. Talking directly to the TV’s serial port makes control fast and reliable, and it also works with TVs that lack smart features or a network connection.

Silla Prism, added by @ebaschiera

Monitor a Silla Prism EV wallbox over its local MQTT API, with sensors for charging status, power, current, voltage, and session and lifetime energy. Setup only needs the MQTT topic your Silla app already shows you. Charging controls are planned for a future release.

Sofar Inverter Modbus, added by @darkrain-nl

Connect a Sofar Solar inverter to Home Assistant over Modbus TCP, either directly or through a Modbus TCP bridge. Setup automatically detects your inverter model, and it works with both PV-only and hybrid inverters with battery storage.

Specialized Turbo, added by @JamieMagee

Connect a Specialized Turbo e-bike over Bluetooth Low Energy, covering the TCU1 and TCX1 through TCX4 models, with detailed ride and battery telemetry. Encrypted bikes can sign in through your Specialized account or use a manually entered key, and Home Assistant manages the Bluetooth connection itself without storing your password.

Tonewinner, added by @emma-sg, launching at 🥈 silver quality

Control Tonewinner AV processors, receivers, and amps over an RS-232 serial connection, using a USB-to-serial adapter or an ESPHome-based serial proxy.

This release also has new virtual integrations. Virtual integrations are stubs that are handled by other (existing) integrations to help with findability. These ones are new:

Ariston, provided by Midea, added by @chemelli74

Beverly, provided by Midea, added by @chemelli74

Bugu, provided by Midea, added by @chemelli74

Carrier, provided by Midea, added by @chemelli74

Colmo, provided by Midea, added by @chemelli74

Comfee, provided by Midea, added by @chemelli74

Inventor, provided by Midea, added by @chemelli74

Little Swan, provided by Midea, added by @chemelli74

Netsu, provided by Midea, added by @chemelli74

Olimpia Splendid, provided by Midea, added by @chemelli74

Pro Breeze, provided by Midea, added by @chemelli74

Rotenso, provided by Midea, added by @chemelli74

Toshiba Lifestyle, provided by Midea, added by @chemelli74

Vandelo, provided by Midea, added by @chemelli74

Wahin, provided by Midea, added by @chemelli74

Noteworthy improvements to existing integrations

It is not just new integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] that have been added; existing ones keep getting better too. Here are some of the noteworthy improvements this release:

Tuya added support for the HCDD device category, covering chasing tape lights, so these RGB LED strips can be controlled like any other light. Thanks, @AnthonyZavala!

Shelly cameras are now fully supported, with a camera platform, motion detection, and a privacy switch to disable the lens. The Wall Display XL also gained its own motion sensor, and climate entities now report the correct heating and cooling status when a thermostat’s relay output is wired inverted. Thanks, @bieniu!

HomeKit Device gained duration, fault, and low battery sensors for more HomeKit accessories, so you can see how long a valve has been running, catch a failing accessory, and get a heads-up before a battery-powered sensor drops offline. Thanks, @nijel!

LG webOS TV added a switch to turn off just the screen while keeping the sound running, handy if you want to keep listening without the picture. Thanks, @darkrain-nl!

Reolink gained floodlight on/off schedule times, a button to synchronize the camera’s clock, a select to choose the anti-flicker frequency, and the ability to enable or disable the tamper alarm. Thanks, @Lukkasss and @starkillerOG!

Roborock brought dock controls, such as starting mop washing, drying, or emptying, to V1 vacuums. Thanks, @piitaya!

Google Gemini added a thinking budget option for Gemini 2.5 models and a thinking level option for Gemini 3 models, so you can tune how much the model reasons before it responds. Thanks, @mxwmnn!

Home Connect gained new event sensors, including short and long presses of the Favorite button on hobs and hoods, and a setpoint temperature option for air conditioners. Thanks, @Diegorro98!

Tado lets you choose which heating circuit serves a zone, handy in homes with more than one circuit, like a mix of underfloor heating and radiators. Thanks, @PeterLinuxOSS!

SwitchBot Cloud now supports the Permanent Outdoor Lights string lighting and the Curtain4 curtain motor, so you can control them from Home Assistant alongside the rest of your SwitchBot devices. Thanks, @XiaoLing-git!

KNX weather and select entities can now be created directly from the KNX panel in the UI, and YAML-defined entities can be given an explicit unique ID instead of relying on the auto-generated one. YAML entities can now also be assigned to devices. Thanks, @farmio and @martinhoefling!

Proxmox VE added a button to pause a VM, handy for freeing up resources for a moment, for example while another job needs the extra headroom, without fully shutting the VM down. Thanks, @erwindouna!

HomematicIP Cloud added a carbon dioxide sensor for supported devices, so you can trigger ventilation or an air purifier automation when CO2 levels creep up in a room. Thanks, @lackas!

VIZIO SmartCast now supports Crave portable speakers, with a battery level sensor and a charging binary sensor. Thanks, @raman325!

Environment Canada radar images can now be smoothed for a less blocky picture and extended with a short-term forecast, so you can see rain or snow coming before it actually arrives. Thanks, @michaeldavie!

MikroTik gained switches to turn Ethernet and Wi-Fi interfaces on or off, a select to set the PoE output mode, a binary sensor for interface connectivity, and more sensors, including a fix for incorrect voltage readings on the netPower 16P. Thanks, @chemelli74!

Mealie added actions to update and delete mealplan entries, so you can manage next week’s dinners from an automation or script instead of opening the app. Thanks, @andrew-codechimp!

Portainer added a Docker event entity, so container lifecycle changes reach Home Assistant immediately instead of waiting for the next update cycle. Thanks, @erwindouna!

Transmission added a sensor for available disk space, so you can get a warning before your download folder fills up. Thanks, @Eniot666!

Honeywell Lyric added a schedule status sensor, so you can tell at a glance whether your thermostat is following its schedule or someone put it on a temporary hold. Thanks, @clutch2sft!

Teslemetry added a rear defroster binary sensor, so you can automate it on a cold morning, and a cover entity for the Cybertruck’s tonneau, so you can open and close the bed cover from Home Assistant. Thanks, @Bre77!

IOmeter added entities for three-phase electricity meters, so homes with a three-phase connection get accurate readings for every phase instead of just the total. Thanks, @torben-iometer!

Modern Forms added support for breeze mode, which varies the fan speed to mimic a natural breeze. Thanks, @wonderslug!

Midea grew substantially this release, with new fan, humidifier, light, and switch controls, select and number entities to configure your appliance, buttons for common actions, and a full dust filter alert binary sensor. Thanks, @chemelli74!

Subaru added binary sensors for doors, windows, and the hood or tailgate, per-door lock status, EV plug and charging state, and vehicle health warning lights. Thanks, @jpettitt!

Anova cook time sensors now suggest hours as the displayed unit, making long cook times easier to read. Thanks, @goetzc!

iZone now shows the supply and return air temperatures of your ducted system, so you can spot a struggling compressor or a clogged filter before it becomes a bigger problem. Thanks, @Swamp-Ig!

Imou added a select entity to change night vision mode and volume, and a binary sensor for door and window contacts. Thanks, @Imou-OpenPlatform!

OpenEVSE added switches for solar PV divert, so you can charge from surplus solar power, the current shaper, which limits charging to protect your home’s electrical service, and a manual override to force charging on or off. Thanks, @firstof9!

Green Planet Energy added a get_prices action to fetch electricity prices for a given period, handy for building your own price charts or automations that react to tomorrow’s rates. Thanks, @petschni!

Vistapool added time entities for the three filtration schedule intervals, so you can adjust when your pool pump runs directly from Home Assistant instead of the Vistapool app. Thanks, @fdebrus!

ToGrill added a button to silence the alarm, handy when your food has reached temperature and you’d rather not walk over to the grill to quiet the beeping. Thanks, @thumbnail!

Watergate added a switch to turn the Sonic device’s automatic leak shut-off on or off. Thanks, @adam-the-hero!

IntelliClima added a binary sensor that reports when the filter needs cleaning. Thanks, @dvdinth!

Lyngdorf rounded out its debut with number entities for lip sync and channel trims, a remote entity to drive the processor’s on-screen menus, selects for RoomPerfect position and voicing, sensors for the active input and streaming source, and now-playing information with transport controls for models with a streaming module. Thanks, @fishloa!

Harbor Sleep added a select entity to set the camera’s night mode to Auto, On, or Off, so you can control it from Home Assistant instead of the Harbor app. Thanks, @Lash-L!

NeoPool added a pool light entity, plus an options flow to opt in to it, since the controller can’t detect whether a light is actually wired to the relay. Thanks, @svasek!

UniFi Protect can now be set up with just an API key from your UniFi OS Console, no local user account required. Select API key only (limited feature set) when adding the integration, or switch an existing entry over at any time. This first usable piece of the public API migration covers the alarm panel, cameras with their streams and snapshots, and lights. Sensors, switches, events, and media browsing are not available in this mode yet, and more platforms follow as they move over. Thanks, @RaHehl!

Integration quality scale achievements

One thing we are incredibly proud of in Home Assistant is our integration quality scale. This scale helps us and our contributors to ensure integrations are of high quality, maintainable, and provide the best possible user experience.

This release, we celebrate several integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] that have improved their quality scale:

3 integrations reached platinum 🏆

Google Health, thanks to @allenporter

LED Infrared, thanks to @tr4nt0r

WiiM, thanks to @balloob and @Linkplay2020

1 integration reached gold 🥇

BleBox devices, thanks to @bkobus-bbx

1 integration reached silver 🥈

Ouman EH-800, thanks to @Markus98

This is a huge achievement for these integrations and their maintainers. The effort and dedication required to reach these quality levels is significant, as it involves extensive testing, documentation, error handling, and often complete rewrites of parts of the integration.

A big thank you to all the contributors involved! 👏

Now available to set up from the UI

While most integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] can be set up directly from the Home Assistant user interface, some were only available using YAML configuration. We keep moving more integrations to the UI, making them more accessible for everyone to set up and use.

The following integrations are now available via the Home Assistant UI:

Flexit, done by @troelde

Netio, done by @agners

Remember The Milk, done by @MartinHjelmare

Farewell to the following

Time for a little cleaning, and no, we did not wait for spring! The following “integrations”Integrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] are no longer available as of this release:

VLC has been removed. It required direct access to your system’s audio hardware, which only worked on the deprecated Home Assistant CoreHome Assistant Core is the Python program at the heart of Home Assistant. It is part of all installation types. It can be installed standalone (without Home Assistant Supervisor) as a container using Docker (this is typically referred to as the Home Assistant Container installation type). For development, Core can also be run using a Virtual Environment (previously referred as the Home Assistant Core installation type). For production setup, the Home Assistant Core installation type is deprecated. installation method. This does not affect the separate VLC via Telnet integration, which remains available on any installation method.

Other noteworthy changes

There is even more packed into this release. Here are some of the other changes worth a mention:

Settings gained a new Connectivity page that groups Matter, Zigbee, Z-Wave, KNX, MQTT, Thread, Bluetooth, Serial, Infrared, Radio frequency, Insteon, and Tags behind a single entry, instead of listing each one directly in the settings menu. Every existing link keeps working, and Voice assistants moved down to join it as the settings root’s short second group. Thanks, @balloob!

Template got some more love this release. Thanks, @Petro31!

Custom attribute templates were added to alarm control panel, button, cover, device tracker, fan, image, light, lock, number, select, switch, update, and weather entities, alongside the binary sensor, event, sensor, and vacuum platforms that already supported them.

The attributes option is now fully templatable, cutting down on repeated Jinja2 templates.

Trigger-based template entities now support a per-entity conditions option. When set, the conditions block all updates to the entity it’s attached to.

Button triggers can now also fire from button helpers, alongside physical device buttons. Thanks, @abmantis!

Automation traces now show which entities, devices, and areas each step targeted, the same way the automation editor already does, instead of baking that information into the step’s own description. Thanks, @piitaya!

Cover open, close, and set position actions gained an optional speed parameter, so covers that support multiple speeds can be told how fast to move, not just where to. Thanks, @wollew!

The restart confirmation dialog now lists the automations and scripts currently running, instead of a vague warning that some might be interrupted. The list updates live as they start and stop. Thanks, @karwosts, @MindFreeze, and @NoRi2909!

The Energy dashboard now labels individual devices with their device name, not just the bare entity name, so devices that share a generic sensor name like Energy are easy to tell apart across the graphs, sankeys, and configuration list. Thanks, @MindFreeze and @silamon!

Dashboards gained a Background tab in their detail editor, so you can set a dashboard’s background straight from the UI instead of needing YAML. Thanks, @timmo001!

Searching the media browser now also reaches media players with their own library, such as Music Assistant, Sonos, Squeezebox, and Jellyfin, instead of only searching media sources. Thanks, @marcelveldt, @bramkragten, and @silamon!

Golden hour, blue hour, and polar sun automations

Rebuilding automationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more] around the sun has been a slow-burn project, and this release wraps it up. 2026.7 replaced the old, offset-heavy sun triggerA trigger is a set of values or conditions of a platform that are defined to cause an automation to run. [Learn more] with dedicated ones for sunrise, sunset, solar noon, solar midnight, dawn, dusk, and elevation changes, plus matching conditionsConditions are an optional part of an automation that will prevent an action from firing if they are not met. [Learn more] like is up, is night, and twilight. 2026.8 then added a time-based offset option to those triggers, the same way the calendar trigger already works, so you can fire an automation a set amount of time before or after a sun event.

This release adds the last of it to the Sun integration: four new conditions and eight matching triggers for golden hour, blue hour, midnight sun, and polar night. Golden hour and blue hour are the warm and cool light either side of sunrise and sunset, handy for automations that match your lighting to the mood outside, or close the blinds before direct sun hits a room. Each one can be limited to morning, evening, or either.

Farther from the equator, midnight sun and polar night cover the more extreme stretches of the year: the sun staying above the horizon for a full day around midsummer, or below it for a full day around midwinter. Both now have their own condition and start and end triggers too, so automations that only make sense at high latitudes finally have something to hook into. Documentation for the full set is still catching up.

Thanks, @emontnemery!

Accessibility for charts!

Making Home Assistant work for everyone isn’t a one-off project for us, it shows up release after release. Better color contrast and clearer buttons landed in 2025.8, clearer status indicators for people who can’t rely on color alone arrived in 2026.7, and this release, it’s charts’ turn.

Charts render straight to a single image, which means every data point on them has been invisible to screen readers and unreachable by keyboard. If you rely on either, a chart in Home Assistant might as well not have been there at all.

That changes this release. Tab into a chart and it becomes a real focus stop: the arrow keys walk you through it point by point, and a live region announces the time and value of each one to your screen reader. Press H at any point to bring up a list of every shortcut, styled to match your own theme.

Here’s the best part: as you move through a chart, Home Assistant also plays a short tone for each point, rising and falling with the data. You don’t just hear the individual numbers, you hear the shape of the whole trend, like a little melody. 🎵 It plays for anyone navigating a chart by keyboard, not only people using a screen reader, since there is no reliable way to know who needs it, so it’s on for everyone.

This works on your line and bar charts, including the device breakdown on the Energy dashboard. A few more specialized ones, like timelines, sankey diagrams, and network graphs, aren’t covered yet.

Thanks to @MindFreeze for bringing this to charts!

Serial and MQTT panels

Serial joins the other protocol panels under Settings > Connectivity, the same recognition infrared and radio frequency got over the last two releases. Once anything is using a serial port, whether that’s a USB dongle like a Zigbee or ThreadThread is a low-power mesh networking standard that is specifically designed for smart home applications. It is a protocol that defines how devices communicate. [Learn more] radio, or an appApps are additional standalone third-party software packages that can be installed on Home Assistant OS. [Learn more] talking to one, the new Serial page lists it.

It splits what it finds into three groups: ports actually in use by an integration or app, ports that are connected but not used by anything, and ports something expects but that aren’t currently plugged in. A status banner at the top gives you the numbers at a glance, so if a stick has come loose or an app lost its connection, you see it the moment you open the page instead of hunting through logs.

This rounds out the trio planned in an Open Home Foundation roadmap opportunity: serial, infrared, and radio frequency all have their own place in Settings now. Documentation for all three is still on its way.

Thanks to @puddly, who built this end to end, panel and all!

MQTT got a settings page of its own this release too, sitting right alongside Serial and Bluetooth in Connectivity instead of hiding its tools behind the integration’s options. A status banner at the top shows whether the broker is online and how many devices it’s found, with quick links to the devices and entities on your network. Discovery options and the broker connection settings each get their own row instead of sharing one options flow, and a new Publish a packet tool lets you send a test message, topic, QoS, and retain flag included, straight from the page, with a code editor for the payload. The topic subscribe view also now formats incoming messages as code, with a copy button. Thanks, @jbouwh!

How full is your network storage?

The Storage page in Settings has always shown which network shares you have connected, like a NAS for backupsHome Assistant has built-in functionality to create files containing a copy of your configuration. This can be used to restore your Home Assistant as well as migrate to a new system. The backup feature is available for all installation types. [Learn more] or media, but not how full each one actually was, so there was no early warning before one quietly ran out of room.

Each active mount now gets a small usage bar and a “{used} of {total} used” line. Rows appear immediately, and each bar fills in as soon as its own request comes back, so one slow or unreachable share never holds up the rest of the list. The bar also changes color as it fills, amber past 85% used and red past 95%, so you get a heads-up before you actually run out of space. A mount that’s currently unreachable just shows no usage bar; it already gets its own warning treatment.

Thanks to @MindFreeze and @silamon for keeping an eye on this!

Patch releases

We will also release patch releases for Home Assistant 2026.9 in September.
These patch releases only contain bug fixes. Our goal is to release a patch
release once a week, aiming for Friday.

2026.9.1 - September 5

Fix SMTP attaching valid images as files when content sniffing fails (@Chang-Jin-Lee - #176774)

Warn that removing an app deletes its data in repair flows (@agners - #181009)

Fix receive backup streaming (@MartinHjelmare - #181012)

Fix potential deadlock in receive_file backup util (@emontnemery - #181070)

Add missing state_class for miele filling level sensors (@astrandb - #181093)

Update python-roborock to 7.2.3 (@Lash-L - #181096)

Bump vizaio to 0.6.1 for vizio state_extended 404 fallback fix (@raman325 - #181131)

Stop rounding Amber Electric prices to 2 decimal places (@romeovan - #181157)

Fix host override ignored in UniFi Protect public-only mode (@RaHehl - #181176)

Purge unreachable deleted devices on device registry load (@emontnemery - #181207)

Bump pydaikin to 2.19.1 (hotfix) (@GhislainC - #181219)

Fix Besen config flow schema serialization (@moryoav - #181223)

Speed up lookup of colliding orphans in device registry (@arturpragacz - #181244)

Revert orjson to 3.11.9 (@emontnemery - #181245)

Bump aioflo to 2026.9.3 and scope Flo consumption by device (@BradKollmyer - #181246)

Bump serialx to 1.10.0 (@puddly - #181249)

Bump env-canada to 0.19.2 (@michaeldavie - #181250)

Bump python-hotspring to 2.1.0 (hotfix) (@Moustachauve - #181256)

Bump samsung-exlink to 1.1.1 (@balloob - #181260)

Reject Hot Spring Spa Network Adapter (SNA) in config flow (hotfix) (@Moustachauve - #181261)

Update knx-frontend to 2026.9.4.63549 (@farmio - #181268)

Allow empty motionEye usernames (@frenck - #181270)

Handle Tradfri devices without a firmware version (@frenck - #181276)

Update frontend to 20260826.6 (@bramkragten - #181293)

Bump reolink_aio to 0.21.15 (@starkillerOG - #181300)

Bump pylitterbot to 2025.6.5 (@natekspencer - #181346)

Bump uiprotect to 16.6.1 (@RaHehl - #180670)

2026.9.2 - September 11

Normalize Hive auth username before login (@Oluwatobi-Mustapha - #168827)

Don’t mutate the module level Roomba SENSORS list (@jasondillingham - #181107)

Fix Openhome players becoming unavailable between polls (@bazwilliams - #181238)

Clear webostv source when the current app is not in the source list (@darkrain-nl - #181381)

Bump adext to 0.4.7 (@Chang-Jin-Lee - #181384)

Bump midea-local to 11.0.1 (@chemelli74 - #181405)

Drop the unknown-app sentinel from vizio app_name on non-app inputs (@raman325 - #181417)

Add l/min unit mapping to nibe_heatpump sensors (@frankkopp - #181433)

Bump airos to 0.6.12 (@CoMPaTech - #181473)

Bump gcal-sync to 9.1.1 (@allenporter - #181499)

Add volume filter DF Portainer (@erwindouna - #181510)

Bump satel_integra to 1.4.0 (@Tommatheussen - #180960)

Bump satel-integra to 1.5.0 (@Tommatheussen - #181523)

Bump aiortm to 0.20.1 (@MartinHjelmare - #181524)

Fix unique_id for service entities in Alexa Devices (@chemelli74 - #181526)

Handle monitoring failure for Satel Integra (@Tommatheussen - #181548)

Fix Vizio soundbars requiring authentication (@raman325 - #181556)

Bump vizaio to 0.6.2 (@raman325 - #181562)

Improve error messages in remote_calendar (@allenporter - #181571)

Update local_todo to explicitly specify UTF-8 encoding for ICS storage (@allenporter - #181578)

Repair local_todo malformed ICS files with CRLF newlines on setup (@allenporter - #181581)

Redact credentials from go2rtc server log output (@balloob - #181583)

Fix MCP client double initialize in config flow (@allenporter - #181594)

Increase HTTP timeout in remote_calendar (@allenporter - #181599)

Bound Tesla Fleet vehicle first refresh with a timeout (@Bre77 - #181606)

Bump ZHA to 2.2.2, zha-quirks to 2.2.2 (@TheJulianJES - #181610)

Retry ViCare setup when the API quota is spent (@lackas - #181629)

Bump actron-neo-api to 0.5.16 (@kclif9 - #181639)

Rename Xbox follower sensor name to ‘Followers’ (@neyzm - #181654)

Fix shared wakelock across Tesla Fleet vehicles (@Bre77 - #181658)

Nest climate: recompute supported_features from live device traits (@rqi14 - #181660)

Bump waterfurnace to 1.9.0 (@sdague - #181746)

Bump python-roborock to 7.4.1 (@piitaya - #181754)

Retry sftp_storage setup when the SSH connection fails (@lackas - #181769)

Stream usage prediction events instead of loading them into memory (@balloob - #181770)

Bump pyatag to 0.3.7.1 (@JamieMagee - #181796)

Do not fail esphome setup when Supervisor is not ready (@balloob - #181805)

Report UniFi WAN latency as unknown when a monitor is unresponsive (@sdelmas - #181809)

Bump PyViCare to 2.62.1 (@lackas - #181830)

Bump reolink_aio to 0.21.16 (@starkillerOG - #181861)

Use PKCE for Weheat OAuth2 authorization (@barryvdh - #181881)

Bump python-roborock to 7.4.2 (@allenporter - #181907)

Preserve form values on error in Remote Calendar config flow (@allenporter - #181908)

Fix MELCloud Home energy interval (@erwindouna - #181937)

bump pyenphase to 4.0.3 (@catsmanac - #181940)

Update frontend to 20260826.7 (@bramkragten - #181950)

2026.9.3 - September 18

Fix EnergyZero market price regression (@klaasnicolaas - #181230)

Require the IRK in the Private BLE Device config flow (@frenck - #181969)

Keep the known Bond host when zeroconf still announces it (@frenck - #181975)

Fix function name in external statistics mean_type message (@Booyaka101 - #182031)

Fix Matter cover entity not created when tilt attribute is null for Shelly devices (@jowi24 - #182042)

Bump holidays to 0.104 (@gjohansson-ST - #182044)

Bump pylutron to 0.4.4 (@cdheiser - #182049)

Make Nest climate turn_on idempotent (@allenporter - #182086)

Increase Hot Spring polling interval to 60 seconds (@Moustachauve - #182150)

Fix Google Tasks error handling on DNS failure (@joostlek - #182195)

Fix Alexa doorbell raises error in state report becase the return status is NO_CONTENT (@jbouwh - #182209)

Bump hassil to 3.12.1 (@synesthesiam - #182213)

Encrypt and decrypt supervisor.tar in backup rewrites (@agners - #182220)

Bump waterfurnace to 1.9.2 (@sdague - #182019)

Bump waterfurnace to 1.9.7 (@sdague - #182263)

Redact the AirVisual API key in debug logging (@frenck - #182280)

Fix Spotify reauth crash when config entry data lacks “id” (@joostlek - #182290)

Validate username during onboarding before creating a new user (@edenhaus - #182320)

Fix missing f-string prefix in wiz error message (@David-Wu1119 - #182363)

Fix IMAP custom data event template option not reset when cleared (@jbouwh - #182377)

Fix duplicate devices in Airthings BLE on incomplete read (@joostlek - #182417)

Log exception when api fails in WAQI (@chemelli74 - #182419)

bump aioamazondevices to 15.2.0 (@jamesonuk - #182204)

Bump aioamazondevices to 16.3.0 (@chemelli74 - #182438)

Bump reolink_aio to 0.21.17 (@starkillerOG - #182472)

Need help? Join the community

Home Assistant has a great community of users who are all more than willing to help each other out. So, join us!

Our very active Discord chat server is an excellent place to be, and don’t forget to join our amazing forums.

Found a bug or issue? Please report it in our issue tracker to get it fixed! Or check our help page for guidance on more places you can go.

Are you more into email? Sign up for the Open Home Foundation Newsletter to get the latest news about features, things happening in our community, and other projects that support the Open Home straight into your inbox.

Backward-incompatible changes

We do our best to avoid making changes to existing functionality that might unexpectedly impact your Home Assistant installation. Unfortunately, sometimes it is inevitable.

We always make sure to document these changes to make the transition as easy as possible for you. This release has the following backward-incompatible changes:

Flexit Nordic (BACnet)

The deprecated fireplace mode switch entity has been removed. If you have automationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more] or scriptsScripts are components that allow you to specify a sequence of actions to be executed by Home Assistant when turned on. [Learn more] that use switch.<device>_fireplace_mode, use the climate.set_preset_mode action on the Flexit climate entity with preset_mode: fireplace instead.

(@magnusoverli - #179272) (Flexit Nordic (BACnet) documentation)

KNX

KNX exposes no longer send an entity’s first value to the KNX bus. Previously, this depended on timing: if the entity already had a value when the expose was set up, nothing was sent, but if the value arrived later, it was sent to the bus right away.

Now, both cases behave the same way. The first value is adopted locally without sending a telegram, but stays available for read requests and periodic sending. Later value changes are still sent as before.

To send the first value right away, turn on Send on initialization for the expose in the KNX panel, or set send_on_init: true in your YAML configuration.

(@Kolbi - #178793) (KNX documentation)

LLM APIs

LLM tool names are now prefixed with the domain of the integration that offers them. For example, GetLiveContext becomes homeassistant__GetLiveContext and HassTurnOn becomes intent__HassTurnOn. If you have a custom prompt that names a tool directly, update it to use the new prefixed name.

(@balloob - #179938)

Persistent Notification

Updating a persistent notification that already exists now triggers an update_type of updated instead of added. If you have an automationAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more] that triggers on an update_type of added to catch every new or changed notification, add updated to the list of types it triggers on.

(@davidlang42 - #171067) (Persistent Notification documentation)

UniFi Protect

The smart detection switches (for example Detections: Person, Detections: Vehicle, and the audio alarm toggles) are no longer hidden while recording is disabled. They now stay available and follow the same public API as the other camera configuration switches. Their entity IDs and what happens when you toggle them are unchanged.

(@RaHehl - #174963) (UniFi Protect documentation)

UniFi Protect 7.2.105 or newer is now required. On an older version, the integration stops setting up and tells you to update. Update UniFi Protect, then reloadApplies the changes made to Home Assistant configuration files. Changes are normally automatically updated. However, changes made outside of the front end will not be reflected in Home Assistant and require a reload. the integration.

(@RaHehl - #179954) (UniFi Protect documentation)

Update

Installing an updateAn update entity is an entity that indicates if an update is available for a device or service. [Learn more], skipping an update, and clearing a skipped update now require an administrator account. These are configuration-level actions, so they are now restricted to admins, like other sensitive actions in Home Assistant.

AutomationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more] are not affected, because they run without a user context. A scriptScripts are components that allow you to specify a sequence of actions to be executed by Home Assistant when turned on. [Learn more] runs in the context of the user who started it, so a script that installs or skips an update now fails when a non-admin user starts it. Trigger it from an automation instead, or start it as an admin.

(@balloob - #178232) (Update documentation)

Vacuum

The deprecated battery_level property has been removed from the base vacuum entity. All core vacuum integrations were already migrated in Home Assistant 2026.8. If a custom integration still sets this property, it no longer reports a battery level; add a separate battery sensor instead.

(@gjohansson-ST - #175682) (Vacuum documentation)

Z-Wave JS

The Z-Wave actions to manage lock users and credentials (set_user, delete_user, delete_all_users, set_credential, delete_credential, and delete_all_credentials) now require an administrator account.

(@balloob - #177300) (Z-Wave JS documentation)

If you are a custom integration developer and want to learn about changes and new features available for your integration: Be sure to follow our developer blog. The following changes are the most notable for this release:

Configurator integration is now deprecated

Device registry WebSocket API changes

More device registry deprecations, new helpers and validation

All changes

Of course, there is a lot more in this release. You can find a list of all changes made here: Full changelog for Home Assistant Core 2026.9.
