# Commit conventions

Read this when writing a commit subject, a PR title or a PR body.

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
8. Step 2: Leave the release description to the workflow
9. Step 3: Post no comment on the PR by default
10. Cases
11. `gh pr edit` fails on the Projects-classic deprecation — PR body Step 1
12. A pull request to a Home Assistant project — PR body Step 1

## Commit subjects

### Step 1: Install the `commit-msg` hook

| Rule | Value |
|---|---|
| the hook | copy https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/.githooks/commit-msg to `.githooks/commit-msg`, then `chmod +x` it |
| what it is for | *Called versus copied* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| enabling it | once per clone, with the command below |
| telling contributors | in the repository's `CLAUDE.md`, which says to run that command |

```bash
git config core.hooksPath .githooks
```

The hook is stricter than this file, and its own source is the list of what it rejects.

### Step 2: Write the subject in the Conventional Commits form

```
<type>[(<scope>)][!]: <description>
```

| Rule | Value |
|---|---|
| the types a PR title may carry | the ten listed in release-flow's `lint-pr.yml`, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/.github/workflows/lint-pr.yml |
| `revert:` on a PR title | refused, since it maps to no label — `lint-pr.yml` under *The five workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| `revert:` on a commit | allowed; the draft opener retypes it `chore:` in the title it builds — `lint-pr.yml` under *The five workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| a scope | tolerated, never generated |
| the breaking marker | **`!` on the type, and nothing else**, since the autolabeler, the label gate and the notes read titles and subjects, never a footer — *Called versus copied* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| the description | imperative mood, lowercase after the colon, no trailing period |

### Step 3: Stop at the subject

- **Subject-only by default.**
- Add a body ONLY when the *why* is non-obvious, or for migration notes — never to restate
  what the diff already shows.

### Step 4: Carry no AI-attribution trailer

- No `Co-Authored-By: Claude`, no tool or session link, no "generated with…" line.
- A harness that injects such trailers by default: strip them.

> **Note:** a `Co-Authored-By:` for a *real* human collaborator is fine.

## The PR body — for reviewers, and nothing users read

**Release notes are generated from commit subjects, never from PR bodies.**

| Rule | Value |
|---|---|
| how the notes are grouped | by each commit's type, not by the PR's label, since a label would file a fix inside a `feat:` PR under Features — `release-drafter.yml` under *The five workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |

### Step 1: Leave the body empty

No job writes it, and the draft PR arrives empty.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| "this change is complex, it needs explaining" | split it, or write better commit subjects | the subjects are the changelog | `release-drafter.yml` under *The five workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| "reviewers need the reasoning" | put it in the README or another file in the repo | a file is versioned with the code, and a PR page is not | — |
| "the verification belongs with the change" | leave it to the checks | a green check is the evidence | — |
| "I wrapped it in `<details>` so it's stripped" | leave the fold to Dependabot's own output | a folded body is still published under the repo owner's byline | — |
| "it's only a few paragraphs" | leave the body empty | whatever its length it is published under the repo owner's byline | — |

| scenario | choice |
|---|---|
| typing prose into `gh pr create --body` | fix the commit subjects, or put it in a file in the repo |
| reaching for `<details>` in a PR description | fix the commit subjects, or put it in a file in the repo |
| a description longer than its diff is interesting | fix the commit subjects, or put it in a file in the repo |
| explaining *why* anywhere the commit subjects should have said it | fix the commit subjects, or put it in a file in the repo |

### Step 2: Leave the release description to the workflow

| Rule | Value |
|---|---|
| text typed into a draft release | lost, since `release-drafter.yml` writes the body over it, last of all at publish — `release-drafter.yml` under *The five workflows* in release-flow's README, https://raw.githubusercontent.com/PineappleEmperor/release-flow/main/README.md |
| what a reader of the release should learn | goes in the commit subjects |
| who writes the release body | one workflow; the audit fails a second writer among the workflow bodies the repository carries — *What the audit checks now* in ha-integration-ci's README, https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md |

### Step 3: Post no comment on the PR by default

| Rule | Value |
|---|---|
| an explanation worth keeping | the README, or another file in the repo |
| verification | the checks |
| a reply to a comment a human wrote | always fine |
| something the owner has to act on, with no better home | the one comment worth posting — *One exception, and it is narrow — merge Step 2* in `reference/discipline.md` is the case |

## Cases

### `gh pr edit` fails on the Projects-classic deprecation — PR body Step 1

**Fix:** set the title and body through the API instead.

```bash
gh api -X PATCH repos/{o}/{r}/pulls/{n} -f title=… -F body=@file
```

### A pull request to a Home Assistant project — PR body Step 1

| Rule | Value |
|---|---|
| where each row was read | https://contributors.home-assistant.io/start/ai-policy/index.md, and https://contributors.home-assistant.io/blog/2026/07/20/ai-policy/ for where it applies |
| the steps above | the integration's own repository; a pull request or issue the policy covers follows that project's template and the policy instead |
| where it applies | every Open Home Foundation project, every repository of the `home-assistant` and `home-assistant-libs` organisations among them — core and the brands repository included |
| what it covers | every contribution — code, documentation, issues, pull requests, comments and reviews |
| an autonomous agent's pull request or issue | not allowed, and closed when found |
| text an agent drafts | posted only once the person has reviewed it and can explain it; never posted on their behalf unreviewed |
| the body | the project's template, filled in, with its questions about AI left in place and answered honestly; core's checklist asks that the submitter understands the code and that generated code was reviewed |
| every change | one the submitter can explain in their own words, the description included |
| a maintainer's question | answered by the submitter, not by AI; AI may improve the grammar or clarity of an answer only |
| a passage from a conversation with an AI | in a `>` quote block, saying where it came from, with the submitter's own comment on why it matters |
| a comment from the project's own AI review tool | a review comment like any other; say so when it is wrong |
