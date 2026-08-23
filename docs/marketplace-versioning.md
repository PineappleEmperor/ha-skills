# Versioning this marketplace repo

Repo-local, deliberately outside `plugins/`: it describes how **this** repository ships,
not anything a scaffolded integration does. An integration's version rides the release
zip and never touches its repo; none of the below applies there.

## Declare the version in `plugin.json`, nowhere else

From the [plugin marketplace reference](https://code.claude.com/docs/en/plugin-marketplaces):

> Avoid setting `version` in both `plugin.json` and the marketplace entry. Claude Code
> always uses the `plugin.json` value without warning, so a stale manifest version can
> mask a version you set in `marketplace.json`.

This repo carried it in both for months, and `pr-checks.yml` had a required step
enforcing that the two agreed — comparing a value Claude Code reads against one it
discards. Both are gone: `marketplace.json` declares no version.

## The declared version is the update signal

Users receive a new copy only when that string changes. A hundred commits under an
unchanged version leave every existing user on the cached copy. Omitting it instead makes
a git source fall back to the resolved commit SHA, so users track the branch — the docs
call that the simplest setup for an actively developed plugin.

**This repo declares it**, because releases are the unit we ship and users should land on
a released state, not on whatever `main` holds mid-cycle.

## Nothing is bumped by hand

`sync_plugin_version.yml` writes the published tag into `plugin.json` and opens a PR that
auto-merge lands. The tag is the input, so a hand-pushed tag overrides. Pushing to `main`
directly would need either a permanent ruleset bypass for `RELEASE_TOKEN` or the
protection disabled at every release; a PR keeps every rule enforced and still needs
nothing typed.

Known limit: two releases published close together produce two sync PRs, and the second
conflicts. It stops visibly rather than silently.
