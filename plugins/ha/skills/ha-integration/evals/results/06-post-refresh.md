# 06 — Router selection, 2026-10-02 to 2026-10-03

- **Date:** runs 1 to 5 on 2026-10-02, runs 6 to 8 on 2026-10-03
- **Skill version:** `feat/refresh-2026-9`, the router per run in the table; runs 3 and 4 read
  uncommitted text on it
- **Arm:** treatment only; three fresh read-only reps per run, told only where the skills live
- **Verdict:** A, B, C and E pass in every run. D fails runs 1, 3 and 4: each rep guessed
  between router rows, which the scenario counts as a routing failure, since the router did
  not say it. D passes runs 2 and 5: each rep cited one row and was unsure only whether "new"
  means never released, which the request does not say. D fails run 6, as runs 1, 3 and 4.
  In run 7 every rep answered `scaffold.md` from the Scaffold row's wording; one decided it
  outright and two still called it a guess against Release, so D fails for those two. No rep
  opened a reference file. D passes run 8: each rep cited the Scaffold row and ruled the
  Release row out on its own wording.

Eight runs share this file, where the evals README asks for one file per run.

| Run | Router (`SKILL.md`) | D answered | Reps unsure of D | Unsure about |
|---|---|---|---|---|
| 1 | `5a89cae` | `github-setup.md` ×3 | 3 | Release row or Repo setup row |
| 2 | `24bb63d`: Release and Repo setup split on whether the repository has released | `github-setup.md` ×3 | 3 | whether "new" means never released |
| 3 | Release row adds "a repository's first release comes after Repo setup", not committed | `github-setup.md` ×3 | 3 | Release, Repo setup or Workflow row |
| 4 | the Scaffold row without "not released yet", not committed | `versioning.md` ×3 | 3 | which row; each read the repository as existing |
| 5 | `0ad281a`: Scaffold row adds "setting up a repository that has not released yet" | `scaffold.md` ×3 | 3 | whether "new" means never released |
| 6 | `b066266`: Scaffold row rewritten by `b83b8bc`, no release clause | `versioning.md` ×3 | 3 | Release, Scaffold, Repo setup or Workflow row |
| 7 | `57c1033`: Scaffold row adds "including setting up its CI and release process" | `scaffold.md` ×3 | 2 | Release, for a repository that already exists |
| 8 | `6d7c3a9`: Release row adds "once the release process is set up" | `scaffold.md` ×3 | 0 | — |

**Key for D:** at `5a89cae`, `github-setup.md` or `versioning.md`. `0ad281a` changed it to
`scaffold.md` alone, before run 5; `7482d31` added `versioning.md` back, after run 5. After
run 8 it is `scaffold.md` alone again, since the Release row at `6d7c3a9` excludes setting
the process up.

**Router since:** run 8 read the router as it stands at `6d7c3a9`.

## Findings not planted by the scenario

- **A matches two triage rows.** Most reps noted that "every entity went unavailable" also fits the
  Connection row; every rep chose *Unexpected reply* on the quoted log line, and both rows
  name `patterns.md`.
- **C has a decoy that held.** Several reps noted that `ha-triage`'s Panel row and `ha-integration`'s
  Panel row both mention panels; every rep routed C to `panel-design.md`.
