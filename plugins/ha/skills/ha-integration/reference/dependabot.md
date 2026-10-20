# Dependabot for a HA custom integration

Read this when configuring or debugging Dependabot on an integration repo.

**The scaffold's Dependabot moves the `uses:` pins and the pinned test dependencies, and
nothing else.**

## Contents

1. Setting Dependabot up
2. Step 1: Write `.github/dependabot.yml`
3. Step 2: Enable `github-actions`
4. Step 3: Enable `pip`
5. Step 4: Leave `manifest.json` `requirements` to a deliberate PR
6. Step 5: Merge the PRs as they arrive
7. Cases
8. A `pip` bump — Step 5
9. Re-copying a plain workflow — Step 2

## Setting Dependabot up

### Step 1: Write `.github/dependabot.yml`

| Rule | Value |
|---|---|
| `commit-message.prefix: "chore"` | on each ecosystem, so titles read `chore: bump …` and the autolabeler files them; the mapping is release-flow's drafter config |
| `cooldown: {exclude: ["PineappleEmperor/*"]}` | on the `github-actions` ecosystem alone — what it exempts, what keeps the hold, and why it is spelled that way, is the cooldown bullet of *The version model* in ha-integration-ci's README |
| what turns it on | the file on the default branch; GitHub needs no setting switched on for version updates |
| the scaffold's copy | `templates/.github/dependabot.yml` carries both rows above |

### Step 2: Enable `github-actions`

Bumps every `uses:` pin under `.github/workflows/`: the action pins in the four plain
workflows, and the callers' pins, which is how a release of a CI repository reaches you —
*The version model* in ha-integration-ci's README.

### Step 3: Enable `pip`

Points at `requirements.test.txt` / `pyproject`. It has something to bump only where the
test dependencies are pinned, as the template ships them
(`pytest-homeassistant-custom-component==…`); no version specifier means nothing to bump.

### Step 4: Leave `manifest.json` `requirements` to a deliberate PR

| Rule | Value |
|---|---|
| what Dependabot does with them | nothing: it cannot parse the manifest, and an open `>=` range resolves to the latest matching at install anyway |
| raising a `>=` floor | by hand, in a PR of its own |
| automating it | nothing in the stack does; anything that ever does is a reusable workflow in ha-integration-ci, never a script and a PR opener written into one repo |

### Step 5: Merge the PRs as they arrive

Dependabot needs no exemption: nothing compares a committed version, and the label gate
skips bot-authored PRs. Its PRs carry a `chore` label from their `chore:` title, fold into
the next release, and need no special case anywhere.

## Cases

### A `pip` bump — Step 5

A bump here moves the **HA version the suite tests against** (`reference/testing.md` says
why), and can drag the Python floor with it.

**Fix:** review these PRs rather than auto-merging, and match ruff's `target-version` and
`mypy.ini`'s `python_version` to the floor the CI declares, which the audit compares —
*What the audit checks now* in ha-integration-ci's README.

**Timing:** a floor move is a CI release first.

### Re-copying a plain workflow — Step 2

The callers carry no stored pin anywhere but your repo, so there is nothing to regress. The
four plain workflows have a template, so re-copying one can move its pin *backwards*.

**Fix:** diff before overwriting, then apply the plain-workflows row of *Step 4: Apply only
the sanctioned adaptations* in `reference/github-actions.md`.
