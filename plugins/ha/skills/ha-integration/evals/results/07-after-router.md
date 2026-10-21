# 07 — Task retrieval, after the router rewrite

| Field | Value |
|---|---|
| Date | 2026-10-20 |
| Skill state | `95665ae`, an unpushed commit later split into `7c28a1c`…`b8c8cc6` on `refactor/skill-standards`; its `SKILL.md` differs from `b8c8cc6`'s only in the description, the overview and lead-in wording, `dev` in place of `2026.10.0` in two core URLs, and a closing `/compact` line; reference files as at `a16ec54` |
| Arm | treatment: `Explore` subagent, the prompt verbatim, reads limited to `plugins/ha/skills/` and URLs it gives |
| Reps | 5: sonnet ×3, haiku ×1, opus ×1 |
| Counting | a part passes only when every item of its key was answered from a file the router row names, or a URL that file or row gives |

| Run | A | B | C | D |
|---|---|---|---|---|
| sonnet 1 | pass | pass | pass | pass |
| sonnet 2 | pass | pass | pass | pass |
| sonnet 3 | pass | pass | pass | pass |
| haiku | fail: "relabel it in GitHub", against `versioning.md` Step 2 | pass | pass | pass |
| opus | pass | pass | pass | pass |

| Part | Passed | Before the rewrite |
|---|---|---|
| A | 4/5 | 0/5 |
| B | 5/5 | 0/5 |
| C | 5/5 | 4/5 |
| D | 5/5 | 5/5 |

**Partial reads:** haiku read `versioning.md`, `commits.md`, `panels.md` and `freshness.md` in part.

**Gaps the runs named:** a PR already merged with the wrong type (sonnet 3, opus); no URL for the consumer's drafter config (opus); `dependabot.md` Step 5 against its pip-bump case (opus); the Marketplace guide's breaking-change note at the top of release notes (opus).
