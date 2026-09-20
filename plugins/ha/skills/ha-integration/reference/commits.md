# Commit conventions

Read this when writing a commit subject, a PR title or a PR body. Labels, gates and the
release model are `reference/versioning.md`.

**The commit subject is the changelog entry: one tight imperative in the Conventional
Commits form, subject-only by default.**

## Contents

1. Commit subjects
2. Step 1: Install the `commit-msg` hook
3. Step 2: Write the subject in the Conventional Commits form
4. Step 3: Stop at the subject
5. Step 4: Carry no AI-attribution trailer
6. The PR body — for reviewers, and nothing users read
7. Step 1: Leave the body empty
8. Step 2: Put the narrative in the release description
9. Step 3: Put the reasoning in the PR conversation
10. Red flags — stop
11. Cases
12. `gh pr edit` fails on the Projects-classic deprecation — PR body Step 1

## Commit subjects

### Step 1: Install the `commit-msg` hook

Copy release-flow's `.githooks/commit-msg`, whose purpose *Called versus copied* in its
README gives, to `.githooks/commit-msg` and `chmod +x`. Tell contributors in `CLAUDE.md` to
enable it once per clone:

```bash
git config core.hooksPath .githooks
```

It is stricter than this file, and the hook itself is the list of what it rejects — read it
rather than assuming these conventions are the whole of it. Don't retype it from this
document.

### Step 2: Write the subject in the Conventional Commits form

```
<type>[(<scope>)][!]: <description>
```

- A PR title carries one of the types release-flow's `lint-pr.yml` accepts — the list is in
  that workflow; why `revert:` is not among them, and what the draft opener does with a
  `revert:` commit, is `lint-pr.yml` under *The five workflows* in its README.
- A scope is tolerated and never generated.
- **`!` is the only breaking marker**; why is *Called versus copied* in release-flow's
  README.
- Imperative mood, lowercase after the colon, no trailing period.

### Step 3: Stop at the subject

- **Subject-only by default.**
- Add a body ONLY when the *why* is non-obvious, or for migration notes — never to restate
  what the diff already shows.

### Step 4: Carry no AI-attribution trailer

- No `Co-Authored-By: Claude`, no tool or session link, no "generated with…" line.
- A harness that injects such trailers by default: strip them.

> **Note:** a `Co-Authored-By:` for a *real* human collaborator is fine.

## The PR body — for reviewers, and nothing users read

**Release notes are generated from commit subjects, never from PR bodies.** How the body is
built, grouped by the type of each commit, and why not from release-drafter's own
PR-per-label output, is `release-drafter.yml` under *The five workflows* in release-flow's
README.

### Step 1: Leave the body empty

No job writes it, and the draft PR arrives empty.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| "this change is complex, it needs explaining" | split it, or write better commit subjects | the subjects are the changelog | commit Step 2 |
| "reviewers need the reasoning" | put it in the PR conversation | what users get is the commit subjects | PR body Step 3 |
| "the verification belongs with the change" | put it in a comment | a description is not a lab notebook | PR body Step 3 |
| "I wrapped it in `<details>` so it's stripped" | leave the fold to Dependabot's own output | the fold is not a licence to write an essay | PR body Step 1 |
| "it's only a few paragraphs" | leave the body empty | whatever its length it is published under the repo owner's byline | PR body Step 1 |

### Step 2: Put the narrative in the release description

The human-readable "what changed and why it matters" belongs in the **release notes**,
written once, in the release description. GitHub's own `generate_release_notes` is not the
mechanism here; the one-writer rule the audit enforces is *What the audit checks now* in
ha-integration-ci's README.

### Step 3: Put the reasoning in the PR conversation

Reasoning, alternatives and verification evidence go in the PR **conversation**, where
reviewers read them and the notes do not.

### Red flags — stop

| scenario | choice |
|---|---|
| typing prose into `gh pr create --body` | put it in a comment, or fix the commit subjects |
| reaching for `<details>` in a PR description | put it in a comment, or fix the commit subjects |
| a description longer than its diff | put it in a comment, or fix the commit subjects |
| explaining *why* anywhere the commit subjects should have said it | fix the commit subjects |

## Cases

### `gh pr edit` fails on the Projects-classic deprecation — PR body Step 1

**Fix:** set the title and body through the API instead.

```bash
gh api -X PATCH repos/{o}/{r}/pulls/{n} -f title=… -F body=@file
```
