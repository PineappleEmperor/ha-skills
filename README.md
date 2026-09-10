# ha-skills

An installable [Claude Code](https://claude.com/claude-code) plugin for building **Home
Assistant custom integrations**, and the scaffold that wires them to their CI.

> [!NOTE]
> **AI assistance:** I'm a programmer; these skills and my HA integrations are built with
> AI (Claude, via Claude Code) for implementation, code review, and QA, under human
> direction. Architecture and final review are mine; every change is human-reviewed before
> it merges.

These are the skills behind the AI-assistance note on my HA integrations, such as
[ocado-ha](https://github.com/PineappleEmperor/ocado-ha) and
[ha-pimoroni-unicorn](https://github.com/PineappleEmperor/ha-pimoroni-unicorn).

## Skills

| Skill | What it does |
|-------|--------------|
| [`ha-integration`](plugins/ha/skills/ha-integration/SKILL.md) | Scaffold, modify, audit, and lint a HA custom integration targeting **Platinum** quality scale. Config flows, the `DataUpdateCoordinator` pattern, entity and notify platforms, diagnostics, `quality_scale.yaml` discipline, and panel integrations. Also triages a `home-assistant.log`. |
| [`ha-panel-design`](plugins/ha/skills/ha-panel-design/SKILL.md) | Size, type, spacing, and colour for HA **custom panels** (Lit/TS web components). Material 3 type scale, 48px touch targets, and HA theme CSS custom properties, preferring tokens over hardcoded literals. |

Both ship in one **`ha`** plugin. Both look up the current HA or Material 3 docs before
acting, because these APIs move and memory goes stale.

## Install

Add this repo as a marketplace and install the plugin from inside Claude Code:

```
/plugin marketplace add PineappleEmperor/ha-skills
/plugin install ha@ha-skills
```

Update later with `/plugin marketplace update ha-skills`.

### Without the plugin system

Symlink the `SKILL.md` files into your commands directory to get plain
`/ha-integration` and `/ha-panel-design`:

```bash
git clone git@github.com:PineappleEmperor/ha-skills.git
ln -s "$PWD/ha-skills/plugins/ha/skills/ha-integration/SKILL.md"  ~/.claude/commands/ha-integration.md
ln -s "$PWD/ha-skills/plugins/ha/skills/ha-panel-design/SKILL.md" ~/.claude/commands/ha-panel-design.md
```

That gets you the guidance without the templates. When it needs them the skill asks where
you cloned the repo; it will not write a CI file from memory.

## Using the skills

Claude invokes a skill when the task matches its `description`, or you can call one
directly. Plugin skills are namespaced:

```
/ha:ha-integration
/ha:ha-panel-design
```

To have Claude reach for them without being asked, add this to your global
`~/.claude/CLAUDE.md`:

```markdown
## Home Assistant integrations
When the task touches a HA custom integration (a `custom_components/<domain>/` package,
a `manifest.json` with a `domain`, a config/options flow, or platform code), invoke the
`ha-integration` skill before writing or modifying integration code. Re-invoke after a
`/compact`, since compaction can drop the skill's guidance from context.

## Home Assistant panels
When the task touches a HA custom panel or any display/UI layer, invoke the
`ha-panel-design` skill before changing it. Re-invoke after a `/compact`.
```

## The CI stack

An integration's CI lives in three repositories of reusable workflows, and a scaffolded
integration calls them rather than carrying their bodies, so a CI release reaches every
integration as a Dependabot PR:

| Repository | Owns |
|---|---|
| [release-flow](https://github.com/PineappleEmperor/release-flow) | PR labelling and the label gate, the title lint, the draft-PR opener, release drafting and notes; the commit hook and drafter config a consumer copies. Generic to any repository using Conventional Commits. |
| [ha-integration-ci](https://github.com/PineappleEmperor/ha-integration-ci) | Python validation, the conformance audit, the release zip HACS installs from; the version model every consumer follows. |
| [ha-panel-ci](https://github.com/PineappleEmperor/ha-panel-ci) | The panel type-check and tests, and the `frontend/` templates. |

Each README says what its workflows do and why, and carries the caller blocks a consumer
copies. What the scaffold carries beyond those, from
[`templates/`](plugins/ha/skills/ha-integration/templates), is the skill's
`reference/github-actions.md`.

## Development

The skills are treated as code: this repo is a consumer of release-flow like any
integration, and its own tooling has unit tests that run on every PR.

Changes to the CI repositories are proven on
[ha-ci-testing](https://github.com/PineappleEmperor/ha-ci-testing), a throwaway integration
that runs the whole cycle — branch, draft PR, merge, release candidate, final — because the
parts that break only execute when something publishes.

[`evals/`](plugins/ha/skills/ha-integration/evals) holds five pressure scenarios, each
stating its pass and fail criteria. The intent is to run every one twice, once with the
skill and once with it withheld, because a withheld run that also passes means the guidance
was doing nothing. Coverage is short of that: scenario 01 has both arms, 02 and 03 have only
the with-skill run, and 04 (fork-PR labelling, which needs a second GitHub identity) and 05
(merge discipline) have not been run.

On the scaffolding task, the withheld runs produce a confident, well-tested CI setup that
would not reach the HACS default store. With the skill, they stop and ask for the templates.

`docs/ha-integration-change-rationale.md` records why each convention exists, usually
because something broke.

## License

[Creative Commons Attribution-NonCommercial 4.0 International](LICENSE) (CC BY-NC 4.0):
share and adapt with credit, **non-commercial use only**.
