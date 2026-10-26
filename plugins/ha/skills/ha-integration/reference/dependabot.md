# Dependabot for a HA custom integration

Read this when configuring or debugging Dependabot on an integration repo.

**The scaffold's Dependabot moves the `uses:` pins, the pinned test dependencies and the
local hooks' versions except ruff's, and nothing else.**

## Contents

1. Setting Dependabot up
2. Step 1: Write `.github/dependabot.yml`
3. Step 2: Enable `github-actions`
4. Step 3: Enable `pip`
5. Step 4: Enable `pre-commit`
6. Step 5: Leave `manifest.json` `requirements` to a deliberate PR
7. Step 6: Leave each PR to the user once its checks are green
8. Cases
9. A `pip` bump — Step 6
10. Re-copying a plain workflow — Step 2
11. A hook bump that reformats files — Step 6

## Setting Dependabot up

### Step 1: Write `.github/dependabot.yml`

| Rule | Value |
|---|---|
| `commit-message.prefix: "chore"` | on each ecosystem, so titles read `chore: bump …` and the autolabeler files them; the mapping is release-flow's drafter config, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/.github/release-drafter.yml |
| `cooldown: {exclude: ["PineappleEmperor/*"]}` | on the `github-actions` ecosystem alone — what it exempts, what keeps the hold, and why it is spelled that way, is the cooldown bullet of *The version model* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| what turns it on | the file on the default branch; GitHub needs no setting switched on for version updates |
| the scaffold's copy | `templates/.github/dependabot.yml` carries the `commit-message` and `cooldown` rows above, and the ecosystems of Steps 2 to 4 |

### Step 2: Enable `github-actions`

Bumps every `uses:` pin under `.github/workflows/`: the action pins in the four plain
workflows, and the callers' pins, which is how a release of a CI repository reaches you —
*The version model* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md.

### Step 3: Enable `pip`

Points at `requirements.test.txt` / `pyproject`. It has something to bump only where the
test dependencies are pinned, as the template ships them
(`pytest-homeassistant-custom-component==…`); no version specifier means nothing to bump.

### Step 4: Enable `pre-commit`

Points at `.pre-commit-config.yaml`.

| Rule | Value |
|---|---|
| what it bumps | each hook repository's `rev:`, and the pins in a Python or Node hook's `additional_dependencies` — prettier and its plugin among them; `pre_commit/lib/dependabot/pre_commit/file_parser.rb` in dependabot-core, https://github.com/dependabot/dependabot-core |
| `ignore` | `dependency-name: "https://github.com/astral-sh/ruff-pre-commit"`, a hook repository's `repo:` URL as written, so ruff stays at the version CI pins — the `python-validate.yml` bullet under *Implementation notes* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| `groups` | one group over every hook, so a mirror's `rev:` and the tool it installs move in the same PR |

### Step 5: Leave `manifest.json` `requirements` to a deliberate PR

| Rule | Value |
|---|---|
| what Dependabot does with them | nothing: it cannot parse the manifest, and an open `>=` range resolves to the latest matching at install anyway |
| raising a `>=` floor | by hand, in a PR of its own |
| automating it | nothing in the stack does; anything that ever does is a reusable workflow in ha-integration-ci, never a script and a PR opener written into one repo |

### Step 6: Leave each PR to the user once its checks are green

Each is the user's to merge once its checks are green, as *Step 3: Tell the user it is ready
to merge* in `reference/discipline.md` says. Dependabot needs no exemption: nothing compares a
committed version, and the label gate skips bot-authored PRs. Its PRs carry a `chore` label
from their `chore:` title and fold into the next release. A `pip` bump is the one to review before merging — *A `pip` bump — Step 6*. A hook bump that turns `validate / Python validation` red is *A hook bump that reformats files — Step 6*.

## Cases

### A `pip` bump — Step 6

A bump here moves the **HA version the suite tests against** (*Step 4: Keep the harness pin
and the Python floor in lockstep* in `reference/testing.md` says why), and can drag the Python
floor with it.

**Fix:** review these PRs rather than auto-merging, and match ruff's `target-version` and
`mypy.ini`'s `python_version` to the floor the CI declares, which the audit compares —
*What the audit checks now* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md.

**Timing:** a floor move is a CI release first.

### Re-copying a plain workflow — Step 2

The callers carry no stored pin anywhere but your repo, so there is nothing to regress. The
four plain workflows have a template, so re-copying one can move its pin *backwards*.

**Fix:** diff before overwriting, then apply the plain-workflows row of *Step 4: Apply only
the sanctioned adaptations* in `reference/github-actions.md`.

### A hook bump that reformats files — Step 6

A formatter's new version can lay out unchanged code differently, so its bump PR fails
`validate / Python validation` at the step that runs the hooks.

**Symptom:** a Dependabot hook PR fails on files it never touched, which reads as a broken bump
rather than a new format.

**Fix:** on the bump PR's own branch, run `prek run <hook id> --all-files` and push the result as
one `style: apply <tool> <version>` commit; the reformat never goes into a feature branch.

| Rule | Value |
|---|---|
| the red check | `validate / Python validation`, one of the contexts *Step 3: The eight required contexts, and what must never be required* in `reference/github-setup.md` lists; its hooks step is the pre-commit hooks bullet under *Implementation notes* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| prek | installed as the "enabling the local hooks" row of *Step 6: Copy the config and CI files* in `reference/scaffold.md` says |
| a reformat under `frontend/` | a panel source change, so the `style:` commit carries the rebuilt bundle too — *Step 1: Build the bundle and commit it* in `reference/panels.md` |

**Timing:** after any open branch that rewrites the same files has merged, or that branch
rebases over the reformat, so the two never conflict.

> **Note:** once anyone pushes to a Dependabot PR, Dependabot stops resolving its conflicts, so
> the branch is kept up to date by hand; `@dependabot recreate`, or a newer grouped PR, drops the
> `style:` commit, which is then pushed again — the commands list in Dependabot's PR body.
