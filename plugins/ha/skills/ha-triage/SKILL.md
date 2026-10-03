---
name: ha-triage
description: >-
  Use when a Home Assistant custom integration misbehaves and the fault is not yet named —
  from a log, a traceback or a symptom — to find the class of fault and the file that owns
  the fix.
  TRIGGER WHEN:
  - reading `home-assistant.log`, or a traceback that names `custom_components`
  - an integration fails to set up, or its entities go unavailable, stale, missing or
  duplicated
  - an action or a panel of an integration stops working
  - an integration broke after a Home Assistant update
  SYMPTOMS:
  - `Setup failed for custom integration`
  - `Error setting up entry`
  - `Unexpected error fetching … data`
  - `Detected blocking call to … inside the event loop`
  - `Detected that custom integration … This will stop working in Home Assistant`
  - `does not generate unique IDs`
  NOT for writing the fix (ha-integration), nor for automations, dashboards, add-ons or the
  devices of core integrations.
---

# Home Assistant Triage

**Name the class of fault from a line core printed or a symptom someone saw, then open the
file that owns that class. A line count ranks nothing.**

## Detect the fault class

Match the line or the symptom to a row, then **read that row's file before naming a cause**.

| Mode | When | Read first | Source |
|---|---|---|---|
| **Read a log** | a log or a traceback with no class named yet | *Read a log* below | `async_enable_logging` in `homeassistant/bootstrap.py` |
| **Blocked at load** | `The custom integration '<domain>' does not have a version key in the manifest file and was blocked from loading`, or `does not have a valid version key (<version>) in the manifest file` | `ha-integration/reference/scaffold.md` | `homeassistant/loader.py` |
| **Setup fails** | `Setup failed for custom integration '<domain>'`, `Error setting up entry <title> for <domain>`, or `Error while setting up <domain> platform for <platform>` | `ha-integration/reference/patterns.md` | `homeassistant/setup.py`, `homeassistant/config_entries.py`, `homeassistant/helpers/entity_platform.py` |
| **Flow module** | `Error importing platform config_flow from integration <domain>` | `ha-integration/reference/testing.md` | `homeassistant/config_entries.py` |
| **Raised too late** | `<domain> raises exception <name> in forwarded platform <platform>; Instead raise <name> before calling async_forward_entry_setups` | `ha-integration/reference/patterns.md` | `homeassistant/helpers/entity_platform.py` |
| **Sign-in** | `Config entry '<title>' for <domain> integration could not authenticate`, or `Authentication failed while fetching <name> data` | `ha-integration/reference/patterns.md` | `homeassistant/config_entries.py`, `homeassistant/helpers/update_coordinator.py` |
| **Connection** | `Timeout fetching <name> data`, `Error requesting <name> data`, `Error fetching <name> data`; or entities unavailable until the integration is reloaded | `ha-integration/reference/patterns.md` | `homeassistant/helpers/update_coordinator.py` |
| **Unexpected reply** | `Unexpected error fetching <name> data`, `Unexpected error updating listener`, or a `ValueError` raised from a sensor's state | `ha-integration/reference/patterns.md` | `homeassistant/helpers/update_coordinator.py`, `homeassistant/components/sensor/__init__.py` |
| **Value wrong or stuck** | a state that reads `unknown` once the entity is added, or carries the wrong unit, with no line in the log | `ha-integration/reference/patterns.md` | — |
| **Entities duplicated** | `Platform <domain> does not generate unique IDs` | `ha-integration/reference/patterns.md` | `homeassistant/helpers/entity_platform.py` |
| **Devices** | a device missing, doubled or split after an update | `ha-integration/reference/patterns.md` | — |
| **Action** | an action reaches more devices than it was aimed at | `ha-integration/reference/patterns.md` | — |
| **Deprecation** | it worked before a Home Assistant update; or `Detected that custom integration '<domain>' … This will stop working in Home Assistant <release>` | `ha-integration/reference/patterns.md` | `homeassistant/helpers/frame.py` |
| **Blocking call** | `Detected blocking call to <function>`, or a `RuntimeError` beginning `Caught blocking call to` | `ha-integration/reference/patterns.md` | `homeassistant/util/loop.py` |
| **Panel** | the panel shows its previous version after an update, or a change made in its source is not there | `ha-integration/reference/panels.md` | — |
| **hassfest** | a red hassfest check on the manifest | `ha-integration/reference/scaffold.md` | — |
| **Naming the cause** | a class is matched and a root cause is about to be named | `ha-integration/reference/discipline.md` | — |

## Read a log

1. Count by logger, not by line — one fault can print a thousand lines, another one.
2. Keep the clusters that name a custom integration.
3. Read one line of each cluster in full, with its traceback, and match it to a row above.
4. Report one row per cluster: class · the line · the file that owns the fix · timestamp.

```bash
# 1. clusters, by level and logger, with the thread name dropped
grep -oE "(ERROR|WARNING|CRITICAL) \([^)]+\) \[[^]]+\]" LOG \
  | sed -E 's/ \([^)]+\)//' | sort | uniq -c | sort -rn
# 2. tracebacks, which the first count gives to their header line alone
grep -c "^Traceback" LOG
# 3. which integrations are named, by path, by logger, in the text of a core line, or as a platform
grep -oE "custom(_components[./]| integration '?)[a-z0-9_]+|Platform [a-z0-9_]+ does not|[a-z0-9_]+ raises exception" LOG | sort | uniq -c | sort -rn
# 4. one integration, with the lines after each hit
grep -n -A 25 -E "custom_components[./]<domain>|custom integration '?<domain>|Platform <domain> |<domain> raises exception" LOG
```

| Rule | Value |
|---|---|
| where each quoted line was read | core at the `.0` tag of the release row in `ha-integration/reference/freshness.md`, in the file the Source column names |
| `We found a custom integration <domain> which has not been tested by Home Assistant` | not a fault: logged at each start for every directory under `custom_components/` whose `manifest.json` parses, configured or not; not logged in safe or recovery mode |
| a line at INFO, such as `Config entry '<title>' for <domain> integration not ready yet … Retrying in <n> seconds` | absent from the log unless Home Assistant runs verbose or the `logger` integration lowers the level, since the root logger sits at WARNING; read the entry's state on the integrations page |
| a line that names no custom integration — by `custom_components` in its logger or traceback, by `custom integration '<domain>'` in its text, or by its domain as the platform, as the Raised too late and Entities duplicated lines do | not this skill's — an automation, a core integration or an add-on |
| a traceback | classed by the core line above it, and located by its last `custom_components/<domain>/` frame |

**Timing:** run the first command before reading any line, since a raw count is what
misleads.
