# GitHub CI stack — what a scaffold carries

An integration's CI is three repositories of reusable workflows. The scaffold carries one
caller workflow per reusable workflow plus a few copied configs; it carries no workflow body
and no script. What each workflow does, and why, is the README of the repository that owns
it. GitHub-side settings (token, ruleset, required checks) are `reference/github-setup.md`.

- What a scaffold carries
- Where `templates/` lives
- Sanctioned adaptations — the complete list
- The plain workflows
- Superseded — do not reinstate

| Repository | Owns |
|---|---|
| [release-flow](https://github.com/PineappleEmperor/release-flow) | PR labelling, the label gate, the title lint, the draft-PR opener, release drafting and notes; the drafter config and commit hook a consumer copies |
| [ha-integration-ci](https://github.com/PineappleEmperor/ha-integration-ci) | Python validation, the conformance audit, the release zip; the version model every consumer follows, and what the audit checks |
| [ha-panel-ci](https://github.com/PineappleEmperor/ha-panel-ci) | the panel check and the `frontend/` templates |

## What a scaffold carries

| In the scaffold | Copied from |
|---|---|
| `.github/workflows/pr-checks.yml`, `lint-pr.yml`, `auto-draft-pr.yml`, `release-drafter.yml` | the usage blocks under *Calling the workflows* in release-flow's README |
| `.github/workflows/python-validate.yml`, `quality-audit.yml`, `release.yml` | the usage blocks under *Calling the workflows* in ha-integration-ci's README |
| `.github/workflows/panel-bundle.yml` (panel repos only) | the usage block under *Calling the workflow* in ha-panel-ci's README |
| `.github/release-drafter.yml`, `.githooks/commit-msg` | release-flow's own files, per *Called versus copied* in its README |
| `.github/workflows/dependency-review.yml`, `hacs-validate.yml`, `hassfest-validate.yml`, `issue_stale.yml` | this skill's `templates/.github/workflows/`; each is settings over a third-party action |
| `.github/dependabot.yml` | this skill's `templates/`; what it must contain is `reference/dependabot.md` |
| `ruleset.json`, `pyproject.toml`, `conftest.py`, `requirements.test.txt`, `.gitignore`, `CLAUDE.md` snippet | this skill's `templates/` and `reference/scaffold.md` |
| `frontend/package.json`, `frontend/tsconfig.json` (panel repos only) | ha-panel-ci's `frontend/` |
| `scripts/bootstrap_repo.sh` | this skill's `templates/scripts/`; when to run it is `reference/github-setup.md` |

Every caller block ends in `@{{sha}} # {{tag}}`. Resolve both with the two commands printed
under the block before writing the file; a `{{` left in a workflow fails the audit. From then
on Dependabot moves the pin, as the version model in ha-integration-ci's README says.

Write each file as the README or template gives it, then apply only the adaptations below.
Verify with `cmp` per file rather than `diff -r` per directory — a tree still being
assembled reads as identical when individual files differ.

## Where `templates/` lives

`templates/` sits next to the `SKILL.md` you are reading, in this skill's own directory.
Resolve it in this order:

1. **The base directory announced when the skill loaded.** Invoking a skill prints
   `Base directory for this skill: <path>` — `templates/` is `<path>/templates/`. Always
   correct; try it first.
2. **Installed as a plugin:** `~/.claude/plugins/cache/*/ha/*/skills/ha-integration/templates/`
3. **Personal or repo skill:** `~/.claude/skills/ha-integration/templates/`, or
   `plugins/ha/skills/ha-integration/templates/` inside a checkout of the skill repo.
4. **Last resort:** `find ~/.claude ~/.agents . -type d -path '*ha-integration/templates' 2>/dev/null`

It holds the copied files of the table above: the four plain workflows,
`.github/dependabot.yml`, `conftest.py`, `pyproject.toml`, `requirements.test.txt`,
`ruleset.json`, `.gitignore`, `scripts/bootstrap_repo.sh` and `hooks/` (optional per-turn
reminders for your own `~/.claude`, installed per the header in each script).

If none of those find it, report which paths you checked and ask for the skill's location.
Do not write any of those files from memory.

## Sanctioned adaptations — the complete list

Any other difference from the README block or the template is drift.

| File | Allowed change |
|---|---|
| `pyproject.toml` | a `[project]` table carrying no version, and pytest or pyright options — never the `[tool.ruff]` tables, which are Home Assistant core's rule set |
| `frontend/package.json` | `<domain>` and `<name>` placeholders → this integration's values, as ha-panel-ci's README says |
| `requirements.test.txt` | uncomment the `home-assistant-frontend` pin, panel repos only |
| `ruleset.json` | drop a context the repo does not produce |
| the four plain workflows | an action pin **newer** than the template's, where Dependabot has already bumped yours — keep the newer pin |

**This table is the only list.** `reference/audit.md` points here; if they ever appear to
disagree, this table wins.

## The plain workflows

The four workflows the scaffold copies whole are settings over a third-party action and
carry nothing of ours to version:

- **`dependency-review.yml`** fails a PR that adds a dependency carrying a high-severity
  advisory; lower severities are deliberately not gated. It needs the dependency graph on,
  per `reference/github-setup.md`.
- **`hacs-validate.yml`** runs HACS's nine checks with no `ignore:` input, since ignoring any
  check disqualifies the repo from the default store.
- **`hassfest-validate.yml`** validates the manifest, services and quality scale.
- **`issue_stale.yml`** labels issues and PRs untouched for 60 days and never closes them.

**A repo that needs a second PR opener declares it.** The audit fails any workflow containing
`gh pr create` other than the release-flow opener; the one way through is a comment line
`# skill-audit: sanctioned-opener` in that workflow, carrying the reason. A `scripts/*.py`
or `.sh` that no workflow runs is a local tool and says so with `# skill-audit: local-tool`.

## Superseded — do not reinstate

`frontend_build.yml` is replaced by ha-panel-ci's `panel-bundle.yml` and `create-dev-pr.yml`
by release-flow's `auto-draft-pr.yml`; the underscore-named copies of every reusable
workflow (`python_validate.yml`, `release_drafter.yml` and the rest) are bodies a caller
replaces. What the audit does with each is *What the audit checks now* in
ha-integration-ci's README. `pr-labeler.yml`, `pr-title-check.yml`,
`pr-commit-summary.yml` and `check-manifest-version.yml` are older still and have no
successor of their own name.
