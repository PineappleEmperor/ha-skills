# 2026-08-21, the CI contract

Closed rows, moved here from the register when they cleared. Formatting may be repaired; a
claim later found false gets a new row in the register rather than an edit here, so this
stays a transcript that can be checked against git.

| # | Finding | Fix | Commit |
|---|---|---|---|
| 99 | **Skill prose outside `reference/` may still describe the copy model.** Contract item 13. `SKILL.md`, `README.md` and `docs/` were not re-read after the tag-driven and, once row 98 lands, the pointer-based delivery. One read, one list of restatements to delete rather than sync | Every prose file read after the caller-based delivery: `SKILL.md`, `README.md`, the reference set and `docs/workflow-map.md`. Each CI fact now points at the README that owns it, and the pairs rows 119 and 124 list went with the sentences that carried them; `workflow-map.md` is an eight-line stub until the maintainer's `git rm`. Done as stated | the thirteen `docs:` commits 45a0799 through 0958a3c, then 1f2f342 |
