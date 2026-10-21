# 07 — Task retrieval, after the final review's fixes

| Field | Value |
|---|---|
| Date | 2026-10-20 |
| Skill state | `e53b8a8` on `refactor/skill-standards` |
| Arm | treatment: `Explore` subagent, the prompt verbatim, reads limited to `plugins/ha/skills/` and URLs it gives |
| Reps | 3: haiku ×1, sonnet ×1, opus ×1 |
| Counting | a part passes only when every item of its key was answered from a file the router row names, or a URL that file or row gives |

| Run | A | B | C | D |
|---|---|---|---|---|
| haiku | partial: no highest-label-wins, no `!`-only, no never-hand-set-label | pass | pass | pass |
| sonnet | partial: no `!`-only, no never-hand-set-label | pass | pass | pass |
| opus | pass | pass | pass | pass |

| Part | Passed | After the router rewrite |
|---|---|---|
| A | 1/3 | 4/5 |
| B | 3/3 | 5/5 |
| C | 3/3 | 5/5 |
| D | 3/3 | 5/5 |

**Files opened for A:** haiku `versioning.md` only; sonnet `versioning.md`, `commits.md` and the release-flow README; opus `versioning.md`, `commits.md`, the release-flow README and its drafter config.

**Wrong answers:** none.

**Gaps the runs named:** the `categories` manifest key of https://contributors.home-assistant.io/blog/2026/10/20/integration-categories/ (opus).
