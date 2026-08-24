# Commit, PR and merge discipline

The rules that decide what ships and what a release says. SKILL.md carries the one-line versions; the reasoning is here.

## PR discipline — the commit subjects are the changelog

<!-- the opener itself is described in reference/github-actions.md -->

**The release notes are built from the commits, not from the PR body.** `scripts/release_notes.py` classifies each subject and groups it, and the draft PR arrives with an empty body (see `reference/github-actions.md`). So a body is optional context for reviewers, and writing the changelog into it just says the same thing twice, in a place users never read.

Reasoning, alternatives, verification evidence: those go in the PR **conversation**, where reviewers read them and the notes do not.

| Excuse | Reality |
|---|---|
| "This change is complex, it needs explaining" | Then it needs splitting, or better commit subjects. The subjects are the changelog. |
| "Reviewers need the reasoning" | Reviewers read the conversation. What users get is the commit subjects, so put the change in those. |
| "The verification belongs with the change" | It belongs in a comment. A description is not a lab notebook. |
| "I wrapped it in `<details>` so it's stripped" | The fold is for Dependabot's own output, not a licence to write an essay. |
| "It's only a few paragraphs" | Measured across eight PRs it was 2,728 words, all republished under the repo owner's byline. |

## Red flags — stop

- Typing prose into `gh pr create --body`
- Reaching for `<details>` in a PR description
- A description longer than its diff is interesting
- Explaining *why* anywhere the commit subjects should have said it

**All of these mean: put it in a comment, or fix the commit subjects.**

> **Observed.** This rule already existed, as "keep two or three sentences of summary at the top of the PR body". It was read and ignored across eight consecutive PRs in this skill's own repo. The author was unaware until they read one of their own PRs. Guidance that exists and is skipped needs a prohibition, not a clearer sentence.

---

## Merge discipline — never merge a red check

**A failing check is the gate working. Merging past it is not a judgement call.**

Violating the letter of this rule is violating the spirit of it. The gate stack in this skill exists to stop bad merges; an agent that reasons its way past a red check has removed the only thing standing between a mistake and `main`.

**One exception, and it is narrow.** A `pull_request_target` workflow loads its definition from the **base** branch, so a PR fixing that workflow is always checked by the broken copy and can never go green on its own. That is the only sanctioned case. It covers **one job, on one PR, whose own definition the PR changes**. To use it you must first prove it with a diff (`git show origin/main:.github/workflows/pr-checks.yml` against the branch's), say in the PR that the failure is the bug being fixed, and verify on the next PR.

| Excuse | Reality |
|---|---|
| "I understand why it's red" | Understanding a failure is a reason to fix it, not to merge it. |
| "The content is correct, only the check is wrong" | Then fix the check. A wrong check is a defect, not an exemption. |
| "It's the `pull_request_target` self-validation case" | Prove it with the diff, on that job, on that PR. If you did not check, it is not that case. |
| "I merged past a red check earlier for a good reason" | That merge carried its own proof. This one needs its own. Precedent is not evidence. |
| "The version/label/content is right anyway" | The gate said otherwise. It is reporting what it can see; if it is wrong about that, say why in writing before merging. |
| "It's only advisory, GitHub let me" | Advisory is a repo-configuration accident, not permission. See *Make the checks REQUIRED*. |
| "Re-running it would waste minutes" | Minutes against a bad merge on `main`. |

## Red flags — stop

- About to run `gh pr merge` while any check is red
- Diagnosing a failure **after** merging rather than before
- Reusing a previous exception without re-deriving why it applies
- Reaching for `--admin`, `--force`, or a `bypass_actors` entry to get a merge through
- Telling yourself the failure is "unrelated" without having read the log

**All of these mean: stop, read the log, fix or explain in writing first.** Which checks are required, and why one of them is deliberately absent, is `reference/github-setup.md`.

> **Observed.** This rule exists because it was broken in this skill's own repo. The `pull_request_target` exception was written, then reused a few hours later on a PR it did not cover: the version gate had correctly failed because the PR carried no label, and the merge went through with the failure undiagnosed. Two conditions made it silent — an allow-rule of `Bash(gh pr *)` pre-approving `gh pr merge`, and no required checks on the branch (listed in `reference/github-setup.md`).

---

## Debugging discipline

- **Trace before naming a cause** — grep the path (publish → subscribe → handler), confirm in code; a pre-trace hunch is a guess, not the diagnosis.
- **Multi-entry service fan-out:** a `hass.services.async_call(DOMAIN, svc, …)` with no target loops **all** config entries. An entity action that should hit only its own device must pass its own `entry_id`/`device_id` and the handler must filter — default to "all" only for a deliberate bulk call.

---
