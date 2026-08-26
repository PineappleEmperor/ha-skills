# 06 — Router selection, post-fix run

- **Date:** 2026-08-26
- **Skill state:** `feat/reference-link-check`, after the second backlog was cleared
- **Arm:** treatment (fresh subagent, no skill preloaded, told only where the three skills live)
- **Verdict:** PASS, 5/5

| Request | Expected | Answered | By |
|---|---|---|---|
| A log triage | `ha-triage`, no reference file | same | `ha-integration/SKILL.md` negative-routing block, then `ha-triage/SKILL.md` line 8 |
| B reconfigure flow | `ha-integration` → `patterns.md` | same | Modify row of the mode table |
| C panel dark mode | `ha-panel-design`, no reference file | same | negative-routing block, then `ha-panel-design/SKILL.md` line 8 |
| D release process | `ha-integration` → `github-setup.md` | same | Release / repo setup row |
| E setup-entry test | `ha-integration` → `testing.md` | same | Test row |

**Reference files opened to decide: zero.** All five were answerable from the router layer —
three `SKILL.md` files and nothing else. None was reached by elimination, which the scenario
counts as a failure even when the destination is right.

## What this run changed

- The scenario's own answer key was stale: it expected E → `patterns.md` (testing sections),
  written before `testing.md` existed. Corrected to `testing.md` before the run.
- Earlier in the same session the line *"This skill is self-contained: everything is in this
  file…"* was deleted from both single-file skills as meta-commentary. That line is the only
  sentence a router can cite for "no reference file to read next", so removing it would have
  turned A and C into answers-by-elimination — a scenario failure. Restored, reworded as
  reader guidance (*"Work from this file alone"*), and the run then cited it for both.

## Findings not planted by the scenario

- **B is near-ambiguous.** The Modify row names `quality-scale.md` as its only alternative,
  scoped to *adding a platform*. A reconfigure flow wins `patterns.md` by that scope
  qualifier rather than by anything in the row naming flows. The confirming line
  (`Add reconfigure flow`) sits ~64 lines below the table.
- **D is ordered, not ambiguous.** The row names four files and sequences them with "Then…",
  which is what stops a reader starting in the wrong one.
- **`ha-triage` did not appear in the session's skill registry**, though the directory exists
  and both other routers name it. Registration is directory-based with no explicit skill
  list, so this is stale session state after the `ha-log-triage` → `ha-triage` rename, not a
  repo defect. Confirm in a fresh session before trusting A end to end.
