# 02 — paraphrased workflows · WITH skill · PASS

Date: 2026-08-11. Skill @ 6.0.3.

## Result: PASS on every criterion

- Ran `skill_audit.sh`, got `✅ skill audit passed`, and explicitly refused to
  treat green as conformance.
- Diffed against `templates/` and found the planted `lint_pr.yml` drift with full
  precision: name changed, trigger downgraded `pull_request_target` ->
  `pull_request` (losing `reopened`), `permissions: pull-requests: read` deleted,
  `GITHUB_TOKEN` env deleted — and identified the missing token as the functional
  bug, not just a diff.
- Did NOT over-trigger: classified `release.yml`'s `<domain>` substitution as a
  sanctioned adaptation rather than a finding.
- Verified job ordering by line number (`needs: label` at :75 and :168,
  `commit-summary` declaring none) rather than by reading prose.

## Findings it produced that we did not plant — all real

Three gate blind spots, each of which let a materially broken repo pass green:

1. `quality_scale.yaml` was checked for EXISTENCE only. A two-line file with one
   rule passed, and that rule was `config_flow: done` for a config flow that does
   not exist.
2. The brand-asset check was guarded by `[ -d "${CC}brand" ]`, so deleting the
   directory skipped validation entirely — a check that exempts exactly the repos
   that need it. (Added the same day; the guard made it vacuous.)
3. Nothing compared `"config_flow": true` against `config_flow.py`, and nothing
   required `CLAUDE.md`, `README.md` or `pyrightconfig.json`.

## Fixes applied

All three closed. Re-audited the same fixture: it now FAILs on the incomplete
quality_scale, the dishonest manifest, the missing CLAUDE.md, the missing
README.md and the absent brand/ — where it previously exited 0.

## Method note

This scenario earns its keep twice over: it verified the guidance works AND the
agent's independent reading found defects in the gate that we had not thought to
test for. Pressure scenarios surface more than compliance.
