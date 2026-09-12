# 04 — a PR from a fork gets labelled

**Status: NOT RUNNABLE with a single GitHub account.** Written out so it can be
run the moment a second identity exists, rather than left as an unresolved claim.

## What is being tested

The `pr-checks.yml` caller triggers on `pull_request_target` so that fork PRs can
be labelled and commented on; what plain `pull_request` would cost a fork PR is
release-flow's README under `pr-checks.yml`. That reasoning has **never been
executed** against a fork.

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
  PR on the testbed has been labelled by `pr / CC labelling`, and
  `pr / CC label validation` has posted its comment (ha-ci-testing PR #9).

NOT covered:

- That a fork PR's token under plain `pull_request` is read-only (documented
  GitHub behaviour, untested here).
- That a fork PR's token under `pull_request_target` is writable **through a
  caller into release-flow's reusable workflow**.

## Procedure, once a second identity exists

1. From account B, fork the testbed.
2. On the fork, branch and push a change with a **labellable** title
   (e.g. `fix: trivial typo`).
3. Open a PR from the fork into `main`.
4. Check, in order:
   - `pr / CC labelling` **ran** and applied a label.
   - `pr / CC label validation` ran after it (`needs:` inside release-flow's
     workflow holds across the fork boundary).
   - Retitle the PR so the label is wrong: the validation job's comment naming
     the right title proves write access, since a read-only token cannot comment.
     Fix the title and confirm the comment is withdrawn.
   - `lint / CC title validation` ran.
5. **Adversarial half.** On the fork, replace `.github/workflows/pr-checks.yml`
   with a body carrying a `run: echo PWNED` step, and re-push. The base branch's
   caller must run instead — `pull_request_target` loads from the base — and the
   run log must show **no checkout of the consumer** — the one `actions/checkout`
   there fetches release-flow itself into `.release-flow`. If `PWNED` appears, or
   any step checked out the fork's head, `pull_request_target` is executing fork
   code with a writable token — a critical finding, not a test failure.

## Pass

Steps 4 and 5 both hold: the fork PR is labelled and commented on, and no
fork-authored code executes.

## Fail

Any of: the labelling job does not run; the validation job cannot comment
(read-only token — the design does not work); or the marker from step 5 appears
in the log (the design is actively dangerous, and the caller must revert to
`pull_request` with fork labelling accepted as unsupported).
