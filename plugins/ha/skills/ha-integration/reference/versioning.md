# Versioning and releasing

How an integration is versioned and released. Commit and PR-title conventions are
`reference/commits.md`; the GitHub-side settings are `reference/github-setup.md`.

- Where the version comes from
- Releasing, rc and final
- Labels are the stack's, not yours
- Orphaned-branch trap

### Where the version comes from

The release tag: what `release.yml` writes at publish, and why no PR ever carries a bump,
is ha-integration-ci's README (its table and version model). Which version the next
release gets is decided by the merged PRs' labels, as release-flow's README says under
`release-drafter.yml`, and `CC label validation`'s step summary reports what the labels so
far imply.

### Releasing, rc and final

Publish a draft from the GitHub release page; the tag is created at publish. How the two
drafts are kept and numbered, and how the body is written and checked, is release-flow's
README under `release-drafter.yml`. What is yours to know: an rc tag is `vX.Y.ZrcN`, marked
as a prerelease, and the manifest inside the zip then carries the matching PEP 440
prerelease (`2.0.0rc1`), which AwesomeVersion, hassfest and HACS all order below the final.

### Labels are the stack's, not yours

Never add a second labeler or patch a label by hand: the autolabeler and the label gate in
release-flow's `pr-checks.yml` own the label, and its README says how. If the gate says the
label is wrong, fix the title or the commits. What the ten title types map to is
`reference/commits.md`.

A `pull_request_target` workflow loads from the base branch, so a PR that fixes one of them
is still judged by the broken copy; that deadlock and its narrow exception are *Merge
discipline* in `reference/discipline.md`.

Dependabot's setup, grouping and floor management live in `reference/dependabot.md`.

### Orphaned-branch trap

A PR merges to `main` as soon as it's approved/auto-merged. **Any commit you push to `feat/rcN` after that merge is stranded** — it's not on `main` and not in the release, even though `git status` on the branch looks fine. **Guard every time, not just when you remember:**
1. At the **start** of any rc work and before claiming work is "pushed/live", run `git fetch origin` then `git log --oneline origin/main..feat/rcN`. If `main` already contains a merge of this branch, the branch is spent.
2. When a cycle has merged/released: **branch fresh** `git checkout -b feat/rc(N+1) origin/main`, `git cherry-pick` the orphaned commits (oldest-first), push, then delete the stale branch so nothing lands on it again. Nothing in the branch carries a version — the rc number is the tag you publish.
3. Don't keep committing onto a `feat/rcN` whose PR has merged — start the next branch immediately after a release.

