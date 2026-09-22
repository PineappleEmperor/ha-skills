# Refreshing the skill for a new Home Assistant release

Repo-local, and maintenance of this repository rather than anything a scaffolded integration
carries — which is why it is here and not in the shipped `reference/freshness.md`. That file
holds the values; this holds the pass that moves them.

`scripts/check_ha_release.py` fails once PyPI's `homeassistant` minor is ahead of the release
row of `plugins/ha/skills/ha-integration/reference/freshness.md`. This is the pass that
clears it.

**Core rule:** a post says *what* changed and *why*. Core at the tag says everything else.

## Contents

1. Step 1: Pull the release's sources
2. Step 2: Read both sources
3. Step 3: Settle every claim against core at the tag
4. Step 4: Write the rows, then move the release cell
5. The terms the fetched copies are kept under

## Step 1: Pull the release's sources

```
python3 scripts/fetch_ha_sources.py --release <the new minor>
```

| Rule | Value |
|---|---|
| what it writes | the window's developer-blog posts, and the *Backward-incompatible changes* section of the release-notes post, into `docs/ha-release/<minor>/` with an index beside them |
| `--since <older minor>` | widens the window, for a backfill across several releases |
| what to commit | what it wrote |
| why it is not a convenience | the governance gate refuses a patch to the skill's `reference/` that names a release until that release's fetched sources have been served |
| exactly what it demands | `unread_sources` in `scripts/governance_gate.py`, which is the one statement of that rule |
| what the gate proves | that the sources which exist for the release were read — never that what you wrote is true |

## Step 2: Read both sources

Neither contains the other.

| Rule | Value |
|---|---|
| developers.home-assistant.io/blog, paged back to the last captured release | the only place most API changes are explained; a release's notes link a few of its window's posts and the rest are reachable only from the blog index |
| the release-notes post's *Backward-incompatible changes* section | user-facing removals, most of which never get a developer-blog post |

**Timing:** open every source before writing a row from it.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| summarising a change from memory | open the post | a row with no source behind it is the failure this procedure exists to prevent | Step 2 |
| writing a row from a release note's one-line mention | open the post behind it | the mention names the change and not the API | Step 2 |
| filtering by "platforms we happen to use" | read all of them | the skill scaffolds any integration, so an OAuth2, event-entity, condition or media-source change is in scope with no such repository in front of you | Step 2 |

## Step 3: Settle every claim against core at the tag

Read `raw.githubusercontent.com/home-assistant/core/<tag>/…` at the tag the release row
names, and say in the row that you did.

| Scenario | Choice |
|---|---|
| what changed, and why | the developer-blog post |
| the API's spelling, and the module it lives in | core at the tag |
| the release it landed in | core at the tag, never a post's publication date |
| the release it is removed in | core at the tag — the `breaks_in_ha_version` of the call site, or the version argument of the `DeprecatedConstantEnum` beside the constant |
| a version neither states | nothing; the row says so rather than guessing one |

**Symptom:** a post is written before the change ships, so stopping at one yields a removal
release the post omits, an enum member list copied from the replaced constants rather than
the enum, a landing release inferred from a publication date, and an API written up as
usable that the release does not carry.

## Step 4: Write the rows, then move the release cell

| Rule | Value |
|---|---|
| a change a custom integration can meet | a row in the `reference/patterns.md` section that owns the topic |
| a change announced for a release that has not landed | a row in *Announced for a release after 2026.9 — Step 1* of `reference/patterns.md`, cleared when it lands |
| every other row in the cached-facts table | re-derived with its own *Re-derive with* command |
| the release cell and its captured date | moved, last |
| the whole pass | one PR |

## The terms the fetched copies are kept under

A cached fact of this repository, not of the skill: nothing in a scaffolded integration reads
it, and the copies it governs live only here.

| Fact | Value | Captured | Re-derive with | Consumers | Gate |
|---|---|---|---|---|---|
| Terms the two source sites publish under | home-assistant.io content is CC BY-NC-SA 4.0; `developers.home-assistant.io` ships no licence file at all | 2026-09-19 | `curl -s https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/LICENSE.md \| head -5`, and check `LICENSE`, `LICENSE.md` and `LICENSE.txt` on both branches of `home-assistant/developers.home-assistant.io` | `LICENCES` in `scripts/fetch_ha_sources.py`, which stamps the notice into every file the fetch writes · the carve-out in this repository's own `LICENSE` | none — a change here is applied by refetching |
