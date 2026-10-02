# 06 — Router selection, after the 2026.9 refresh

- **Date:** 2026-10-02
- **Skill state:** `feat/refresh-2026-9` from `5a89cae`, through five router wordings
- **Arm:** treatment, three reps per run (fresh read-only subagent, told only where the skills live)
- **Verdict:** FAIL on D at `5a89cae`; PASS 15/15 on the final wording, with D's answer key
  changed before that run (see the warning below)

The run row 224 asks for: the router was converted to the schema's mode table and
`ha-triage` became a router by fault class since the last run of this scenario.

## Run 1, at `5a89cae` — FAIL on D

A, B, C and E were answered as the key expects in all three reps, each from the row the key
names, opening no reference file. D landed on a file the key then accepted, `github-setup.md`,
but every rep called it a guess between the Release row ("cutting or gating a release") and
Repo setup ("first release"). The scenario counts an answer the router did not decide as a
routing failure, so D fails.

The run's real finding was in the content, not the table. After a new repository's first
commit come two stages, the GitHub setup and the first release; `scaffold.md`, the file for a
new repository, stopped before both, and `github-setup.md` never points on to the release.

## Three wordings that did not fix it

| Run | Wording | D in three reps |
|---|---|---|
| 2 | Release and Repo setup split on whether the repository has released | `github-setup.md` each time, quoting the split; each rep still called it a guess, on whether "new" meant never released. The review then found the split sent a whole first release to `github-setup.md`, which has no step for cutting one, and that the new cell named a state rather than an action. Reverted |
| 3 | a clause on the Release row, "a repository's first release comes after Repo setup" | `github-setup.md` each time, and each rep called it a guess among Release, Repo setup and Workflow. Reverted |
| 4 | the fix below, before the Scaffold row named a repository that has not released yet | `versioning.md` each time, a guess: every rep read "my new integration repo" as one that already exists, which the Scaffold row then excluded |

## The fix

`scaffold.md` now runs through the first release: Step 9 is every step of `github-setup.md`,
after the first push, and Step 10 is *Cutting a release* in `versioning.md`. Its scope admits
a repository that has not released yet, from the first step it lacks. The Scaffold row claims
a new repository, or setting up one that has not released yet; the Release and Repo setup rows
are back to their own work, with "first release" gone from Repo setup.

## Run 5, on `0ad281a`'s router — PASS 15/15

The router the reps read is `SKILL.md` as `0ad281a` left it, which no later commit changes.
`scaffold.md`'s own text changed after the run — Step 9 widened from two headings of
`github-setup.md` to every step of it, Step 10 lost a precondition, and the scope gained the
unreleased repository — but no rep opened a reference file, so none of that was read.

| Request | Expected | Answered, all three reps | By |
|---|---|---|---|
| A firmware log line | `ha-triage` → `ha-integration/reference/patterns.md` | same | the *Unexpected reply* row; `ha-integration`'s description disclaims fault triage |
| B reconfigure flow | `ha-integration` → `patterns.md` | same | the Modify row |
| C panel dark mode | `ha-integration` → `panel-design.md` | same | the Panel design row |
| D release process, new repo | `ha-integration` → `scaffold.md`, or `versioning.md` if the repository has released | `scaffold.md` | the Scaffold row's "setting up a repository that has not released yet" |
| E setup-entry test | `ha-integration` → `testing.md` | same | the Test row |

**Reference files opened to decide: zero**, in every rep of every run. Each rep of run 5 noted
that D turns on whether "new" means unreleased, which the request does not say; each reading
has a row, and the key accepts both.

## ⚠️ The key was edited before run 5

D's expected answer moved from `github-setup.md` to `scaffold.md` in the same change that made
`scaffold.md` carry the sequence. That is the right key for the skill as it now stands, but a
test whose answer moves with the change proves less than one that did not. Its acceptance of
`versioning.md` for an already-released reading was added after the run; no rep answered it,
so it changed no verdict.

## Findings not planted by the scenario

- **A matches two triage rows.** Most reps noted that "every entity went unavailable" also
  fits the Connection row; every rep decided it for *Unexpected reply* on the quoted log line,
  and both rows name `patterns.md`.
- **C has a decoy that held.** Several reps noted that `ha-triage`'s Panel row and
  `ha-integration`'s Panel row both mention panels; every rep routed C to `panel-design.md`.
