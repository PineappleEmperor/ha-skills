# 2026.8: Approachable by design

Fetched from https://www.home-assistant.io/blog/2026/08/05/release-20268/
Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of home-assistant/home-assistant.io.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Tip

Don’t forget to join our release party live stream on YouTube on August 5, 2026, at 20:00 GMT / 12:00 PT / 21:00 CET!

Tip

There’s more to look forward to next week: the ESPHome Starter Kit is launching, and you’re invited to the official launch party! 🚀 Join the ESPHome team and their partners at Apollo Automation on the ESPHome YouTube channel on August 12 at 21:00 CEST. Familiar faces are dropping by to celebrate lift-off, too: Reed from Smart Home Solver, Simon from Simon Says Home Assistant, and Gavin from HomeTech.fm.

Home Assistant 2026.8! 🎉

Hi, I’m Ashley, the Technical Program Manager at the Open Home Foundation. With Frenck taking a well-deserved break, Bram and I are teaming up to handle things this time around.

We have been working on a lot over the past few weeks, and I’m excited to share some of what we have done for this release!

If there’s one thread tying this release together, it’s a direction we care about: making Home Assistant something you don’t need to be technical to use. This release is another step along that path.

Enjoy the release!

- Ashley

Making Home Assistant more approachable

The same Home Assistant, minus the magic number

Your current setup keeps working

Want to change the port? We’ve got you covered

What this means for YAML

Less “advanced”, more approachable

Describing the feature, not the user

Just Tools, no developer required

Home Assistant Cloud, now easier to explore

Your entity IDs, your choice

A cleaner way to handle your devices

We can’t stop adding triggers and conditions

Integrations

New integrations

Noteworthy improvements to existing integrations

Integration quality scale achievements

Now available to set up from the UI

Farewell to the following

Other noteworthy changes

Tell us how setup went

A roomier template editor

Taps that land where you mean them

A combined battery level you can trust

Search your media

Find your favorite cards faster

Z-Wave lock credentials, properly managed

And a few more

Patch releases

2026.8.1 - August 7

2026.8.2 - August 14

2026.8.3 - August 21

Need help? Join the community

Backward-incompatible changes

All changes

A huge thank you to all the contributors who made this release possible! And a special shout-out to @frenck and @bramkragten who helped write the release notes this release. Also, @piitaya, @RaHehl, and @farmio for putting effort into tweaking its contents. Thanks to them, these release notes are in great shape. ❤️

Making Home Assistant more approachable

One of the directions we care about most for Home Assistant is making it simpler to pick up and use, without compromising on capability. It’s something we have been working toward for a long time, and it runs through our roadmap and goals for this year. We cannot do it overnight though, so we keep listening to your feedback to make sure we are fixing the things that actually get in your way. If there is something you would like to see, we would love for you to weigh in. Every comment helps shape what comes next.

This release brings together some of that work. It may never be truly finished, and that is fine, but it is something we hold close: the more people who can use Home Assistant, whatever their technical ability, the better.

The same Home Assistant, minus the magic number

Ever wondered why the address for your own home has a random number stuck on the end? So did we. For years, reaching Home Assistant meant remembering to add :8123 to the address, a little piece of technical trivia that everyone simply had to learn. This release starts to put that right.

New installations of “Home Assistant OS”Home Assistant OS, the Home Assistant Operating System, is an embedded, minimalistic, operating system designed to run the Home Assistant ecosystem on single board computers (like the Raspberry Pi) or Virtual Machines. It includes Home Assistant Core, the Home Assistant Supervisor, and supports apps. Home Assistant Supervisor keeps it up to date, removing the need for you to manage an operating system. Home Assistant Operating System is the recommended installation type for most users. now use a normal web address by default, with no number to add on the end. You reach your home the same way you reach any website. Nothing extra to remember, nothing extra to type.

Your current setup keeps working

If you are already running Home Assistant, nothing changes and there is nothing you need to do. This only affects new installations of Home Assistant OS. Your existing installation is completely unchanged, keeps the exact port it has always used, and keeps working just as before. If everything works today, the simplest thing is to leave it exactly as it is.

Want to change the port? We’ve got you covered

You do not have to change anything, but if you would like the cleaner address, or need to change the port for another reason, you can now do it yourself from the interface. The same screen also holds a few more options, like choosing which network connection Home Assistant listens on and setting trusted proxies, for the setups that need them.

Changing something as fundamental as the port your home lives on can feel nerve-wracking, so we made it hard to get stuck. When you change the web server settings, Home Assistant applies the new configuration and then waits for you to confirm everything still works. If you do not confirm within five minutes, it assumes something went wrong, puts your previous settings back, and restarts. And if the new settings cannot be applied at all, it falls back right away. So if you ever lock yourself out with the wrong setting, you do not have to do anything: wait a few minutes, and Home Assistant returns you to where you were.

Note

One thing to keep in mind: anything that reaches Home Assistant using the old address may need updating to match the new port, such as your bookmarks or other services and tools you have connected, including the mobile app. If your setup works today, that is a good reason to leave it as it is.

What this means for YAML

If you currently set up the web server in YAMLYAML is a human-readable data serialization language. It is used to store and transmit data in a structured format. In Home Assistant, YAML is used for configuration, for example in the configuration.yaml or automations.yaml files. [Learn more], you do not need to change anything. The first time you start Home Assistant after updating, your settings move into the interface for you, and you manage them there from then on. You might also see a repair appear, just to let you know your settings were imported; it can point you to tidying up the old YAML if you like, but nothing breaks either way.

Less “advanced”, more approachable

A word comes up around Home Assistant a lot: advanced. But what does it actually mean, and who gets to decide what counts as advanced and what does not? Too often it is a label that quietly tells people a feature is not for them. We want Home Assistant to be approachable for everyone, so this release removes some of that language.

Describing the feature, not the user

The clearest place to start is the words themselves. Labels like advanced and expert were dotted around Home Assistant. Words like these can be discouraging: they suggest a feature is not for you and steer you away from trying it, even when it is perfectly approachable. This release removes that wording in around 43 places, across the app, its documentation, and the companion apps. None of these features changed. Instead of rating your skill, the wording now simply describes what each one does.

A big thank you to everyone who helped comb through and clean this up! 👏

Just Tools, no developer required

In the same spirit, Developer Tools is now simply Tools. It has always been a useful spot for everyone, whether you are checking the stateThe state holds the information of interest of an entity, for example, if a light is on or off. Each entity has exactly one state and the state only holds one value at a time. However, entities can store attributes related to that state such as brightness, color, or a unit of measurement. [Learn more] of your “devices”A device is a model representing a physical or logical unit that contains entities., testing a templateA template is an automation definition that can include variables for the action or data from the trigger values. This allows automations to generate dynamic actions. [Learn more], or reloading part of your setup, and you never needed to be a developer to use it. The shorter name matches how people actually use it, and feels a little friendlier to open.

Home Assistant Cloud, now easier to explore

Home Assistant Cloud by Nabu Casa is how many people add remote access, fast and private voice, encrypted backupsHome Assistant has built-in functionality to create files containing a copy of your configuration. This can be used to restore your Home Assistant as well as migrate to a new system. The backup feature is available for all installation types. [Learn more], and more to their home, all while supporting the project at the same time. Until now, everything it offers lived on a single long page of switches and settings. This release gives that page a proper redesign.

The main page is now a clean overview. Each feature (remote access, backups, voice assistants, the companion app, and more) has its own space, so you can see what you have turned on at a glance. The settings for each one move onto their own page, which keeps the overview tidy and makes every feature easier to understand on its own.

The bigger change is for anyone just getting started. There is now a guided setup that walks you through Home Assistant Cloud step by step, instead of leaving you to find your way around a wall of options. If it is not a good moment, you can put it off and pick it up again later.

A big thank you to @klejejs for this redesign!

Your entity IDs, your choice

Behind every deviceA device is a model representing a physical or logical unit that contains entities. and sensorSensors return information about a thing, for instance the level of water in a tank. [Learn more] sits an entity ID, a short name such as light.kitchen_ceiling that your automationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more], scriptsScripts are components that allow you to specify a sequence of actions to be executed by Home Assistant when turned on. [Learn more], and dashboards use to refer to it. Most of the time they look after themselves. But when you do want them neat and consistent, you should be the one deciding how they read.

Some earlier work looked at building entity IDs automatically from the areaAn area in Home Assistant is a logical grouping of devices and entities that represents a room or space in your home, such as the living room, kitchen, or garage. [Learn more] a device belongs to. Your feedback told us this suited some people but not everyone. So this release takes a more flexible route and puts you in charge: you can rename an entity ID yourself, and control how it is ordered, so your entitiesAn entity represents a sensor, actor, or function in Home Assistant. Entities are used to monitor physical properties or to control other entities. An entity is usually part of a device or a service. [Learn more] follow whatever naming pattern makes sense to you.

Thanks to @arturpragacz and @piitaya for this work.

A cleaner way to handle your devices

Home Assistant is changing how it keeps track of your devices behind the scenes. Until now, if one physical deviceA device is a model representing a physical or logical unit that contains entities. was set up through two different integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more], Home Assistant merged them into a single device. Details that can only hold one value, such as the model or serial number, could then clash. From this release, each integration keeps its own device entry, so nothing gets collapsed together.

When you update, any devices that were merged this way are separated automatically, and their entitiesAn entity represents a sensor, actor, or function in Home Assistant. Entities are used to monitor physical properties or to control other entities. An entity is usually part of a device or a service. [Learn more] move to the right device for you. Most people will not notice a thing. In the rarer cases where a device was set up through more than one integration, you might see it appear twice, once per integration, and Home Assistant may raise a repair to let you know.

There is nothing you need to do. Your automationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more] and scriptsScripts are components that allow you to specify a sequence of actions to be executed by Home Assistant when turned on. [Learn more] keep working, because Home Assistant still sends actions to the right devices after the split. The only things that might need a second look are automations that point to a device by its ID directly, or the occasional unusual setup. If a repair appears, just follow it.

This is groundwork for more flexible device handling we are building toward over the coming months, so think of it as a step along the way rather than the finished picture.

If you build a custom integrationA custom integration is an integration that has been created by someone from the Home Assistant community and has been published for others to use at their own risk. Custom integrations are not supported by the Home Assistant project. They are not reviewed or tested by the Home Assistant development team and thus may negatively impact the stability of your Home Assistant instance. An example of a custom integration is the Spook integration., most need no changes at all. If yours works with device details directly, the developer blog walks through what changed. There is no rush: the previous approach keeps working for now, so you have plenty of time.

Thanks to @emontnemery for this work.

We can’t stop adding triggers and conditions

Last release, purpose-specific triggers and conditions became the friendlier way to build automationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more]: you describe the moment you care about, like when the front door opens, instead of piecing it together from the technical parts underneath. This release adds two more of them.

Vibration now has conditions to match its triggers. On top of reacting the moment vibration starts or stops, you can check whether something is vibrating (or not) as part of a bigger automation, for example, only sending a “laundry is done” message once the washing machine has actually stopped shaking.

Moon gains a trigger and matching conditions. You can start an automation the moment the moon enters a new phase, or check the current phase as part of a bigger automation. Point it at the full moon, the new moon, or any change of phase, and let your home take it from there, whether that is mood lighting, a reminder, or just a bit of fun. 🌙

Thanks, @nielsrowinbik!

Integrations

Thanks to our community for keeping pace with the new integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] and improvements to existing ones! You’re all awesome 🥰

New integrations

We welcome the following new integrations in this release:

Dyson Infrared, added by @elax46

Control your Dyson fans through any infrared transmitter you already have set up in Home Assistant. Because the connection only goes one way, Home Assistant shows the last command you sent rather than the fan’s live state.

Fuelprices.dk, added by @MTrab

Track current fuel prices from Danish fuel companies in Home Assistant. The integration pulls prices from the Fuelprices.dk service and creates a sensor for each product you select at a station, so you can watch prices and build automations around them.

Gatus, added by @TN-1, launching at 🥈 silver quality

Bring the health of your services into Home Assistant from your Gatus monitoring instance. Each monitored endpoint shows up as a binary sensorA binary sensor is an entity that reports one of two mutually exclusive states, on or off. The device class determines how those states are labeled in the UI. For example, open/closed for a door or detected/clear for motion. [Learn more], so you can put service status on a dashboard or trigger automations when something goes down or comes back up.

GeoSphere Austria Warnings, added by @tklecka

Bring official weather warnings for Austria into Home Assistant from GeoSphere Austria (formerly ZAMG), the national weather service. Warnings are issued per municipality and cover events like storms, heavy rain, snow, black ice, thunderstorms, heat, and cold, so you can get notified or trigger automations when the warning level rises.

Google Health, added by @allenporter

Bring your health and fitness data into Home Assistant from Google Health and the Fitbit Web API. After you connect your Google account, you get sensors such as steps, distance, weight, and resting heart rate, and it can run alongside the existing Fitbit integration.

Harbor Sleep, added by @Lash-L

Keep an eye on your Harbor Sleep baby monitor from Home Assistant. The integration connects to the device on your local network and exposes sensors like temperature, Wi-Fi strength, and stream quality.

Harman Luxury Audio, added by @sbesh91

Control network streamers built on the Harman Luxury Audio platform, such as the Arcam Radia ST5 and ST60, and equivalent JBL and Mark Levinson streamers. The integration talks to the device directly on your local network, so no cloud account is required.

Karakeep, added by @sli-cka

Connect your self-hosted Karakeep bookmarking service to Home Assistant and keep track of your bookmark statistics. Karakeep helps you save, organize, and tag links, notes, and images, and this integration surfaces those numbers as sensors.

LED Infrared, added by @tr4nt0r

Control LED lights through any infrared emitter you already have set up in Home Assistant. It supports many branded and unbranded bulbs and strip controllers that use generic infrared remotes. Communication is one-way, so the integration uses assumed states.

LiteLLM, added by @luismalves

Use a LiteLLM proxy as a conversation agent in Home Assistant. LiteLLM puts a single OpenAI-compatible API in front of many model providers, so you can reach almost any model through one endpoint, hosted or self-hosted. Home Assistant creates a conversation agent for each model you configure.

llama.cpp, added by @allenporter

Use a local llama.cpp server, or any OpenAI-compatible endpoint, as a conversation agent in Home Assistant. You can set up several agents, each with its own model and instructions, and keep everything running on your own hardware.

Lyngdorf, added by @fishloa, launching at 🥈 silver quality

Control Lyngdorf audio processors and amplifiers from Home Assistant, including power, volume, source selection, and sound modes. The integration keeps in sync with the device over your local network.

Midea, added by @chemelli74

Bring devices that use the Midea protocol, such as air conditioners and air purifiers, into Home Assistant. The integration provides information on the connected devices and lets you control their main features.

NeoPool, added by @svasek, launching at 🥈 silver quality

Monitor and manage pool controllers built on the NeoPool system, originally from Sugar Valley and sold under many brands like Hidrolife, Aquarite, and Oxilife. It talks to your controller locally over Modbus TCP, exposing water chemistry, filtration, and hydrolysis data with no cloud needed.

ScorpionTrack, added by @Herbertmt978, launching at 🥈 silver quality

Follow vehicles shared through a public ScorpionTrack location-share link on your Home Assistant map. The integration reads the shared vehicle feed and creates a device trackerDevice trackers are used to track the presence, or location, of a device. [Learn more] for each vehicle, without needing your private account credentials.

Noteworthy improvements to existing integrations

It is not just new integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] that have been added; existing ones keep getting better too. Here are some of the noteworthy improvements this release:

Shelly now supports Enhanced Security, the HTTPS-only mode on firmware 2.0 for gen2 and newer devices, and added support for Shelly circuit breakers, with on/off control plus output-state and safety-switch sensors. Thanks, @bieniu and @thecode!

Reolink gained pre-siren entities and a motion device class on its AI-detection binary sensors. Thanks, @starkillerOG and @abmantis!

Overkiz added window and tilt binary sensors for contact sensors, boost and drying-duration numbers for the Atlantic electrical towel dryer, and support for the Somfy Thermostat PRO. Thanks, @iMicknl!

SwitchBot added support for the Candle Warmer Lamp and the RGBIC Neon Rope Light, plus fan and select controls for the Standing Fan. Thanks, @Onero-testdev!

Roborock got plenty of love for the Q10, with a do-not-disturb switch, switch entities, a map image, and a volume control. Thanks, @lboue and @tubededentifrice!

Whirlpool added an oven light, an oven cook-mode select, and an oven target-temperature number. Thanks, @matthewdias and @bdlcalvin!

MQTT gained an infrared platform, so you can send infrared commands over MQTT. Thanks, @jbouwh!

KNX got a whole set of improvements. Button and notify entities can now be configured from the interface, the KNX panel gained a Send telegram dialog (keyboard shortcut s), plus a datapoint type (DPT) reference and a device view for your project data. On top of that, all KNX entities now restore their state after a reload or restart. Thanks, @farmio!

Enphase Envoy added ACB battery sensors, along with sleep and wake controls. Thanks, @genestealer!

MELCloud gained on/off control, an operation-mode select, and a flow-temperature number for air-to-water heat pump zones. Thanks, @imilchev!

MELCloud Home added energy-consumption reporting and a number platform. Thanks, @erwindouna!

Portainer added an update platform and container health status. Thanks, @erwindouna!

Mikrotik gained sensor, button, and update platforms. Thanks, @chemelli74!

Imou added switch and sensor platforms. Thanks, @Imou-OpenPlatform!

Fronius added a binary sensor for backup mode. Thanks, @farmio!

OpenAI Conversation now supports GPT-5.6. Thanks, @Shulyaka!

WiiM added multi-room grouping and metadata synchronization. Thanks, @Linkplay2020!

SMLIGHT added Bluetooth proxy support and an infrared receiver for SMLIGHT Ultima devices. Thanks, @tl-sl!

Vizio added command aliases for its remote. Thanks, @raman325!

Tesla Wall Connector added an option to switch total power calculation between single-phase / split-phase and three-phase electrical service, along with vehicle current and Wi-Fi signal sensors. Thanks, @sarabveer!

Teslemetry added control for seat coolers. Thanks, @Bre77!

Tessie added a navigation-destination text entity. Thanks, @Mattheinrichs!

Gardena Bluetooth added tank pressure and water temperature sensors. Thanks, @icereed!

Duco added ventilation temperature sensors. Thanks, @ronaldvdmeer!

Victron BLE added support for Orion XS and inverter devices. Thanks, @rajlaud!

OMIE added an action to get prices for a specific date. Thanks, @abmantis!

Ecowitt added soil conductivity sensor support. Thanks, @GSzabados!

Steam added an image platform, plus new Last online, Level, and Now playing sensors. Thanks, @tr4nt0r!

LG Infrared added support for LG air conditioners. Thanks, @Dr-Blank!

UniFi Protect now supports the USL smart sensors (USL Entry, USL Environmental, and USL GlassBreak) on UniFi Protect 7.2 and newer, and cameras gained Motion detection, Smart detection, and Sound detection event entities that fire for any detection the camera reports, such as a person, a package, or barking, with the detected type as an attribute. Thanks, @RaHehl!

Integration quality scale achievements

One thing we are incredibly proud of in Home Assistant is our integration quality scale. This scale helps us and our contributors to ensure integrations are of high quality, maintainable, and provide the best possible user experience.

This release, we celebrate several integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] that have improved their quality scale:

2 integrations reached platinum 🏆

Anthropic, thanks to @Shulyaka

SMLIGHT SLZB, thanks to @tl-sl

1 integration reached gold 🥇

Nobø Ecohub, thanks to @oyvindwe

5 integrations reached silver 🥈

Dropbox, thanks to @bdr99

Kiosker, thanks to @Claeysson

OpenWrt (luci), thanks to @kristbaum

STIEBEL ELTRON, thanks to @ThyMYthOS

WattWächter Plus, thanks to @smartcircuits

2 integrations reached bronze 🥉

Midea ccm15 AC Controller, thanks to @ocalvo

Netatmo, thanks to @cgtobi

This is a huge achievement for these integrations and their maintainers. The effort and dedication required to reach these quality levels is significant, as it involves extensive testing, documentation, error handling, and often complete rewrites of parts of the integration.

A big thank you to all the contributors involved! 👏

Now available to set up from the UI

While most integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] can be set up directly from the Home Assistant user interface, some were only available using YAML configuration. We keep moving more integrations to the UI, making them more accessible for everyone to set up and use.

The following integrations are now available via the Home Assistant UI:

AquaLogic, done by @j-mutter

OpenWrt (luci), done by @kristbaum

Farewell to the following

Time for a little cleaning, and no, we did not wait for spring! The following “integrations”Integrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] are no longer available as of this release:

Permobil has been removed. Permobil deprecated the API it relied on, so the integration could no longer retrieve any data, and there is no replacement available.

Volvo On Call has been removed. If you have a supported Volvo, set up the newer Volvo integration instead.

Other noteworthy changes

There are many more improvements in this release; here are some of the other noteworthy changes:

Tell us how setup went

If you have set up Home Assistant recently, you might notice a short, optional survey asking how your first experience went. It is entirely up to you, and every response helps us make getting started smoother for the next person. Thank you to everyone who shares their thoughts! 💛

A roomier template editor

The template tool in Tools is where you try out “templates”A template is an automation definition that can include variables for the action or data from the trigger values. This allows automations to generate dynamic actions. [Learn more] and watch the result update as you type. This release gives it a more comfortable layout: the editor and the result now sit in a split view you can drag to resize, and you can switch between side by side and stacked, whichever suits what you are working on. Your choice is remembered for next time.

Thanks, @maartenla!

Taps that land where you mean them

On the picture elements card, a tap could trigger the element next to the one you meant, or hit nothing at all, and some elements could not be tapped. Taps now go to the nearest icon or label, so every element can be reached, and tapping a label’s text always triggers that label. Thanks, @RaHehl!

A combined battery level you can trust

If you track more than one battery in the energy dashboard, you can now give each one a capacity. The combined state of charge is then weighted by size, so a small full battery and a large empty one no longer average out to a misleading number. Batteries without a capacity set keep using the plain average, so nothing changes unless you want it to. Thanks, @MindFreeze!

Search your media

Browsing for the right song, photo, or film used to mean clicking through folder after folder. Now, integrationsIntegrations connect and integrate Home Assistant with your devices, services, and more. [Learn more] that provide media can offer search right in the media browser, so you type what you are looking for and jump straight to it.

What you can search depends on the media source. Immich, for example, gained a smart search that finds photos by what is actually in them rather than by their filename, and Overseerr lets you search for and request movies and shows without leaving Home Assistant.

Thanks, @zweckj, @mib1185, and @felixschndr!

Find your favorite cards faster

Your most-used cards are now easier to find. In the card picker’s “By Card” tab, you can now mark the cards you use most as favorites using the icon in the corner of each card. Favorited cards float to the top of the section, so if you reach for the same card again and again while building similar dashboards, it’s always right there waiting for you. Tap the icon again to remove a card from your favorites.

Thanks, @piitaya, @laupalombi, and everyone who suggested this at a Release Party!

Z-Wave lock credentials, properly managed

Managing who can unlock your Z-Wave lock just got a lot more capable. Powered by Z-Wave JS’s new Access Control API, the Z-Wave JS app 1.6.0 brings a heavily revised interface: every supported lock now gets a dedicated Access Control tab. For now, this lives in Z-Wave JS UI rather than in the Z-Wave panel in Home Assistant.

Users, their credentials, and a full audit trail, all in one place.

Depending on what your lock supports, you can now give each user several credentials of more than one type, so the same person can have a PIN and a fingerprint, or multiple of both. New credentials can be learned on the lock itself: start the enrollment from the interface, then present the finger or type the PIN. There is also an audit log of every change, admin code management for locks that use one, and the ability to move credentials between users or delete them in bulk.

Update the Z-Wave JS app to 1.6.0 or later, then open Z-Wave JS UI to find the new tab. Thanks, @AlCalzone!

And a few more

There is even more packed into this release. Here are some of the other changes worth a mention:

Templates keep getting faster. Another round of “templates”A template is an automation definition that can include variables for the action or data from the trigger values. This allows automations to generate dynamic actions. [Learn more] performance work landed: templates with a numeric result are up to 40% faster, and templates used on dashboards can now be cached. Thanks, @frenck!

Template entities remember their state. Fan, coverCovers are devices such as blinds, garage doors, etc that can be opened and closed and optionally set to a specific position. [Learn more], and device trackerDevice trackers are used to track the presence, or location, of a device. [Learn more] template entities now restore their previous state after a restart, so they pick up right where they left off. Thanks, @Petro31!

Search finds more of what is connected. When you search or open a device or entity, Home Assistant now digs deeper into what is related, so scenes, scripts, groups, the people behind a person entity, and anything sharing a label or area all show up where you would expect them. It is a small change that makes it much easier to see how your setup fits together. Thanks, @frenck!

A reboot heads-up on Home Assistant OS. The system updateAn update entity is an entity that indicates if an update is available for a device or service. [Learn more] entity now lets you know when an update needs a reboot to finish. Thanks, @mdegat01!

A new radon device class. Sensors and numbers can now be classified as radon, so radon measurements get the right units and display. Thanks, @abmantis!

Filter entities by manufacturer and model. The entity filter can now narrow entities by manufacturer, model, and model ID. Thanks, @Skaronator!

Ask Assist from quick search. You can now start an Assist command straight from quick search. Thanks, @timmo001!

A date on the clock card. The clock card can now show the date alongside the time. Thanks, @timmo001!

More from the Activity panel. The Activity panel gained a CSV download and a clear-and-reset action. Thanks, @karwosts and @timmo001!

Patch releases

We will also release patch releases for Home Assistant 2026.8 in August. These patch releases only contain bug fixes. Our goal is to release a patch release once a week, aiming for Friday.

2026.8.1 - August 7

Fixes #173399 Seerr webhook registration (@shtefko - #177201)

Debounce Matter cover state writes to coalesce split attribute updates (@agners - #177540)

Bump pydaikin to 2.18.4 (@fredrike - #178001)

Adapt vicare to set via_device_id in DeviceInfo (@emontnemery - #178229)

Adapt mqtt to set via_device_id in DeviceInfo (@emontnemery - #178234)

bump pyenphase to 3.2.1 (@catsmanac - #178273)

Bump lyngdorf to 1.4.3 (@fishloa - #178323)

Track shielded service call task in REST API (@arturpragacz - #178377)

Bump aiowebostv to v0.9.1 (@thecode - #178384)

chore: update python-picnic-api2 to v2.0.1 (@codesalatdev - #178395)

Bump lyngdorf to 1.4.4 (@fishloa - #178401)

Use SmartThings cooling setpoint range for air conditioners (@StellarSea - #178430)

Bump solaredge-web to 0.3.1 (@tronikos - #178437)

Bump pytrydan to 1.0.5 (@dgomes - #178447)

mikrotik: Don’t reuse a string from Vodafone Station (@reedy - #178455)

Update frontend to 20260729.6 (@bramkragten - #178470)

2026.8.2 - August 14

Teslemetry: convert streamed tyre pressure and isolation resistance to their declared units (@Bre77 - #177541)

Handle inconsistence api response in Husqvarna Automower (@Thomas55555 - #178200)

Scope hassfest Docker manifest.json discovery to documented locations (@jabone - #178265)

Fix/tplink omada switch port refresh (@rubempoli - #178270)

Unload legacy notify actions in SMTP integration (@tr4nt0r - #176747)

Fix potential race condition in SMTP integration (@tr4nt0r - #178416)

Fix adaptive update interval Tado (@erwindouna - #178515)

Bump midea-local to 7.0.0 (@chemelli74 - #178535)

Bump python-bsblan to 6.1.8 (@liudger - #178561)

Victron GX: Fix regression in SSDP rediscovery with missing host (@tomer-w - #178585)

Bump evohome-async to v2.1.0 (@zxdavb - #178588)

Fix Reolink time import (@starkillerOG - #178597)

Add handle_safe_area opt-out to panel_custom and fix KNX panel (@farmio - #178598)

Use common logger in Mikrotik (@chemelli74 - #178602)

Fix sensors for Mikrotik (@chemelli74 - #178604)

Bump ical to 14.1.0 (@allenporter - #178626)

Update xknx to 3.19.0 (@farmio - #178652)

Bump aiolyric to 2.1.2 (@timmo001 - #178670)

Create hassio config entry during setup instead of deferring to started (@agners - #178677)

Handle Wyoming error events (@synesthesiam - #178696)

Bump homematicip to 2.14.1 (@lackas - #178701)

Report a refused alarm activation in homematicip_cloud (@lackas - #179139)

Fix missing optional gameserverip field in Steam Online dataclass (@tr4nt0r - #178751)

Fix delayed trains being dropped from Israel Rail departures (@mikomgk - #178773)

Bump lyngdorf to 1.4.9 (@fishloa - #178784)

Bump aiopvapi to 3.4.1 for hunterdouglas_powerview (@kingy444 - #178792)

Make tedee unknown during calibration and updates (@zweckj - #179048)

Bump blebox-uniapi to v2.5.7 (@bkobus-bbx - #179050)

Fix composed devices behind Matter bridge losing “via device” (@TheJulianJES - #179118)

Electric Kiwi: bugfix connections empty not checked (@mikey0000 - #179119)

Separate energy endpoint MELCloud Home (@erwindouna - #179124)

Update frontend to 20260729.7 (@bramkragten - #179131)

Bump incomfort-client to v0.7.1 (@jbouwh - #179134)

Bump py-nymta to 0.4.1 (@OnFreund - #179136)

Bump homematicip to 2.15.0 (@lackas - #179153)

2026.8.3 - August 21

Show artwork and a play button when opening a Sonos music library album (@bharat - #177510)

Pass config entry explicitly in Supla coordinator (@Fistacho - #178347)

Bump holidays to 0.102 (@gjohansson-ST - #179170)

errors could be None in Shelly Wall Display status (@bieniu - #179207)

Bump google-health-api to 0.9.0 (@allenporter - #179323)

Bump ical to 14.1.1 (@allenporter - #179325)

Fix Signal Messenger self notifications (@brozikcz - #179351)

Remove use of default_ device info in device_tracker (@emontnemery - #179380)

Remove use of default_ device info in dlna_dmr (@emontnemery - #179381)

Remove use of default_ device info in fritz (@emontnemery - #179382)

Remove use of default_ device info in netgear (@emontnemery - #179383)

Remove use of default_ device info in unifi (@emontnemery - #179384)

Remove use of default_ device info in wake_on_lan (@emontnemery - #179385)

Use dedicated translation on sensor entities if it’s Ecovacs mower (@edenhaus - #179416)

Revert host update on Overkiz local gateway rediscovery (@iMicknl - #179422)

Fix Vizio media player crash when volume is missing from audio settings (@raman325 - #179431)

Fix KeyError in Shelly integration for LinkedGo ST802 in floor heating mode (@bieniu - #179435)

Invalidate conversation slot-list cache on device registry changes (@emontnemery - #179486)

Log warning when event triggers filter on composite device (@emontnemery - #179490)

Bump holidays to 0.103 (@gjohansson-ST - #179500)

Remove just go2rtc sessions of the failing camera (@edenhaus - #179534)

Bump reolink-aio to 0.21.9 (@starkillerOG - #179625)

bump pyenphase to 4.0 and add required None handling and tests (@catsmanac - #179673)

Bump volvocarsapi to v0.4.4 for the Volvo integration (@thomasddn - #179712)

Bump aiowebostv to 0.9.2 (@thecode - #179757)

Need help? Join the community

Home Assistant has a great community of users who are all more than willing to help each other out. So, join us!

Our very active Discord chat server is an excellent place to be, and don’t forget to join our amazing forums.

Found a bug or issue? Please report it in our issue tracker to get it fixed! Or check our help page for guidance on more places you can go.

Are you more into email? Sign up for the Open Home Foundation Newsletter to get the latest news about features, things happening in our community, and other projects that support the Open Home straight into your inbox.

If you would like to wear your support: the Open Home Foundation store just added new T-shirts featuring ESPHome, Music Assistant, and a fresh Home Assistant design, all in classic black (or Dark Mode, if you prefer!). They are versatile, built to last, and best of all, every purchase helps fund the foundation’s work. Grab yours from the store.

Backward-incompatible changes

We do our best to avoid making changes to existing functionality that might unexpectedly impact your Home Assistant installation. Unfortunately, sometimes it is inevitable.

We always make sure to document these changes to make the transition as easy as possible for you. This release has the following backward-incompatible changes:

AirNow

The station radius option has been removed. The 2026 AirNow API no longer uses a distance parameter, so the radius had no effect on which reporting station was used. Existing entries are updated automatically, and any radius you had set is discarded. No action is needed.

(@derekcentrico - #176740) (AirNow documentation)

Gardena Bluetooth

The valve’s activation_reason sensor now reports a fixed set of values instead of free-form text. If you have automationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more], scriptsScripts are components that allow you to specify a sequence of actions to be executed by Home Assistant when turned on. [Learn more], or “templates”A template is an automation definition that can include variables for the action or data from the trigger values. This allows automations to generate dynamic actions. [Learn more] that match on the old text values, update them to match the new ones.

(@elupus - #177187)

Edifier Infrared

If you set up the Edifier Infrared integration for the R2000DB or R2730DB speakers, some buttons were mapped to the wrong infrared codes (on the R2730DB, power and mute were swapped). The mappings are now corrected and migrated automatically. If you built automationsAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more] or scriptsScripts are components that allow you to specify a sequence of actions to be executed by Home Assistant when turned on. [Learn more] around the old, incorrect buttons, update them to match.

(@abmantis - #177472) (Edifier Infrared documentation)

Ohme

The Ohme energy sensor has been removed. It reported an estimate of the energy stored in the car’s battery rather than the energy delivered by the charger, which caused confusing jumps in the energy dashboard, and the vendor’s API no longer provides a useful value.

If you tracked this sensor, use an Integration - Riemann sum helperA helper is a virtual entity you create inside Home Assistant. It is not backed by a physical device. Helpers store values, track state, or do calculations that your automations and dashboards need. [Learn more] on a power sensor to estimate the energy instead.

(@dan-r - #174664) (Ohme documentation)

Paperless-ngx

Paperless-ngx now requires a newer version of your Paperless-ngx server. The minimum supported server version is raised to 2.19, which also restores compatibility with Paperless-ngx 3.0. If your Paperless-ngx server is on version 2.18 or older, update it before you update Home Assistant.

(@IngmarStein - #176889) (Paperless-ngx documentation)

Robot vacuums

The deprecated battery_level property has been removed from the vacuum entitiesAn entity represents a sensor, actor, or function in Home Assistant. Entities are used to monitor physical properties or to control other entities. An entity is usually part of a device or a service. [Learn more] of several integrations. If you use a robot vacuum’s battery level in an automationAutomations in Home Assistant allow you to automatically respond to things that happen in and around your home. [Learn more], scriptScripts are components that allow you to specify a sequence of actions to be executed by Home Assistant when turned on. [Learn more], or on a dashboard, use the vacuum’s battery sensor instead.

This affects the following integrations:

LG ThinQ

Neato

Romy

Shark IQ

SwitchBot Cloud

Template

TP-Link

Xiaomi Miio

(@gjohansson-ST - #175681, #175684, #175685, #175686, #175687, #175688, #175691, #175764)

ScreenLogic

The option to configure the pollingData polling is the process of querying a device or service at regular intervals to check for updates or retrieve data. By defining a custom polling interval, you can control how frequently your system checks for new data, which can help optimize performance and reduce unnecessary network traffic. [Learn more] interval has been removed from ScreenLogic. Home Assistant now polls the integration at a fixed interval. If you need a different update frequency, you can set your own polling interval or trigger an update with the homeassistant.update_entity action.

(@Pinball3D - #175576) (ScreenLogic documentation)

UniFi Protect

Support for UniFi Protect AI Port devices has been removed. These devices only ever exposed diagnostic sensors, all disabled by default, and are not part of the UniFi Protect public API the integration is moving to. The AI Port device and its sensors are removed automatically when you update. You can still configure the AI Port directly in UniFi Protect.

(@RaHehl - #174378) (UniFi Protect documentation)

Detection scores are no longer available. The detection binary sensors (motion, person, vehicle, animal, and the smart-audio alarm sensors) now take their state from the UniFi Protect public API, which carries no per-event score, so their event_score attribute is gone and automations that filter on it need another condition. The event id and the detected types moved to the new Motion detection, Smart detection, and Sound detection event entities.

(@RaHehl - #174948) (UniFi Protect documentation)

UniFi Protect 7.1 or newer is now required. On an older console the integration reports that the version is too old instead of setting up. Update UniFi Protect to 7.1 or newer to keep using it.

(@RaHehl - #177620) (UniFi Protect documentation)

Volvo On Call

The Volvo On Call integration has been removed. If you have a supported Volvo, set up the newer Volvo integration instead.

(@gjohansson-ST - #175677)

If you are a custom integration developer and want to learn about changes and new features available for your integration: Be sure to follow our developer blog. The following changes are the most notable for this release:

Devices are restricted to a single config entry and at most one subentry

Introducing the Open Home Foundation AI Policy

Media sources can now be searched

Modernizing Modbus in Home Assistant

Standard event types for button event entities

All changes

Of course, there is a lot more in this release. You can find a list of all changes made here: Full changelog for Home Assistant Core 2026.8.
