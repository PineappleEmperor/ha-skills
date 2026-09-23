# Commit, PR and merge discipline

Read this when a check is red, or before naming a root cause. Commit and PR-body format is
`reference/commits.md`.

**A failing check is the gate working. Merging past it is not a judgement call.**

## Contents

1. Merge discipline — never merge a red check
2. Step 1: Stop and read the log
3. Step 2: Fix it, or say in writing why the gate is wrong
4. Debugging discipline
5. Step 1: Trace the path
6. Step 2: Name the cause
7. Cases
8. One exception, and it is narrow — merge Step 2
9. An action hits more devices than it should — debugging Step 2

## Merge discipline — never merge a red check

### Step 1: Stop and read the log

Before anything else, and before the merge — not after it.

### Step 2: Fix it, or say in writing why the gate is wrong

Fix the failure, or write down why the gate is wrong about what it can see; either way,
before merging.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| merging on "I understand why it's red" | fix it | understanding a failure is a reason to fix it, not to merge it | Step 2 |
| merging on "the content is correct, only the check is wrong" | fix the check | a wrong check is a defect, not an exemption | Step 2 |
| merging on "it's the `pull_request_target` self-validation case" | prove it with the diff, on that job, on that PR | if you did not check, it is not that case | *One exception, and it is narrow — merge Step 2* |
| merging on "I merged past a red check earlier for a good reason" | carry this merge's own proof | the earlier exception was proved on its own diff, which says nothing about this one | *One exception, and it is narrow — merge Step 2* |
| merging on "the version/label/content is right anyway" | say in writing why the gate is wrong, before merging | the gate is reporting what it can see | Step 2 |
| merging on "it's only advisory, GitHub let me" | read the log | advisory means GitHub will not stop you, not that the check is wrong | `reference/github-setup.md` |
| merging on "re-running it would waste minutes" | re-run it | a flake and a real failure look identical until the second run | Step 1 |

| scenario | choice |
|---|---|
| about to run `gh pr merge` while any check is red | stop, and read the log |
| diagnosing a failure **after** merging rather than before | diagnose first, merge after |
| reusing a previous exception without re-deriving why it applies | re-derive the diff before claiming it |
| reaching for `--admin`, `--force`, or a `bypass_actors` entry to get a merge through | fix the check |
| telling yourself the failure is "unrelated" without having read the log | read the log |

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
`pr-checks.yml` under *The five workflows* in release-flow's README. That is the only
sanctioned case, and it covers **one job, on one PR, whose own definition the PR changes**.

**Fix:** prove it with `git show origin/main:.github/workflows/pr-checks.yml` against the
branch's copy, then say in the PR that the failure is the bug being fixed.

**Timing:** re-derive that diff every time before claiming the exception, and verify on the
next PR, where the fixed caller runs as `main`'s.

### An action hits more devices than it should — debugging Step 2

**Fix:** suspect the fan-out first — the service-call shape that causes it is in
`reference/patterns.md`.
