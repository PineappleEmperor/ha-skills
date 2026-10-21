# 07 — Task retrieval

Known-answer test for what a reader gets once routed: do the files the router names hold
the answer, or does the answer sit a second hop away, in a place the reader cannot reach?

## Setup

No fixture. The agent may read only files under `plugins/ha/skills/`, and web pages at URLs
those files give. It may not read the CI repositories' local clones, since a user's
integration repository has none.

## Prompt

> You are helping the maintainer of a Home Assistant custom integration. Load the
> `ha-integration` skill from `plugins/ha/skills/ha-integration/SKILL.md` and answer each
> request below from the skill. You may read only files under `plugins/ha/skills/`, and web
> pages at URLs those files give (fetch the Markdown with curl). Do not read any other local
> file. Do not answer from your own knowledge without saying so.
>
> A. "My release draft says v1.3.0, but I merged a PR that removes an option users rely on,
> so it should be v2.0.0. What decides the number, and how do I fix it?"
> B. "I'm adding a sidebar panel to my integration. Which Home Assistant developer docs page
> explains how a custom panel is registered? Give its URL."
> C. "Dependabot opened a PR bumping `pytest-homeassistant-custom-component`. Can I let it
> auto-merge, and what should I check first?"
> D. "Is this skill still current for the latest Home Assistant release, and how would I
> check?"
>
> For each request report: the answer; every file you opened, in order, and whether you
> read it whole or in part; the sentence in the skill each part of the answer came from;
> and any pointer you could not follow.

## Pass

| Request | The answer holds | Reached by |
|---|---|---|
| A | the merged PRs' labels decide the version and the highest wins; `!` on the type in the PR title is the only breaking marker, never a `BREAKING CHANGE:` footer; the fix is the title or the commits, never a hand-set label or a hand-written version | a file the router's Release row names, or a URL the row or that file gives |
| B | `https://contributors.home-assistant.io/frontend/custom-ui/panel/` | the router's Panel row, or the file it names |
| C | no auto-merge; the bump moves the Home Assistant version the tests run against, and can move the Python floor; match ruff's `target-version` and mypy's `python_version` to the floor the CI declares | a file the router's Dependabot row names, or a URL the row or that file gives |
| D | `reference/freshness.md`'s release row and the command that re-derives it | the router row a reader asking "is this current" picks |

Each part of an answer must cite a sentence from the skill. A part answered from the
agent's own knowledge, or from a page the skill does not give, does not count.

## Fail

A part of an answer missing or wrong; a part reached only through a reference file the row
does not name; a pointer the agent could not follow.
