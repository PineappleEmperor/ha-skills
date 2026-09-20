# Versioning and releasing

Read this when cutting or gating a release. Commit and PR-title conventions are
`reference/commits.md`; the GitHub-side settings are `reference/github-setup.md`;
Dependabot's setup is `reference/dependabot.md`.

**The release tag is the version — no PR, branch or committed manifest ever carries one.**

## Contents

1. Cutting a release
2. Step 1: Let the merged PRs' labels decide the version
3. Step 2: Leave the label to the stack
4. Step 3: Publish the draft
5. Cases
6. Release candidate — Step 3
7. The branch's PR has already merged — Step 3

## Cutting a release

### Step 1: Let the merged PRs' labels decide the version

What `release.yml` writes at publish, and why no PR ever carries a bump, is
ha-integration-ci's README (its table and version model). Which version the next release
gets is decided by the merged PRs' labels, as release-flow's README says under
`release-drafter.yml`, and `CC label validation`'s step summary reports what the labels so
far imply.

### Step 2: Leave the label to the stack

Never add a second labeler or patch a label by hand: the autolabeler and the label gate in
release-flow's `pr-checks.yml` own the label, and its README says how. If the gate says the
label is wrong, fix the title or the commits. What each title type maps to is the drafter
config, as release-flow's README says under *Called versus copied*.

The `pull_request_target` deadlock and its narrow exception are *Merge discipline — never
merge a red check* in `reference/discipline.md`.

### Step 3: Publish the draft

Publish a draft from the GitHub release page; the tag is created at publish. How the two
drafts are kept and numbered, and how the body is written and checked, is release-flow's
README under `release-drafter.yml`.

## Cases

### Release candidate — Step 3

An rc tag is `vX.Y.ZrcN`, marked as a prerelease. The manifest inside the zip then carries
the matching PEP 440 prerelease (`2.0.0rc1`), which AwesomeVersion, hassfest and HACS all
order below the final.

### The branch's PR has already merged — Step 3

A PR merges to `main` as soon as it is approved or auto-merged, and any commit pushed to
`feat/rcN` after that merge is stranded: not on `main`, and not in the release.

**Symptom:** `git status` on the branch looks fine.

**Timing:** check at the start of any rc work and before claiming work is pushed or live;
start the next branch immediately after a release rather than committing on to a `feat/rcN`
whose PR has merged.

```bash
git fetch origin
git log --oneline origin/main..feat/rcN
```

**Fix:** if `main` already contains a merge of this branch, the branch is spent — branch
fresh with `git checkout -b feat/rc(N+1) origin/main`, `git cherry-pick` the orphaned
commits oldest-first, push, then delete the stale branch so nothing lands on it again.

