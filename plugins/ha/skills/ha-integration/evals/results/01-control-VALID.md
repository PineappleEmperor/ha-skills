# 01 — templates unreachable · TRUE CONTROL (guidance explicitly withheld) · RED

Date: 2026-08-11. Same fixture and task as the treatment arm; the skill was
withheld by explicit constraint, not by hiding files.

## Result: the failure the scenario exists to catch, reproduced in full

Wrote **12 files** from its own knowledge. Never paused, never asked. The work
was competent by ordinary standards — it parsed every YAML, ran `bash -n` over
each embedded `run:`, and tested the version-gate logic end-to-end in a throwaway
git repo across 10 version-comparison cases including prereleases.

That competence is the point. This is not sloppy output that review would catch;
it is a confident, verified, plausible CI stack that is wrong in ways only a diff
against the templates reveals.

## What it actually produced vs the canonical stack

| Canonical | Control wrote |
|---|---|
| `hacs_validate.yml`, **no `ignore:`** | `hacs.yml` with **`ignore: brands`** |
| `hassfest_validate.yml` | `hassfest.yml` with `ignore: brands` |
| `python_validate.yml` (ruff + **pyright** + pytest, py3.14) | `lint.yml` (ruff + **mypy**, py3.13, no tests) |
| `lint_pr.yml` (semantic-pull-request **@v6**) | `pr-title.yml` (**@v5** — stale) |
| `pr-checks.yml` (4 ordered jobs) | absent; a separate `version-bump.yml` instead |
| `scripts/skill_audit.sh` | `scripts/audit.sh` — hand-written |
| `scripts/manifest_gate.py` + tests | absent |
| `scripts/commit_summary.py` + tests | absent |
| `conftest.py`, `requirements.test.txt` | absent; `requirements-dev.txt` instead |
| `.gitignore` | absent |

**`ignore: brands` is the materially harmful one.** The skill states that
ignoring any HACS check disqualifies the repo from the default store, and that
the `ignore:` input exists for debugging only. The control reached for it to make
a failing check pass — confidently, with no signal that it was trading away
store eligibility.

Every filename differs, so a later `diff` against `templates/` would not even
align. The stale `@v5` pin is exactly what the audit's stale-pin rules exist for,
and the hand-written `audit.sh` would have graded its own homework.

## Conclusion

Control writes 12 files; treatment writes zero and asks. The guidance is
load-bearing, and scenario 01 is now a valid RED/GREEN pair rather than a
compliance observation.
