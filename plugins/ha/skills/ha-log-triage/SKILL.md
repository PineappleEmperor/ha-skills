---
name: ha-log-triage
description: Use when reading a Home Assistant log — a `home-assistant.log`, a Settings → System → Logs download, or a pasted log dump — and the question is what is actually wrong. Reach for it on "thousands of errors after restart", "what is spamming my log", "is this error real or noise", a repeating `websocket_api` pending-messages burst, `extra keys not allowed` from a script or automation, a `notify.mobile_app_*` service that stopped existing, or a Z-Wave value id that no longer resolves. Also when a companion-app notification image works on Wi-Fi but fails on cellular. NOT for writing integration code — that is the `ha-integration` skill.
---

# Home Assistant Log Triage

This skill is self-contained: everything is in this file, and there is no `reference/` directory to open.

Input is a `home-assistant.log`, a **Settings → System → Logs** download, or a pasted dump.
Turn thousands of log lines into a short ranked list of *actionable* issues, separating real
faults from the background noise HA emits constantly.

**A raw error count is meaningless** — one slow client emits 1000+ identical lines; one config
typo emits one. Rank by distinct root cause, never by line count.

Most of what a log reports is config, automation or external-device trouble rather than
integration code. When a cluster does land under `custom_components.<domain>`, hand off to the
`ha-integration` skill.

### Step 1 — Build (or load) the device inventory FIRST

Logs identify clients/devices by **opaque tokens** — an IP, a browser user-agent, a Z-Wave `node_id`, a `notify.mobile_app_*` slug, a UniFi/camera hostname. Triage stalls every time on "what *is* `192.168.1.42`?". Resolve it **once**, up front, into a persistent map so every future triage is instant.

**The map is user/environment-specific — it does NOT belong in this (shareable) skill repo.** Keep it in a **local, git-ignored file next to the logs** (e.g. `device_map.md` in the log directory) or in Claude auto-memory. Never commit a home's IP/device layout to a public repo.

**Up-front Q&A** — when no map exists, extract the distinct tokens from the log and ask the user to name each once:

```bash
# Web/app clients: IP + device fingerprint (SM-X210 = Galaxy Tab, KFTRPWI = Amazon Fire, etc.)
grep -oE "from [0-9.]+ \(Mozilla[^)]*Build/[^ ;]+" LOG | sort -u
# All LAN IPs by frequency
grep -oE "192\.168\.[0-9]+\.[0-9]+" LOG | sort | uniq -c | sort -rn
# Named device tokens worth resolving
grep -oE "mobile_app_[a-z0-9_]+|node_id=[0-9]+|notify\.[a-z0-9_]+" LOG | sort | uniq -c | sort -rn
```

Then ask the user to fill **device · room/owner · role** for each token. Store as a table:

```markdown
| Token | Device | Room / owner | Role |
|-------|--------|--------------|------|
| 192.168.1.42 (SM-X210) | Android tablet | Kitchen | Wall dashboard |
| node_id=3 | Z-Wave keypad | Front door | Alarmo front pinpad |
| notify.mobile_app_pixel | Phone | (owner) | Alarm notifications |
```

Decode common fingerprints without asking: `SM-*` = Samsung Galaxy (Tab/phone), `KF*`/`Build/PS*` = Amazon Fire, `Pixel*` = Google Pixel, `iPad`/`iPhone` = Apple. Ask only for room/role.

### Step 2 — Aggregate by logger, not by line

```bash
grep -oE "(ERROR|WARNING) \([^)]+\) \[[^]]+\]" LOG | sort | uniq -c | sort -rn
```

Collapse each logger cluster to one row. Then read **one representative line** per cluster — not all of them.

### Step 3 — Classify each cluster: noise vs actionable

**Known noise — acknowledge once, do not chase:**

| Pattern | Why it's noise |
|---------|----------------|
| `[homeassistant.loader] We found a custom integration X which has not been tested` | Boot banner, **one per HACS integration**, every restart. Count ≈ number of custom integrations. Benign. |
| `[websocket_api.http.connection] ... Reached 4096 pending messages` | A **single slow client** can't drain the state_changed queue — almost always a tablet/dashboard right after restart. Check it's **one IP** over a **bounded window** (resolve the IP via the map). Self-heals on reconnect. Burst at boot = client weight, not a code bug; *continuous* = genuinely overloaded dashboard (trim history-graph / auto-entities cards). |
| `[snitun.*]`, `ClientConnectionResetError`, `Task exception was never retrieved` | Nabu Casa Cloud / network transients. Ignore unless frequent + correlated with an outage. |
| transient device fetch (`spotify`, `apple_tv`/`pyatv`, weather) | One-off API/device blips. Ignore unless sustained — sustained → that integration's reauth/availability. |

**Actionable — real bugs to fix:**

- **`extra keys not allowed @ data['<key>']`** in a script/automation `call_service` → a **service-schema deprecation**. The big recurring one: `light.turn_on` dropped **`color_temp`** → use **`color_temp_kelvin`** (kelvin = `1000000 / mired`). Also `white_value` (removed), `effect` keys that moved. Grep config for the dead key and replace.
- **`Action notify.mobile_app_* not found`** / **`Service … not found`** → a referenced entity/service was renamed or its device removed (re-onboarded phone, deleted integration). Update the automation/Alarmo action to the current slug.
- **Z-Wave `NotFoundError: Value N-CC-… not found on node Node(node_id=N)`** → a `zwave_js.set_value` targets a value id the node no longer exposes (re-interview, firmware change, wrong endpoint). Resolve `node_id` via the map, re-check the value id in the device's Z-Wave page.
- **`Bad credentials` / auth errors** (`github`, etc.) → expired token/PAT. Reconfigure that integration.
- **Anything under `custom_components.<your_domain>`** → your code. Trace it (publish→subscribe→handler) per *Debugging discipline* in the `ha-integration` skill (`ha-integration/reference/discipline.md`); this is the only cluster the rest of this skill directly acts on.

### Step 4 — Report

Ranked table: **severity · cluster · root cause · fix · evidence (`timestamp` / `file:line`)**. State explicitly which clusters are *known noise* (so the user stops worrying about a scary count) and which are *actionable*. Resolve every opaque token through the device map so the report reads in plain device names ("Kitchen wall tablet", not `192.168.1.42`). If a fix is config-side (scripts/automations/integration settings) and you only have the log, say so and offer to apply it once given the config path.

### Companion-app notification images (off-network delivery)

Recurring config-side fix: a `notify.mobile_app_*` image "works on Wi-Fi, fails on cellular". Root cause is always that the **phone** downloads the attachment over the internet through Nabu Casa — so anything only reachable on the LAN, or served stale, breaks off-network. Three causes:

1. **Hardcoded LAN / internal URL** (`http://192.168.x.x…`, an `internal_url`-based absolute) — unreachable off-network. Use a **relative** path; the companion app prepends the *active* base URL (cloud when remote) and adds auth.
2. **Legacy `attachment: { url, content-type }`** or a bad MIME (`content-type: jpeg` → must be `image/jpeg`). Prefer the modern **`image:`** key — most robust internal↔external resolution + auth.
3. **Stale CDN cache** — the killer. A snapshot written to a **fixed** `/config/www/…` filename and served via `/local/…` gets cached by Nabu Casa's CDN: off-network you receive the *previous* image (or a pre-first-write 404). Compounded by a **write→push race** (the push beats the file flush).

Fixes, best first:
- **`image: /api/camera_proxy/camera.<name>`** — no file, no race, no static cache, authenticated, resolves via cloud. Frame at fetch time (~live). Best for camera alerts; lets you delete the whole `camera.snapshot` step.
- **Point at a public URL directly** when the image is already internet-hosted (e.g. a YouTube thumbnail `https://i1.ytimg.com/vi/<id>/hqdefault.jpg`) — skip HA entirely; drop any `downloader.download_file` + `delay` steps.
- **Keep a frozen local snapshot** only if you must: switch `attachment`→`image:`, add a cache-buster `?v={{ now().timestamp() | int }}`, and a ~1 s `delay` after `camera.snapshot` so the write flushes.
- iOS attachment cap is **10 MB**. Give each alert source a **distinct `tag:`** — a reused tag means a new alert *replaces* the previous one on the lock screen.

> **Scope note:** most HA log errors are **config / automation / external-device** issues, *not* custom-integration code — this skill triages and routes them, but the editing patterns in the `ha-integration` skill apply only to the `custom_components.<your_domain>` cluster. Don't add a home's specific errors to this skill; add only a **new reusable noise/actionable *pattern*** here when one recurs across triages.
