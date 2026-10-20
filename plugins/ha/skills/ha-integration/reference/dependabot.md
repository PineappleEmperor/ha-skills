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
6. Step 5: Merge each PR once its checks are green
7. Cases
8. A `pip` bump — Step 5
9. Re-copying a plain workflow — Step 2

## Setting Dependabot up

### Step 1: Write `.github/dependabot.yml`

| Rule | Value |
|---|---|
| `commit-message.prefix: "chore"` | on each ecosystem, so titles read `chore: bump …` and the autolabeler labels them `chore`, a patch — release-flow's `.github/release-drafter.yml`, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/.github/release-drafter.yml |
| `cooldown: {exclude: ["PineappleEmperor/*"]}` | on the `github-actions` ecosystem alone, so a release of this stack's CI arrives without the three-day hold every other action and package keeps — the cooldown bullet of *The version model* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| what turns it on | the file on the default branch; GitHub needs no setting switched on for version updates |
| the scaffold's copy | `templates/.github/dependabot.yml`, which carries both rows above and groups each ecosystem's bumps into one weekly PR |

### Step 2: Enable `github-actions`

| Rule | Value |
|---|---|
| what it bumps | every `uses:` pin under `.github/workflows/`: the action pins in the four plain workflows, and the callers' pins |
| how a release of a CI repository reaches the integration | as that bump, with the pin's SHA and its version comment moved together in one PR — *The version model* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |

### Step 3: Enable `pip`

| Rule | Value |
|---|---|
| what it reads | `requirements.test.txt` and `pyproject.toml` at the repository root, the template's `directory: /` |
| what it bumps | a version pinned with `==`, as the template pins `pytest-homeassistant-custom-component`; a requirement with no version specifier gives it nothing to bump |

### Step 4: Leave `manifest.json` `requirements` to a deliberate PR

| Rule | Value |
|---|---|
| what Dependabot does with them | nothing: it cannot parse the manifest, and an open `>=` range resolves to the latest matching at install anyway |
| raising a `>=` floor | by hand, in a PR of its own |
| automating it | nothing in the stack does; anything that ever does is a reusable workflow in ha-integration-ci, never a script and a PR opener written into one repo |

### Step 5: Merge each PR once its checks are green

| Rule | Value |
|---|---|
| a version in `manifest.json` for a Dependabot PR to bump | none: `release.yml` writes the release tag into it at publish — *The three workflows* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| the label gate on a Dependabot PR | skipped, since a bot opened the PR — the `if:` of the `title-check` job, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/.github/workflows/pr-checks.yml |
| where a Dependabot PR lands in the release notes | under 🧰 Maintenance, from its `chore:` commit subject — `HEADINGS` in release-flow's `scripts/commit_summary.py`, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/scripts/commit_summary.py |
| a `github-actions` bump | merge it once its checks are green |
| a bump of the callers to a new major of ha-integration-ci | add to the PR the edits *The version model* lists under that version; it cannot go green without them — ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| a bump of the callers to an ha-integration-ci release on a new Python floor | raise ruff's `target-version` and `mypy.ini`'s `python_version` to that floor in the same PR, since the audit fails while they differ from the reusable workflows' — `version_sync.py`, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/scripts/version_sync.py |
| a `pip` bump | review it before merging; never auto-merge it — *A `pip` bump — Step 5* |

## Cases

### A `pip` bump — Step 5

A bump to `pytest-homeassistant-custom-component` moves the Home Assistant version the suite
tests against, and can raise the Python floor — *Step 4: Keep the harness pin and the Python
floor in lockstep* in `reference/testing.md`.

| Rule | Value |
|---|---|
| where the new floor is read | `requires_python` in https://pypi.org/pypi/pytest-homeassistant-custom-component/<version>/json, for the version the PR pins |
| the floor at the skill's last refresh | the harness row of `reference/freshness.md` |
| a bump that raises the floor | merge it only once the callers' pins sit on an ha-integration-ci release on that floor; the PR that moved those pins raised `target-version` and `python_version` — Step 5 |

**Fix:** check the new harness's floor before merging, and wait for the CI release when it rises.

### Re-copying a plain workflow — Step 2

The four plain workflows ship in `templates/.github/workflows/` with the pins of the skill's
last refresh — the GitHub action versions row of `reference/freshness.md` — so re-copying
one over a file Dependabot has bumped since moves its pins backwards. The callers ship with
no stored pin, so a re-copy cannot regress them.

**Fix:** diff before overwriting, then follow the plain-workflows row of *Step 4: Apply only
the sanctioned adaptations* in `reference/github-actions.md`.
