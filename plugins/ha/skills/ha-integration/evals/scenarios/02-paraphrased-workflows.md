# 02 — Audit a repo whose CI was written from memory

Guards the audit mode. The fixture is the state `ha-lego` was actually in: CI that
looks right, and diverges from the files it was supposed to be copied from.

## Setup

```bash
./make_fixture.sh 02
```

The fixture is a copy of the testbed integration with its history stripped, so it
starts out genuinely conforming rather than approximately so. Two divergences are
then planted:

1. **`hacs-validate.yml` rewritten from its description.** It is one of the four
   workflows a scaffold still copies whole, so there is a template to compare it
   against. The rewrite drops the daily schedule and the `category: integration`
   input, and HACS validation then checks nothing while reporting green.
2. **`pr-checks.yml` written from memory as a caller.** The `uses:` line is
   correct, so the caller checks pass, but the trigger is `pull_request` rather
   than `pull_request_target` and the `pull-requests: write` permission is gone —
   what that costs a fork PR is release-flow's README under `pr-checks.yml`. The
   caller-model shape of the same mistake.

The agent gets the **full skill, `templates/` included** — this scenario tests
whether it *uses* them, not whether it can find them.

## Prompt

> Audit this repo against the ha-integration skill and report whether it was
> followed.

## Pass

The agent finds **both**. The mechanical audit (run as `SKILL.md`'s mode table
says) reports the second and says nothing about the first, so an agent that
stops at the gate reports one of two. The first is only reachable by comparing
`hacs-validate.yml` against `templates/.github/workflows/hacs-validate.yml`, per
file, and the caller workflows against the blocks in the three READMEs.

It should also read the pinned SHAs as *current* rather than as findings, and not
report the testbed's own `ruleset.json` context list as drift — distinguishing a
sanctioned adaptation from a divergence is the actual skill.

## Fail

- Runs the audit, reports its one failure, calls the rest conformant. This is the
  baseline behaviour and the exact failure being guarded.
- Reads each workflow and judges it "equivalent" without comparing. Watch for
  *"hacs-validate.yml looks correct — it runs the HACS action as described."* It
  does. It is still wrong.
- Reports every pinned SHA as something to verify, or the caller pins as drift
  because they are not the newest release (over-triggering; a checklist that cries
  wolf gets skipped).

## Variant worth running

Revert the `pr-checks.yml` drift before the run, leaving only the `hacs-validate.yml`
one. The gate then passes clean and the whole finding depends on the comparison —
the original form of this scenario, and the harder arm.

## Note

The fixture clones `PineappleEmperor/ha-ci-testing`, so it needs network. Basing it
on the testbed rather than a synthetic tree is deliberate: a hand-built conforming
repo would have to enumerate the whole quality-scale rule set and a brand icon, and
be re-enumerated every time the audit grows a check.
