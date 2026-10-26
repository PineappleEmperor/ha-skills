# Commit, PR and merge discipline

Read this when a check is red, a merge is about to happen, or before naming a root cause.

**A failing check is the gate working. Merging past it is not a judgement call.**

## Contents

1. Merge discipline — never merge a red check
2. Step 1: Stop and read the log
3. Step 2: Fix it, or say in writing why the gate is wrong
4. Step 3: Tell the user it is ready to merge
5. Debugging discipline
6. Step 1: Trace the path
7. Step 2: Name the cause
8. Cases
9. One exception, and it is narrow — merge Step 2
10. An action hits more devices than it should — debugging Step 2

## Merge discipline — never merge a red check

### Step 1: Stop and read the log

Before anything else, and before the merge — not after it. On the gate path the run and its
failing step's log are a gate read — *Step 3: Read from GitHub* in
`reference/github-access.md`.

### Step 2: Fix it, or say in writing why the gate is wrong

Fix the failure, or write down why the gate is wrong about what it can see; either way,
before merging.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| merging on "I understand why it's red" | fix it | understanding a failure is a reason to fix it, not to merge it | — |
| merging on "the content is correct, only the check is wrong" | fix the check | a wrong check is a defect, not an exemption | — |
| merging on "it's the `pull_request_target` self-validation case" | prove it with the diff, on that job, on that PR | if you did not check, it is not that case | `pr-checks.yml` under *The five workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| merging on "I merged past a red check earlier for a good reason" | carry this merge's own proof | the earlier exception was proved on its own diff, which says nothing about this one | — |
| merging on "the version/label/content is right anyway" | say in writing why the gate is wrong, before merging | the gate is reporting what it can see | — |
| merging on "it's only advisory, GitHub let me" | read the log | advisory means GitHub will not stop you, not that the check is wrong | — |
| merging on "re-running it would waste minutes" | re-run it, or on the gate path ask the user to, as *Step 6: Write to GitHub* in `reference/github-access.md` says | a flake and a real failure look identical until the second run | — |

| scenario | choice |
|---|---|
| about to run `gh pr merge`, red check or green | stop — the merge is the user's, Step 3 |
| diagnosing a failure **after** merging rather than before | diagnose first; the merge after it is the user's, Step 3 |
| reusing a previous exception without re-deriving why it applies | re-derive the diff before claiming it |
| reaching for `--admin`, `--force`, or a `bypass_actors` entry to get a merge through | stop and read the log, then fix it or say in writing why the gate is wrong |
| telling yourself the failure is "unrelated" without having read the log | read the log |

### Step 3: Tell the user it is ready to merge

| Rule | Value |
|---|---|
| the merge | the user's, whatever the session's credential allows: say the PR is ready, or what still stands in its way, and stop there |
| an approval | the user's too: a session acting with the user's credential would approve its own work as them |
| ready | every required check green, or the exception *One exception, and it is narrow — merge Step 2* proved on this PR |

## Debugging discipline

**Name the cause only from a trace you have followed. A hunch that arrives first is a guess
wearing the diagnosis's clothes.**

### Step 1: Trace the path

Grep the path — publish → subscribe → handler — then confirm it in code.

### Step 2: Name the cause

Name it from the trace, and say which call in the trace produces the behaviour.

## Cases

### One exception, and it is narrow — merge Step 2

A PR fixing a `pull_request_target` caller can never go green on its own; why is
`pr-checks.yml` under *The five workflows* in release-flow's README,
https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md. That is the only
sanctioned case, and it covers **one job, on one PR, whose own definition the PR changes**.

**Fix:** prove it with `git show origin/main:.github/workflows/pr-checks.yml` against the
branch's copy, then say in the PR that the failure is the bug being fixed. On the gate path,
fetch first, *Step 4: Fetch* in `reference/github-access.md`, and post the comment as *Step 6:
Write to GitHub* in `reference/github-access.md` gives.

**Timing:** re-derive that diff every time before claiming the exception, and verify on the
next PR, where the fixed caller runs as `main`'s.

### An action hits more devices than it should — debugging Step 2

**Fix:** suspect the fan-out first — the "a call with no target" row of *Custom services —
Step 1* in `reference/patterns.md`.
