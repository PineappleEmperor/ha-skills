# pineapple-claude-hacs

An installable [Claude Code](https://claude.com/claude-code) plugin for building **Home
Assistant custom integrations**, with the CI templates those repos need.

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
/plugin marketplace add PineappleEmperor/pineapple-claude-hacs
/plugin install ha@pineapple-claude-hacs
```

Update later with `/plugin marketplace update pineapple-claude-hacs`.

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

### Without the plugin system

Symlink the `SKILL.md` files into your commands directory to get plain
`/ha-integration` and `/ha-panel-design`:

```bash
git clone git@github.com:PineappleEmperor/pineapple-claude-hacs.git
ln -s "$PWD/pineapple-claude-hacs/plugins/ha/skills/ha-integration/SKILL.md"  ~/.claude/commands/ha-integration.md
ln -s "$PWD/pineapple-claude-hacs/plugins/ha/skills/ha-panel-design/SKILL.md" ~/.claude/commands/ha-panel-design.md
```

That gets you the guidance without the templates. When it needs them the skill asks where
you cloned the repo; it will not write the CI from memory.

## The CI templates

Scaffolding an integration copies a working CI setup into it, from
[`templates/`](plugins/ha/skills/ha-integration/templates):

| | |
|---|---|
| **PR checks** | One workflow whose jobs are ordered with `needs:`. Labels the PR from its title, checks the title is labellable, gates the version against the last published release, and collects the commit subjects into the PR body. |
| **Validation** | hassfest, the eight HACS checks, ruff and pyright, and pytest with the Home Assistant test plugin already wired up. |
| **Release** | Notes drafted from the PR labels, and the zip asset HACS installs from. |
| **Conformance** | `skill_audit.sh` runs on every PR and fails on a missing workflow, a stale action pin, a deprecated pattern, a `quality_scale.yaml` claiming rules it has no tests for, or a branch with no required status checks. |
| **Repo setup** | A `commit-msg` hook, a `.gitignore`, and a branch ruleset, without which every check above is advisory and a red PR still merges. |
| **Panels** | An esbuild pipeline that fails the build when the committed bundle is stale, plus the frontend test runner. |

The templates are copied byte-for-byte, with one permitted substitution. Write them from the
skill's prose instead and you get something that looks right and drifts silently, so the
audit looks for the files themselves.

## Development

The skills are treated as code. `skill_audit.sh` and `manifest_gate.py` have unit tests, and
this repo runs the same CI it scaffolds.

[`evals/`](plugins/ha/skills/ha-integration/evals) holds pressure scenarios with their
recorded results. Each states its pass and fail criteria and gets run twice, once with the
skill and once with it withheld. If the withheld run passes too, the guidance was not doing
anything and should go.

On the scaffolding task, the withheld runs produce a confident, well-tested CI setup that
would not reach the HACS default store. With the skill, they stop and ask for the templates.

`docs/ha-integration-change-rationale.md` records why each convention exists, usually
because something broke.

## License

[Creative Commons Attribution-NonCommercial 4.0 International](LICENSE) (CC BY-NC 4.0):
share and adapt with credit, **non-commercial use only**.
