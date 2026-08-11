# 04 — a PR from a fork gets labelled

**Status: NOT RUNNABLE with a single GitHub account.** Written out so it can be
run the moment a second identity exists, rather than left as an unresolved claim.

## What is being tested

`pr-checks.yml` uses `pull_request_target` specifically so fork PRs can be
labelled, commented on, and have their body updated. Under plain `pull_request`,
GitHub gives a fork PR's workflow a **read-only** `GITHUB_TOKEN`, so the
autolabeler silently does nothing and the PR gets no release category — the same
class of gap that made `create-dev-pr` unusable for outside contributors.

That reasoning is documented in the skill and has **never been executed**.

## Why it can't be run here

Forking requires a second GitHub identity: GitHub will not fork a repository into
the account that owns it, and the working account has no organisations. Verified
2026-08-11 — `gh api user/orgs` empty, `forks` count 0.

## What HAS been verified, and what that does and doesn't cover

Covered:

- **`pull_request_target` runs the workflow from the BASE branch.** Demonstrated
  twice: a PR fixing `pr-checks.yml` was still checked by the broken copy on
  `main`, and a PR introducing a new `pull_request_target` workflow did not run it
  at all. That is the half of the mechanism this design depends on.
- **The token is writable for same-repo PRs under `pull_request_target`** — every
  PR in the repo has been labelled by the `label` job.

NOT covered:

- That a fork PR's token under plain `pull_request` is read-only (documented
  GitHub behaviour, untested here).
- That a fork PR's token under `pull_request_target` is writable **in this repo's
  configuration**.

## Procedure, once a second identity exists

1. From account B, fork the repo.
2. On the fork, branch and push a change with a **labellable** title
   (e.g. `fix: trivial typo`).
3. Open a PR from the fork into `main`.
4. Check, in order:
   - `PR Checks / Label from title` **ran** and applied a label.
   - `title-check` ran after it (`needs: label` holds across the fork boundary).
   - `commit-summary` updated the PR body — this proves write access, since a
     read-only token cannot edit a PR body.
   - `version-gate` read the fork's `manifest.json` **over the API** and did not
     check out the fork's head. Confirm in the run log that the checkout step
     resolved `base.sha`, not the fork's SHA.
5. **Adversarial half.** On the fork, add a commit that writes a marker file in
   `scripts/manifest_gate.py` (e.g. `print("PWNED")`). Re-push. The
   `version-gate` job must run the BASE copy and never print the marker. If it
   does print, `pull_request_target` is executing fork code with a writable
   token — a critical finding, not a test failure.

## Pass

Steps 4 and 5 both hold: the fork PR is labelled and its body updated, and no
fork-authored code executes.

## Fail

Any of: the label job does not run; `commit-summary` cannot edit the body
(read-only token — the design does not work); or the marker from step 5 appears
in the log (the design is actively dangerous and must be reverted to
`pull_request` with fork labelling accepted as unsupported).
