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

| Rule | Value |
|---|---|
| what `release.yml` writes at publish, and why no PR carries a bump | ha-integration-ci's README — its table and version model |
| what decides the next version | the merged PRs' labels, as release-flow's README says under `release-drafter.yml` |
| where to read what those labels so far imply | `CC label validation`'s step summary |

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

**Timing:** check at the start of any rc work, and again before claiming work is pushed.

```bash
git fetch origin
git log --oneline origin/main..feat/rcN
```

**Fix:** where `main` already carries a merge of this branch, branch fresh from it:

```bash
git checkout -b feat/rc$((N+1)) origin/main
git cherry-pick <orphaned commits, oldest first>
git push origin --delete feat/rcN
```

