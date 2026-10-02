# 06 — Router selection, after the 2026.9 refresh

- **Date:** 2026-10-02
- **Skill state:** `feat/refresh-2026-9` from `5a89cae`, through four router wordings
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

The run's real finding was in the content, not the table: a new repository needs three files
in order — the GitHub setup, the workflows, the release — and `scaffold.md`, the file for a new
repository, stopped before the first two of those that happen after the first commit, while
`github-setup.md` never points on to the release.

## Two wordings that did not fix it

- Splitting Release and Repo setup on whether the repository had released sent a new
  repository's whole release to `github-setup.md`, which has no step for cutting one. The
  review found that, and that the new cell named a state rather than an action. Reverted.
- A clause on the Release row, "a repository's first release comes after Repo setup", still
  left D a guess in all three reps. Reverted.

## The fix

`scaffold.md` now runs through the first release: Step 9 sets the repository up on GitHub and
Step 10 cuts the first release, each pointing at the owning heading. The Scaffold row claims a
new repository, and setting up one that has not released yet, through its first release; the
Release and Repo setup rows are back to their own work, with "first release" gone from Repo
setup. One intermediate run, before "not released yet" was in the Scaffold row, had all three
reps read "my new integration repo" as one that already exists and guess `versioning.md`.

## Run 4, on the final wording — PASS 15/15

| Request | Expected | Answered, all three reps | By |
|---|---|---|---|
| A firmware log line | `ha-triage` → `ha-integration/reference/patterns.md` | same | the *Unexpected reply* row; `ha-integration`'s description disclaims fault triage |
| B reconfigure flow | `ha-integration` → `patterns.md` | same | the Modify row |
| C panel dark mode | `ha-integration` → `panel-design.md` | same | the Panel design row |
| D release process, new repo | `ha-integration` → `scaffold.md` | same | the Scaffold row's "setting up a repository that has not released yet" |
| E setup-entry test | `ha-integration` → `testing.md` | same | the Test row |

**Reference files opened to decide: zero**, in every rep. Each rep still noted that D turns
on whether "new" means unreleased, which the request does not say; the rows now decide either
reading, so that is the request's ambiguity and not the router's.

## ⚠️ The key was edited before run 4

D's expected answer moved from `github-setup.md` to `scaffold.md` in the same change that made
`scaffold.md` carry the sequence. That is the right key for the skill as it now stands, but a
test whose answer moves with the change proves less than one that did not.

## Findings not planted by the scenario

- **A matches two triage rows.** "Every entity went unavailable" also fits the Connection
  row; the quoted log line decided it for *Unexpected reply* in every rep, and both rows name
  `patterns.md`.
- **C has a decoy that held.** `ha-triage`'s Panel row and `ha-integration`'s Panel row both
  mention panels; every rep followed the Panel row's "how it looks is the Panel design row".
