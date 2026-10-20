# 07 — Task retrieval, skill before the rewrite

| Field | Value |
|---|---|
| Date | 2026-10-20 |
| Skill state | `e4a9f7b` on `feat/refresh-2026-9`, read from a snapshot of that commit |
| Arm | treatment: `Explore` subagent, the prompt verbatim, reads limited to `plugins/ha/skills/` and URLs it gives |
| Reps | 5: sonnet ×3, haiku ×1, opus ×1 |
| Counting | a part passes only when every item of its key was answered from the file the router row names, or a URL that file or row gives |

| Run | A | B | C | D |
|---|---|---|---|---|
| sonnet 1 | fail: no `!` marker | fail: no URL | pass | pass |
| sonnet 2 | fail: `!` only via `commits.md`; also offered a `BREAKING CHANGE` form | fail: page found by browsing `llms.txt` | pass | pass |
| sonnet 3 | fail: no `!` marker | fail: no URL | pass | pass |
| haiku | fail: no `!` marker | fail: no URL | fail: no HA-version reason | pass |
| opus | fail: `!` only via `commits.md` | fail: page found by browsing `llms.txt` | pass | pass |

| Part | Passed |
|---|---|
| A | 0/5 |
| B | 0/5 |
| C | 4/5 |
| D | 5/5 |

**Partial reads:** sonnet 1 read `patterns.md` to line 593 of 819 and `testing.md` to line 84.

**Pointers no run could follow:** release-flow's README (every run), ha-integration-ci's README (every run), ha-panel-ci's README (opus).
