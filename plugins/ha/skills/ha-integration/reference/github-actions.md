# GitHub CI stack — what a scaffold carries

Read this when writing or reviewing an integration's CI files: where each comes from, and what a copy may change.

**Each CI file is copied from the source Step 2 names for it, and never written from memory.**

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

An integration calls reusable workflows from three repositories. What each workflow does,
and why, is the README of the repository that owns it:

| file | when to read |
|---|---|
| release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md | PR labelling, the label gate, the title lint, the draft-PR opener, release drafting and notes, and the drafter config and commit hook a consumer copies |
| ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md | Python validation, the conformance audit, the release zip, the version model every consumer follows, and what the audit checks |
| ha-panel-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-panel-ci/main/README.md | the panel check and the `frontend/` templates |

### Step 1: Locate `templates/`

`templates/` sits in this skill's own directory, beside its `SKILL.md`. Resolve it in this
order:

1. **The base directory announced when the skill loaded.** Invoking a skill prints
   `Base directory for this skill: <path>` — `templates/` is `<path>/templates/`. Always
   correct; try it first.
2. **Installed as a plugin:** `~/.claude/plugins/cache/*/ha/*/skills/ha-integration/templates/`
3. **Personal or repo skill:** `~/.claude/skills/ha-integration/templates/`, or
   `plugins/ha/skills/ha-integration/templates/` inside a checkout of the skill repo.
4. **Last resort:** `find ~/.claude ~/.agents . -type d -path '*ha-integration/templates' 2>/dev/null`

| Rule | Value |
|---|---|
| the files it holds for Step 2 | the four plain workflows, `.github/dependabot.yml`, `tests/`, `pyproject.toml`, `mypy.ini`, `requirements.test.txt`, `ruleset.json`, `.gitignore`, the four local-hook files and `scripts/bootstrap_repo.sh` |
| `hooks/` | optional reminders for your own `~/.claude`, carried by no integration; each is installed as its script's header says |

### Step 2: Take each file from its source

How to verify a copy is *Step 1: Callers, not bodies; copies, not paraphrases* in
`reference/audit.md`.

| Artefact | Taken from |
|---|---|
| `.github/workflows/pr-checks.yml`, `lint-pr.yml`, `auto-draft-pr.yml`, `release-drafter.yml` | the usage blocks under *Calling the workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| `.github/workflows/python-validate.yml`, `quality-audit.yml`, `release.yml` | the usage blocks under *Calling the workflows* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| `.github/workflows/panel-bundle.yml` (panel repos only) | the usage block under *Calling the workflow* in ha-panel-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-panel-ci/main/README.md |
| `.github/release-drafter.yml`, `.githooks/commit-msg` | release-flow's own files, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/.github/release-drafter.yml and https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/.githooks/commit-msg, per *Called versus copied* in its README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| `.github/workflows/dependency-review.yml`, `hacs-validate.yml`, `hassfest-validate.yml`, `issue_stale.yml` | this skill's `templates/.github/workflows/`; each is settings over a third-party action |
| `.github/dependabot.yml` | this skill's `templates/`; what it must contain is `reference/dependabot.md` |
| `ruleset.json`, `pyproject.toml`, `mypy.ini`, `tests/conftest.py`, `tests/__init__.py`, `tests/ruff.toml`, `requirements.test.txt`, `.gitignore`, `.pre-commit-config.yaml`, `.yamllint`, `.prettierrc.js`, `.prettierignore`, and the `CLAUDE.md` and `.githooks/pre-commit` snippets | this skill's `templates/` and `reference/scaffold.md` |
| `frontend/package.json`, `frontend/tsconfig.json` (panel repos only) | ha-panel-ci's `frontend/`, https://raw.githubusercontent.com/PineappleEmperor/ha-panel-ci/main/frontend/package.json and https://raw.githubusercontent.com/PineappleEmperor/ha-panel-ci/main/frontend/tsconfig.json |
| `scripts/bootstrap_repo.sh` | this skill's `templates/scripts/`; when to run it is *Step 10: Apply the GitHub settings* in `reference/scaffold.md` |

| Rule | Value |
|---|---|
| what the audit checks in a caller | that its `uses:` names the right repository and workflow, and that it carries no body — `check_callers` under *What the audit checks now* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| what the audit checks in a pin | a 40-hex SHA with a version comment — `check_action_pins` under *What the audit checks now* in ha-integration-ci's README |
| what the audit never checks | that a copied file matches its source, so a caller written from memory can pass — the core rule of `reference/audit.md` |

The four workflows the scaffold copies whole are settings over a third-party action, so they
carry nothing of ours to version:

| Rule | Value |
|---|---|
| `dependency-review.yml` | fails a PR adding a dependency with a high-severity advisory, and gates no lower severity, since Dependabot raises those on its own schedule; needs the dependency graph on, per *`Dependency review` is red on every PR — checks Step 3* in `reference/github-setup.md` |
| `hacs-validate.yml` | runs HACS's checks with no `ignore:` input — which of them run, and what each demands, is *`HACS validation` is red — Step 9* in `reference/scaffold.md`; stays on `hacs/action@main`, the ref HACS documents, never a SHA, with `contents: read` and `persist-credentials: false` kept |
| `hassfest-validate.yml` | runs core's hassfest plugins over the integration; what it does with a custom integration's quality scale is *Step 4: Claim the tier in the manifest only once it is fully met* in `reference/quality-scale.md`; stays on `hassfest@master`, the ref Home Assistant documents, never a SHA, with `contents: read` and `persist-credentials: false` kept |
| `issue_stale.yml` | labels issues and PRs untouched for 60 days, and closes none |

### Step 3: Resolve each caller's pin

| Rule | Value |
|---|---|
| what every caller block ends in | `@{{sha}} # {{tag}}` |
| how to resolve both | the two commands printed after the caller blocks in the README Step 2 names for that caller, run before writing the file |
| how the pin moves after that | *The version model* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |

### Step 4: Apply only the sanctioned adaptations

Any other difference from the README block or the template is drift, and this table is the
only list of them.

| Rule | Value |
|---|---|
| `pyproject.toml` | a `[project]` table carrying no version, and pytest options; never the `[tool.ruff]` tables, which are Home Assistant core's rule set |
| `frontend/package.json` | the `<domain>` and `<name>` placeholders → this integration's values — *The frontend templates* in ha-panel-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-panel-ci/main/README.md |
| `requirements.test.txt` | uncomment the `home-assistant-frontend` pin and give it its version, panel repos only — *Step 2: Pin `home-assistant-frontend` in `requirements.test.txt`* in `reference/panels.md` |
| `tests/conftest.py` | the repo's own imports and fixtures added to the template's |
| `ruleset.json` | drop a context the repo does not produce |
| `.pre-commit-config.yaml` | a hook `rev` newer than the template's, and words added to codespell's `--ignore-words-list` |
| `.prettierignore` | a path added for another file the repo copies or builds |
| the four plain workflows | an action pin **newer** than the template's, where Dependabot has already bumped yours; keep the newer pin |

### Step 5: Delete any superseded workflow

- `frontend_build.yml` → ha-panel-ci's `panel-bundle.yml`
- `create-dev-pr.yml` → release-flow's `auto-draft-pr.yml`
- `python_validate.yml`, `release_drafter.yml` and every other underscore-named copy of a
  reusable workflow → the hyphenated caller
- `pr-labeler.yml`, `pr-title-check.yml`, `pr-commit-summary.yml`,
  `check-manifest-version.yml` → no successor of their own name; delete

What the audit does with a body left under `.github/workflows/` is *What the audit checks
now* in ha-integration-ci's README,
https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md.

## Cases

### `templates/` cannot be located — Step 1

**Fix:** report which paths you checked and ask for the skill's location; write none of
those files from memory.

### A README block cannot be read — Step 2

**Fix:** with no network and no `gh`, stop and say so, exactly as *`templates/` cannot be
located — Step 1* requires for the templates.

### A repo needs a second PR opener — Step 2

**Fix:** declare it with a `# skill-audit: sanctioned-opener` line and its reason beside it.

| Rule | Value |
|---|---|
| what the marker allows | `gh pr create` in that workflow — *What the audit checks now* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| who reads the reason | a person; the audit reads only the marker |
