# Versioning and releasing

Read this when cutting or gating a release.

**The release tag is the version.**

## Contents

1. Cutting a release
2. Step 1: Let the merged PRs' labels decide the version
3. Step 2: Leave the label to the stack
4. Step 3: Publish the draft
5. Cases
6. A merged PR carried too low a type — Step 1
7. Release candidate — Step 3
8. The branch's PR has already merged — Step 3

## Cutting a release

### Step 1: Let the merged PRs' labels decide the version

| Rule | Value |
|---|---|
| what decides the next version | the labels on the PRs merged since the last full release; each carries a semver step, and the highest wins — `release-drafter.yml` under *The five workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| which label a PR gets | from its title: `feat!:` or any `type!:` → `xfeat`, a major; `feat:` → `feature`, a minor; `fix:` → `fix`, a patch; `chore:`, `docs:`, `refactor:`, `perf:`, `test:`, `build:`, `ci:` or `style:` → `chore`, a patch — the repository's own `.github/release-drafter.yml`, copied from release-flow's |
| where to read the version those labels so far imply | `CC label validation`'s step summary — `pr-checks.yml` under *The five workflows* in release-flow's README |
| what `release.yml` writes at publish, and why no PR carries a bump | *The three workflows* and *Implementation notes* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |

### Step 2: Leave the label to the stack

Never add a second labeler or patch a label by hand: the autolabeler and the label gate own
the label — `pr-checks.yml` under *The five workflows* in release-flow's README. If the gate
says the label is wrong, fix the title or the commits, in the form *Step 2: Write the subject
in the Conventional Commits form* in `reference/commits.md` gives.

The `pull_request_target` deadlock and its narrow exception are *One exception, and it is
narrow — merge Step 2* in `reference/discipline.md`.

### Step 3: Publish the draft

Publish a draft from the GitHub release page; the tag is created at publish. How the two
drafts are kept and numbered, and how the body is written and checked, is
`release-drafter.yml` under *The five workflows* in release-flow's README,
https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md.

| Rule | Value |
|---|---|
| the order of the body's sections | 🚨 Breaking Changes, then Features, Fixes, Maintenance and Other — `ORDER` in release-flow's `scripts/commit_summary.py`, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/scripts/commit_summary.py |
| where a change a user must act on goes | at the top of the notes — *Write release notes*, https://contributors.home-assistant.io/marketplace/guides/releases/index.md; so its commit carries `!` on its type, which files it under Breaking Changes |

## Cases

### A merged PR carried too low a type — Step 1

A break merged under `fix:` or `feat:` labels its PR `fix` or `feature`, so the draft
resolves a patch or a minor and lists the break under Fixes or Features, where it stays.
The label gate passes it, since it reads the same commit subjects.

**Symptom:** the draft's version, or the version in `CC label validation`'s step summary, is
lower than the change needs.

**Fix:** leave the merged PR's label and the draft alone. Merge a follow-up PR whose commit
carries `!` on its type and says what the user has to change; the draft PR takes its title
from that commit — `auto-draft-pr.yml` in release-flow's README — so it is labelled `xfeat`,
the draft resolves a major, and the break heads the notes.

```bash
git checkout -b declare-break origin/main
git commit --allow-empty -m "feat!: <what the user has to change>"
git push -u origin declare-break
```

**Timing:** before the draft is published. Once it is, the break has shipped as a patch or a
minor; declare it the same way in the next release.

### Release candidate — Step 3

An rc tag is `vX.Y.ZrcN`, marked as a prerelease. The manifest inside the zip then carries
the matching PEP 440 prerelease (`2.0.0rc1`), which AwesomeVersion, hassfest and HACS all
order below the final.

| what | lands in | do now | do then |
|---|---|---|---|
| Marketplace, replacing HACS, gives users the tag of the latest release that is not a prerelease, and an rc only to a user who turns on the repository's Pre-release switch, while it is newer than that release; while every release is an rc, it gives the default branch's newest commit | 2026.11 — *Pre-releases*, https://contributors.home-assistant.io/marketplace/guides/releases/index.md; the every-rc case, `_async_update_releases` and `version_to_install` in https://raw.githubusercontent.com/home-assistant/core/dev/homeassistant/components/marketplace/repositories/base.py | publish a final before telling users to install | nothing |

### The branch's PR has already merged — Step 3

A PR merges to `main` as soon as it is approved or auto-merged, and any commit pushed to
`feat/rcN` after that merge is stranded: not on `main`, and not in the release.

**Symptom:** `git status` on the branch looks fine.

**Timing:** check at the start of any rc work and before claiming work is pushed, and branch
fresh the moment a release is cut rather than committing on to a merged `feat/rcN`.

```bash
git fetch origin
git log --oneline origin/main..feat/rcN
```

**Fix:** where `main` already carries a merge of this branch, branch fresh from it:

```bash
git checkout -b feat/rc$((N+1)) origin/main
git cherry-pick <orphaned commits, oldest first>
git push -u origin feat/rc$((N+1))
git push origin --delete feat/rcN
```

