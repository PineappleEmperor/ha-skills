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
| what `release.yml` writes at publish, and why no PR carries a bump | *The three workflows* and *Implementation notes* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |
| what decides the next version | the merged PRs' labels, as `release-drafter.yml` under *The five workflows* in release-flow's README says, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| where to read what those labels so far imply | `CC label validation`'s step summary |

### Step 2: Leave the label to the stack

Never add a second labeler or patch a label by hand: the autolabeler and the label gate in
release-flow's `pr-checks.yml` own the label — `pr-checks.yml` under *The five workflows* in its README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md. If the gate says the
label is wrong, fix the title or the commits. What each title type maps to is the drafter
config, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/.github/release-drafter.yml, as release-flow's README says under *Called versus copied*, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md.

The `pull_request_target` deadlock and its narrow exception are *One exception, and it is
narrow — merge Step 2* in `reference/discipline.md`.

### Step 3: Publish the draft

Publish a draft from the GitHub release page; the tag is created at publish. How the two
drafts are kept and numbered is `release-drafter.yml` under *The five workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md;
what the body is built from is *The PR body — for reviewers, and nothing users read* in `reference/commits.md`.

## Cases

### A merged PR carried too low a type — Step 1

**Symptom:** the draft's version is lower than the change needs: a break merged under `fix:`
or `feat:`, so the draft resolves a patch or a minor.

**Fix:** merge a follow-up PR whose commit carries `!`, the breaking marker *Step 2: Write the subject in the Conventional Commits form* in `reference/commits.md` names, and says what the user has to change — never a label set by hand, as Step 2 says.

```bash
git checkout -b declare-break origin/main
git commit --allow-empty -m "feat!: <what the user has to change>"
git push -u origin declare-break
```

How that commit becomes the PR's title and the notes' Breaking Changes entry is
`auto-draft-pr.yml`, `pr-checks.yml` and `release-drafter.yml` under *The five workflows* in
release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md;
which label that title earns is the drafter config Step 2 names.

**Timing:** before the draft is published; once it is, declare the break the same way in the
next release.

### Release candidate — Step 3

An rc tag is `vX.Y.ZrcN`, marked as a prerelease. The manifest inside the zip then carries
the matching PEP 440 prerelease (`2.0.0rc1`), which AwesomeVersion, hassfest and HACS all
order below the final.

| what | lands in | do now | do then |
|---|---|---|---|
| Marketplace, replacing HACS, gives users the tag of the latest release that is not a prerelease, and an rc only to a user who turns on the repository's Pre-release switch, while it is newer than that release; while every release is an rc, it gives the default branch's newest commit | 2026.11 — https://contributors.home-assistant.io/marketplace/guides/releases/; the every-rc case, `_async_update_releases` and `version_to_install` in core's `homeassistant/components/marketplace/repositories/base.py` on `dev` | publish a final before telling users to install | nothing |

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

