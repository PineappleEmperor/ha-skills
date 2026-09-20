# GitHub CI stack — what a scaffold carries

Read this when writing or reviewing an integration's workflow files: what the scaffold
carries, where each piece comes from, and what may differ from its source. GitHub-side
settings (token, ruleset, required checks) are `reference/github-setup.md`.

**A scaffold carries one caller workflow per reusable workflow plus a few copied configs —
no workflow body and no script, the invariant in `SKILL.md`.**

## Contents

1. Assembling the scaffold's CI files
2. Step 1: Locate `templates/`
3. Step 2: Take each file from its source
4. Step 3: Resolve each caller's pin
5. Step 4: Apply only the sanctioned adaptations
6. Step 5: Delete any superseded workflow
7. Cases
8. `templates/` cannot be located — Step 1
9. A README block cannot be read — Step 2
10. A repo needs a second PR opener — Step 2

## Assembling the scaffold's CI files

An integration's CI is three repositories of reusable workflows. What each workflow does,
and why, is the README of the repository that owns it:

- [release-flow](https://github.com/PineappleEmperor/release-flow) owns PR labelling, the
  label gate, the title lint, the draft-PR opener, release drafting and notes; the drafter
  config and commit hook a consumer copies.
- [ha-integration-ci](https://github.com/PineappleEmperor/ha-integration-ci) owns Python
  validation, the conformance audit, the release zip; the version model every consumer
  follows, and what the audit checks.
- [ha-panel-ci](https://github.com/PineappleEmperor/ha-panel-ci) owns the panel check and
  the `frontend/` templates.

### Step 1: Locate `templates/`

`templates/` sits next to the `SKILL.md` you are reading, in this skill's own directory.
Resolve it in this order:

- **The base directory announced when the skill loaded.** Invoking a skill prints
  `Base directory for this skill: <path>` — `templates/` is `<path>/templates/`. Always
  correct; try it first.
- **Installed as a plugin:** `~/.claude/plugins/cache/*/ha/*/skills/ha-integration/templates/`
- **Personal or repo skill:** `~/.claude/skills/ha-integration/templates/`, or
  `plugins/ha/skills/ha-integration/templates/` inside a checkout of the skill repo.
- **Last resort:** `find ~/.claude ~/.agents . -type d -path '*ha-integration/templates' 2>/dev/null`

It holds the copied files Step 2 names: the four plain workflows, `.github/dependabot.yml`,
`conftest.py`, `pyproject.toml`, `requirements.test.txt`, `ruleset.json`, `.gitignore`,
`scripts/bootstrap_repo.sh` and `hooks/` (optional per-turn reminders for your own
`~/.claude`, installed per the header in each script).

### Step 2: Take each file from its source

A README block is to a caller what `templates/` is to a copy: the source. Write each file as
the README or template gives it, and write none of them from memory; how to verify a copy is
the first item of `reference/audit.md`.

- `.github/workflows/pr-checks.yml`, `lint-pr.yml`, `auto-draft-pr.yml`,
  `release-drafter.yml` — the usage blocks under *Calling the workflows* in release-flow's
  README
- `.github/workflows/python-validate.yml`, `quality-audit.yml`, `release.yml` — the usage
  blocks under *Calling the workflows* in ha-integration-ci's README
- `.github/workflows/panel-bundle.yml` (panel repos only) — the usage block under *Calling
  the workflow* in ha-panel-ci's README
- `.github/release-drafter.yml`, `.githooks/commit-msg` — release-flow's own files, per
  *Called versus copied* in its README
- `.github/workflows/dependency-review.yml`, `hacs-validate.yml`, `hassfest-validate.yml`,
  `issue_stale.yml` — this skill's `templates/.github/workflows/`; each is settings over a
  third-party action
- `.github/dependabot.yml` — this skill's `templates/`; what it must contain is
  `reference/dependabot.md`
- `ruleset.json`, `pyproject.toml`, `conftest.py`, `requirements.test.txt`, `.gitignore`,
  `CLAUDE.md` snippet — this skill's `templates/` and `reference/scaffold.md`
- `frontend/package.json`, `frontend/tsconfig.json` (panel repos only) — ha-panel-ci's
  `frontend/`
- `scripts/bootstrap_repo.sh` — this skill's `templates/scripts/`; when to run it is
  `reference/github-setup.md`

The audit does not compare a caller with its README block — what it does check is *What the
audit checks now* in ha-integration-ci's README — so a caller written from memory can pass
it.

The four workflows the scaffold copies whole are settings over a third-party action and
carry nothing of ours to version. Each has its own contract:

- **`dependency-review.yml`** fails a PR that adds a dependency carrying a high-severity
  advisory; lower severities are deliberately not gated, since Dependabot raises those on
  its own schedule. It needs the dependency graph on, per `reference/github-setup.md`.
- **`hacs-validate.yml`** runs HACS's nine checks with no `ignore:` input, since ignoring any
  check disqualifies the repo from the default store.
- **`hassfest-validate.yml`** runs core's hassfest plugins over the integration — manifest,
  services, translations and the rest. What it does and does not do with the quality
  scale for a custom integration is `reference/quality-scale.md`.
- **`issue_stale.yml`** labels issues and PRs untouched for 60 days and never closes them.

### Step 3: Resolve each caller's pin

Every caller block ends in `@{{sha}} # {{tag}}`. Resolve both with the two commands printed
under the block before writing the file; from then on the pin moves as *The version model*
in ha-integration-ci's README says.

### Step 4: Apply only the sanctioned adaptations

Any other difference from the README block or the template is drift. **This list is the only
list.** `reference/audit.md` points here; if they ever appear to disagree, this list wins.

- `pyproject.toml` — a `[project]` table carrying no version, and pytest or pyright options;
  never the `[tool.ruff]` tables, which are Home Assistant core's rule set
- `frontend/package.json` — the `<domain>` and `<name>` placeholders → this integration's
  values, as ha-panel-ci's README says
- `requirements.test.txt` — uncomment the `home-assistant-frontend` pin, panel repos only
- `ruleset.json` — drop a context the repo does not produce
- the four plain workflows — an action pin **newer** than the template's, where Dependabot
  has already bumped yours; keep the newer pin

### Step 5: Delete any superseded workflow

- `frontend_build.yml` → ha-panel-ci's `panel-bundle.yml`
- `create-dev-pr.yml` → release-flow's `auto-draft-pr.yml`
- `python_validate.yml`, `release_drafter.yml` and every other underscore-named copy of a
  reusable workflow → the hyphenated caller
- `pr-labeler.yml`, `pr-title-check.yml`, `pr-commit-summary.yml`,
  `check-manifest-version.yml` → no successor of their own name; delete

Leaving one in place leaves a body in a repository that should carry none, and the audit
reads every file under `.github/workflows/`: what it does with a body is *What the audit
checks now* in ha-integration-ci's README.

## Cases

### `templates/` cannot be located — Step 1

**Fix:** report which paths you checked and ask for the skill's location; write none of
those files from memory.

### A README block cannot be read — Step 2

**Fix:** with no network and no `gh`, stop and say so, exactly as *`templates/` cannot be
located — Step 1* requires for the templates.

### A repo needs a second PR opener — Step 2

**Fix:** declare it, with the marker line *What the audit checks now* in ha-integration-ci's
README names.
