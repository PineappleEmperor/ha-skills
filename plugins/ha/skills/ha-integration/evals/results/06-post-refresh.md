# 06 — Router selection, after the 2026.9 refresh

- **Date:** 2026-10-02
- **Skill state:** `feat/refresh-2026-9` at `5a89cae`, then the Release and Repo setup rows rewritten
- **Arm:** treatment, three reps per run (fresh read-only subagent, told only where the skills live)
- **Verdict:** PASS, 3/3 reps in both runs, 15/15 answers each

The run row 224 asks for: the router was converted to the schema's mode table and
`ha-triage` became a router by fault class since the last run of this scenario.

## First run, at `5a89cae`

| Request | Expected | Answered, all three reps | By |
|---|---|---|---|
| A firmware log line | `ha-triage` → `ha-integration/reference/patterns.md` | same | the *Unexpected reply* row; `ha-integration`'s description disclaims fault triage |
| B reconfigure flow | `ha-integration` → `patterns.md` | same | the Modify row |
| C panel dark mode | `ha-integration` → `panel-design.md` | same | the Panel design row |
| D release process, new repo | `ha-integration` → `github-setup.md` or `versioning.md` | `github-setup.md` | the Repo setup row's "first release" |
| E setup-entry test | `ha-integration` → `testing.md` | same | the Test row |

**Reference files opened to decide: zero**, in every rep.

**D was a guess in all three reps.** The Release row ("cutting or gating a release") and
the Repo setup row ("first release") both claimed a new repository's first release, and each
rep chose between them on its own reading of "new". The destination was in the key, but the
scenario counts an answer the router did not decide as a routing failure.

## The fix, and the second run

The two rows now split on whether the repository has released: Repo setup is "a repository
that has never released", and Release applies "once the repository has released before; one
that never has starts at Repo setup".

All three reps again answered every request as the key expects, opening no reference file.
Each answered D by quoting the Release row's redirect to Repo setup. What two of them still
called a guess is whether "new integration repo" means one that has never released, which is
the request's own wording and not a choice between rows.

## Findings not planted by the scenario

- **A matches two triage rows.** "Every entity went unavailable" also fits the Connection
  row; the quoted log line decided it for *Unexpected reply* in every rep, and both rows name
  `patterns.md`.
- **C has a decoy that held.** `ha-triage`'s Panel row and `ha-integration`'s Panel row both
  mention panels; every rep followed the Panel row's "how it looks is the Panel design row".
- **`ha-triage` was in the session's skill registry** this time, which the last run could not
  confirm.
