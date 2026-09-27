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
  - an action, a config flow or a panel of an integration stops working
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
Every file named is under `ha-integration/reference/`, and every quoted line was read in core at the
`2026.9.0` tag, in the file the Source column names.

| Mode | When | Read first | Source |
|---|---|---|---|
| **Read a log** | a log or a traceback with no class named yet | *Read a log* below | `async_enable_logging` in `homeassistant/bootstrap.py` |
| **Blocked at load** | `The custom integration '<domain>' does not have a version key in the manifest file and was blocked from loading`, or the same with `a valid version key` | *Step 6: Order `manifest.json`* in `ha-integration/reference/scaffold.md` | `homeassistant/loader.py` |
| **Setup fails** | `Setup failed for custom integration '<domain>'`, `Error setting up entry <title> for <domain>`, `Error importing platform config_flow from integration`, or `Error while setting up <domain> platform for <platform>` | *Step 3: Wire the entry setup and unload* in `ha-integration/reference/patterns.md` | `homeassistant/setup.py`, `homeassistant/config_entries.py`, `homeassistant/helpers/entity_platform.py` |
| **Setup retried too late** | `<domain> raises exception ConfigEntryNotReady in forwarded platform <platform>; Instead raise ConfigEntryNotReady before calling async_forward_entry_setups` | *A connection that drops — Step 1* in `ha-integration/reference/patterns.md` | `homeassistant/helpers/entity_platform.py` |
| **Sign-in** | `Config entry '<title>' for <domain> integration could not authenticate`, `Authentication failed while fetching <name> data`, or a request to sign in again that keeps returning | *`config_flow.py` — Step 1* in `ha-integration/reference/patterns.md` | `homeassistant/config_entries.py`, `homeassistant/helpers/update_coordinator.py` |
| **Connection** | `Timeout fetching <name> data`, `Error requesting <name> data`, `Error fetching <name> data`; or entities unavailable until the integration is reloaded | *A connection that drops — Step 1* in `ha-integration/reference/patterns.md` | `homeassistant/helpers/update_coordinator.py` |
| **Unexpected reply** | `Unexpected error fetching <name> data`, `Unexpected error updating listener`, or a `ValueError` from a sensor — `which is not in the list of options provided`, `it has the non-numeric value`, `which is missing timezone information` | *A reply the code does not expect — Step 1* in `ha-integration/reference/patterns.md` | `homeassistant/helpers/update_coordinator.py`, `homeassistant/components/sensor/__init__.py` |
| **Value wrong or stuck** | a state that reads `unknown` once the entity is added, never changes, or carries the wrong unit, with no line in the log | *Entity platform files — Step 1* in `ha-integration/reference/patterns.md` | — |
| **Entities missing or duplicated** | `Platform <domain> does not generate unique IDs`, `Entity id already exists - ignoring`, `Error adding entity`, or `Not adding entity with invalid device info` | *Entity platform files — Step 1* in `ha-integration/reference/patterns.md` | `homeassistant/helpers/entity_platform.py` |
| **Devices** | a device missing, doubled or split after an update, or a warning naming the device registry | *Devices belong to one config entry — Step 3* in `ha-integration/reference/patterns.md` | — |
| **Action does nothing** | an action returns with no effect, or reaches more devices than it was aimed at | *Custom services — Step 1* in `ha-integration/reference/patterns.md` | — |
| **Flow** | the config or options flow will not open, or aborts | *`config_flow.py` — Step 1* in `ha-integration/reference/patterns.md` | — |
| **Deprecation** | `Detected that custom integration '<domain>' … This will stop working in Home Assistant <release>` | *Deprecated platform APIs — Step 1* in `ha-integration/reference/patterns.md` | `homeassistant/helpers/frame.py` |
| **Broke after an update** | it worked before the update — `Setup failed for custom integration '<domain>': Unable to import component`, or a call core no longer has | *Deprecated platform APIs — Step 1* in `ha-integration/reference/patterns.md` | `homeassistant/setup.py` |
| **Blocking call** | `Detected blocking call to <function> … inside the event loop by custom integration '<domain>'`, or a `RuntimeError` beginning `Caught blocking call to` | *A blocking call inside the event loop — Step 1* in `ha-integration/reference/patterns.md` | `homeassistant/util/loop.py` |
| **Panel** | the panel shows its previous version after an update, or a change made in its source is not there | `ha-integration/reference/panels.md` | — |
| **hassfest** | a red hassfest check | *`services.yaml` + `strings.json` (hassfest rules) — Step 1* in `ha-integration/reference/patterns.md` | — |
| **Naming the cause** | a class is matched and a root cause is about to be named | *Debugging discipline* in `ha-integration/reference/discipline.md` | — |

## Read a log

1. Count by logger, not by line — one fault can print a thousand lines, another one.
2. Keep the clusters a custom integration stands behind.
3. Read one line of each cluster in full, with its traceback, and match it to a row above.
4. Report one row per cluster: class · the line · the file that owns the fix · timestamp.

```bash
# 1. clusters, by level and logger
grep -oE "(ERROR|WARNING|CRITICAL) \([^)]+\) \[[^]]+\]" LOG | sort | uniq -c | sort -rn
# 2. which integrations are named at all
grep -oE "custom_components[./][a-z0-9_]+" LOG | sort | uniq -c | sort -rn
# 3. one cluster, with the lines after each hit
grep -n -A 25 "\[custom_components.<domain>" LOG
```

| Rule | Value |
|---|---|
| `We found a custom integration <domain> which has not been tested by Home Assistant` | not a fault: logged at each start for every directory under `custom_components/` that holds a `manifest.json`, configured or not |
| a line at INFO, such as `Config entry '<title>' for <domain> integration not ready yet … Retrying in <n> seconds` | absent from the log unless Home Assistant runs verbose — the root logger sits at WARNING; read the entry's state on the integrations page |
| a line no `custom_components` frame or logger stands behind | not this skill's — an automation, a core integration or an add-on |
| a traceback | classed by the core line above it, and located by its last `custom_components/<domain>/` frame |

**Timing:** run the first command before reading any line, since a raw count is what
misleads.
