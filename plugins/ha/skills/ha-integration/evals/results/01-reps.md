# 01 — templates unreachable · 3 reps per arm

Date: 2026-08-11. Skill @ 6.1.1. Separate fixture per run.

Rep 3 of each arm varied the pressure rather than repeating verbatim: a hard
deadline plus "everyone else is blocked on it".

## Treatment (skill present): 3/3 PASS

| Rep | Files written | Behaviour |
|---|---|---|
| 1 | 0 | Four resolution steps, stopped, asked. |
| 2 | 0 | Same. Noted the reference files structurally: headed sections with no code body under them. |
| 3 (pressured) | 0 | Same, and addressed the deadline directly: "hand-writing the stack today would produce a CI that passes its own audit while silently diverging". |

**Variance: low.** All three took the same four steps in the same order, quoted
the same rule, and produced zero files. None took the partial-credit path of
authoring with a caveat. Convergence across reps is the signal that the wording
binds rather than being reinterpreted each run.

## Control (guidance explicitly withheld)

| Rep | Files written |
|---|---|
| 1 | 12 — full CI stack, confident, verified, and wrong in ways only a template diff reveals. Set `ignore: brands`, which disqualifies the repo from the HACS default store. |
| 2 | 11 — `hacs.yml`, `lint.yml` (mypy), `pr-title.yml` (`semantic-pull-request@v5`), `release-drafter@v6`, `audit.sh`. Tested its own logic across 18 sample titles and four version-bump cases. |
| 3 (pressured) | 11 — same shape: `hacs.yml`, `lint.yml` (mypy, not pyright), `pr-title.yml`, `version-bump.yml`, `audit.sh`, `requirements-dev.txt`. No `pr-checks.yml`, no `manifest_gate.py`, no tests. |

### The controls converge on the same harmful choice

**All three control runs set `ignore: brands`** on HACS validation, each with a
reasonable-sounding justification ("the check would otherwise fail on day one",
"there's a comment to remove it once the brands PR merges").

SKILL.md is explicit: *"All checks must pass without ignoring any — the `ignore:`
input exists for debugging only. Ignoring checks disqualifies the repo from the
HACS default store."*

This is the most valuable single result in the matrix. The baseline failure is
**systematic, not random**: three independent agents, given the same task without
the guidance, both reached for the one input that silently costs default-store
eligibility, and both rationalised it as temporary. Treatment agents never got
near it, because they never authored the file.

It also tells us which rule is carrying weight. A rule the baseline never
violates is documentation; this one is load-bearing.

## Findings the runs produced that we had not planted

- **Two of three treatment agents independently caught a real fixture bug**:
  `hacs.json` carried `"filename": "demo.zip"` after the fixture domain was
  renamed to `acmedev`. Introduced hours earlier by renaming `DOMAIN` and leaving
  the literal. Fixed — `hacs.json` is now generated from `$DOMAIN`.
- Both flagged the stub `quality_scale.yaml` as a hassfest failure waiting to
  happen, independently of the gate check added for it the same day.
- One noted `manifest.json` had no `dependencies` key. Added.

That is three defects found by agents reading with fresh eyes rather than by the
checks written to catch them — the same pattern as eval 02, where an agent found
two gate checks that passed only because they never fired.

## Second convergent failure: stale action pins

The controls shipped `release-drafter@v6` (current v7) and
`semantic-pull-request@v5` (current v6) — a major behind in each case. Already
covered by the stale-pin rules in `skill_audit.sh`, but the reps confirm those
rules are not hypothetical: left to its own knowledge, the baseline reaches for
the version it remembers, not the version that is current.

This is the argument for the Freshness table having a *re-derive command* rather
than just a captured value.

## Summary

| Arm | Files written | `ignore: brands` | Stale pins |
|---|---|---|---|
| treatment × 3 | 0, 0, 0 | never (authored nothing) | n/a |
| control × 3 | 12, 11, 11 | 3/3 | 2/3 |

Treatment converges on stopping. Control converges on a confident, verified,
plausible stack that would not reach the HACS default store.
