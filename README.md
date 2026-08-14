# pineapple-claude-hacs

Custom [Claude Code](https://claude.com/claude-code) skills for building and maintaining
**Home Assistant custom integrations**, from scaffold to Platinum quality scale, plus
native-looking custom panels.

> [!NOTE]
> **AI assistance:** I'm a programmer; these skills and my HA integrations are built with
> AI (Claude, via Claude Code) for implementation, code review, and QA, under human
> direction. Architecture and final review are mine; every change is human-reviewed before
> it merges.

These are the skills behind the AI-assistance note on my HA integrations (for example
[ocado-ha](https://github.com/PineappleEmperor/ocado-ha) and
[ha-pimoroni-unicorn](https://github.com/PineappleEmperor/ha-pimoroni-unicorn)). They encode
conventions learned the hard way, so a new session starts with them instead of rediscovering
them.

## Skills

| Skill | What it does |
|-------|--------------|
| [`ha-integration`](plugins/ha/skills/ha-integration/SKILL.md) | Scaffold, modify, audit, and lint a HA custom integration targeting **Platinum** quality scale. Config flows, the `DataUpdateCoordinator` pattern, modern entity and notify platforms, diagnostics, `quality_scale.yaml` discipline, panel integrations, and the CI stack below. Also triages a `home-assistant.log`. |
| [`ha-panel-design`](plugins/ha/skills/ha-panel-design/SKILL.md) | Size, type, spacing, and colour for HA **custom panels** (Lit/TS web components). Material 3 type scale, 48px touch targets, and HA theme CSS custom properties, preferring tokens over hardcoded literals. |

Both ship in a single **`ha`** plugin in this marketplace, and both fetch the authoritative
HA or Material 3 docs before acting rather than coding from memory, since these APIs change.

## What it ships

`ha-integration` is mostly a set of files to copy, not prose to follow. Its
[`templates/`](plugins/ha/skills/ha-integration/templates) directory carries the CI stack
verbatim: ten workflows, the release-drafter and Dependabot configs, a `commit-msg` hook,
a branch ruleset, pytest wiring, and the frontend build for panel integrations.

They are copied byte-for-byte, with one sanctioned substitution. That rule exists because a
paraphrase looks right and drifts silently: fifteen hand-written CI files once passed a
hand-written audit while diverging from every convention they claimed to follow.

Two scripts do the enforcing, and both are unit-tested:

- [`skill_audit.sh`](plugins/ha/skills/ha-integration/templates/scripts/skill_audit.sh) runs on
  every PR. It fails on a missing workflow, a stale action pin, a deprecated pattern in
  `custom_components/`, a `quality_scale.yaml` claiming rules it has no tests for, a tracked
  `.pyc`, or a default branch with no required status checks.
- [`manifest_gate.py`](plugins/ha/skills/ha-integration/templates/scripts/manifest_gate.py)
  decides whether a version bump matches the PR's type label, measured against the last
  published release.

## The CI stack it scaffolds

Humans open PRs. `pr-checks.yml` holds every job that reads or writes labels in one workflow
so `needs:` can order them: label from the title, check the title is labellable, gate the
version, and accumulate the commit subjects into the PR body. Release notes are drafted from
those labels, and `release.yml` attaches the zip HACS installs.

None of it binds until the checks are **required**, which is what
[`ruleset.json`](plugins/ha/skills/ha-integration/templates/ruleset.json) is for. The audit
fails a repo that skipped it.

## It is tested against itself

[`evals/`](plugins/ha/skills/ha-integration/evals) holds pressure scenarios with recorded
results, on the principle that guidance nobody has watched an agent fail without is
unverified. Given the same task with the skill withheld, agents write a confident, plausible
CI stack that would not reach the HACS default store. Given the skill, they stop and ask for
the templates.

## Install

### Plugin marketplace (recommended)

Add this repo as a marketplace and install the `ha` plugin from inside Claude Code:

```
/plugin marketplace add PineappleEmperor/pineapple-claude-hacs
/plugin install ha@pineapple-claude-hacs
```

Both skills come with it. Claude auto-invokes them when relevant (the trigger is in each
skill's `description`), or call them explicitly, since plugin skills are namespaced:

```
/ha:ha-integration
/ha:ha-panel-design
```

Update later with `/plugin marketplace update pineapple-claude-hacs`.

### Manual (symlink)

Prefer the files loose as plain `/ha-integration` and `/ha-panel-design` commands? Symlink
the `SKILL.md` files into your commands directory:

```bash
git clone git@github.com:PineappleEmperor/pineapple-claude-hacs.git
ln -s "$PWD/pineapple-claude-hacs/plugins/ha/skills/ha-integration/SKILL.md"  ~/.claude/commands/ha-integration.md
ln -s "$PWD/pineapple-claude-hacs/plugins/ha/skills/ha-panel-design/SKILL.md" ~/.claude/commands/ha-panel-design.md
```

This gets you `SKILL.md` only. The templates and scripts live in the repo you just cloned,
and the skill will ask you for their path rather than writing them from memory.

To have Claude invoke the skills automatically, add a rule to your global
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

## License

[Creative Commons Attribution-NonCommercial 4.0 International](LICENSE) (CC BY-NC 4.0):
share and adapt with credit, **non-commercial use only**.
