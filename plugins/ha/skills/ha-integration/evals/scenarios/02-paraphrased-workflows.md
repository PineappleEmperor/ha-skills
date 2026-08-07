# 02 — Audit a repo whose workflows were paraphrased

Guards Mode 4. The fixture is the state `ha-lego` was actually in: a CI stack
that looks right, passes the mechanical gate clean, and diverges from the
templates.

## Setup

```bash
./make_fixture.sh 02
```

The agent gets the **full skill, `templates/` included** — this scenario tests
whether it *uses* them, not whether it can find them.

Planted drift: `.github/workflows/lint_pr.yml` rewritten from its one-line
description. It drops `pull_request_target`, the `permissions` block and the
`GITHUB_TOKEN` env — so PR-title linting silently stops working on forks. Every
canonical file is present, so `bash scripts/skill_audit.sh` exits 0.

## Prompt

> Run a Mode 4 audit on this repo and report whether the ha-integration skill
> was followed.

## Pass

The agent diffs `.github/` and `scripts/` against `templates/`, reports
`lint_pr.yml` as diverged with the specific hunks, and does **not** treat the
green `skill_audit.sh` as evidence of conformance. It should also note the
`release.yml` `<domain>` substitution as a *sanctioned* adaptation rather than
listing it as a finding — distinguishing the two is the actual skill.

## Fail

- Runs `skill_audit.sh`, sees exit 0, reports conformance. This is the baseline
  behaviour and the exact failure being guarded.
- Reads each workflow and judges it "equivalent" / "functionally the same"
  without diffing. Watch for *"lint_pr.yml looks correct — it runs the semantic
  PR title check as described."* It does. It is still wrong.
- Flags the `<domain>` substitution as drift (over-triggering; a checklist that
  cries wolf gets skipped).

## Variant worth running

Delete `scripts/manifest_gate.py` from the fixture before the run. Post-R3 the
mechanical gate catches it; before R3, only the diff did. Useful for confirming
the gate change actually fires.
