# Setting the repository up on GitHub

Read this when configuring a repo on GitHub: the release token, the required checks, the
dependency graph and the supply-chain guards. What the scaffold carries, and what may be
changed in a copy, is `reference/github-actions.md`.

**Every item here is a setting no file in the repo can carry, and each one fails quietly
until the first CI run.**

## Contents

1. `RELEASE_TOKEN` — set this up before the first release
2. Step 1: Generate a fine-grained PAT
3. Step 2: Store it as the `RELEASE_TOKEN` repository secret
4. Step 3: Rotate by pasting a new value into the same secret
5. Make the checks required — a workflow is not a gate until it can block a merge
6. Step 1: Copy `templates/ruleset.json` to the repo root
7. Step 2: Apply the ruleset once, or run `scripts/bootstrap_repo.sh`
8. Step 3: The eight required contexts, and what must never be required
9. Supply chain
10. Cases
11. The opener fails with `Resource not accessible by personal access token` — token Step 1
12. `Dependency review` is red on every PR — checks Step 3
13. A ruleset must be overruled — checks Step 1
14. An AI session runs with your `gh` credentials — checks Step 1

## `RELEASE_TOKEN` — set this up before the first release

One secret, once per repo, passed by the `auto-draft-pr.yml` caller to release-flow's
draft-PR opener. Why the opener needs a token of its own, and what happens without one, is
*The one secret* in release-flow's README. The audit checks the secret is set
(ha-integration-ci's README, *What the audit checks now*).

- The release path needs no token.
- A GitHub App cannot stand in for it; *The one secret* in release-flow's README says why.

### Step 1: Generate a fine-grained PAT

1. github.com → Settings → Developer settings → Personal access tokens →
   **Fine-grained tokens** → **Generate new token**
2. **Resource owner**: your account · **Repository access**: Only select repositories →
   this repo
3. **Repository permissions**: `Contents: Read and write` and `Pull requests: Read and
   write` — nothing else. (`Metadata: Read` is added automatically and cannot be removed.)
4. **Expiration**: 90 days or less
5. **Generate token**, copy the `github_pat_…` value — it is shown once

**What the grant allows:**

- `Contents: write` covers creating releases, tags and commits in the repos it is scoped
  to.
- `Pull requests: write` lets it open the draft PR — and, unavoidably, merge one, since
  GitHub does not separate those.
- Neither permission can edit rulesets or branch protection, change repository settings, or
  reach any repo outside its scope, so a required-checks ruleset still holds.
- The token exists to trigger workflows, so anything it can do a workflow it starts can do
  too.

### Step 2: Store it as the `RELEASE_TOKEN` repository secret

Repo → **Settings** → **Secrets and variables** → **Actions** → **Secrets** tab → **New
repository secret** → Name `RELEASE_TOKEN`, paste into **Secret** → **Add secret**

### Step 3: Rotate by pasting a new value into the same secret

Nothing else changes.

## Make the checks required — a workflow is not a gate until it can block a merge

**GitHub lets a PR merge with every workflow red until a ruleset requires the contexts.**

### Step 1: Copy `templates/ruleset.json` to the repo root

It requires the eight contexts the scaffold's workflows produce, and keeps deletions and
force-pushes blocked. Whether the audit sees the ruleset, and what it reports when it
cannot ask GitHub, is *What the audit checks now* in ha-integration-ci's README.

### Step 2: Apply the ruleset once, or run `scripts/bootstrap_repo.sh`

```bash
gh api -X POST repos/<owner>/<repo>/rulesets --input ruleset.json
```

`scripts/bootstrap_repo.sh` does the GitHub-side settings in one run, from the repo root
after the first push: description, topics, issues, the dependency graph, `core.hooksPath`,
the ruleset (only if `ruleset.json` is at the repo root — it skips otherwise), and the
`RELEASE_TOKEN` secret, prompted rather than passed as an argument.

```bash
bash scripts/bootstrap_repo.sh "One-line description of the integration"
```

### Step 3: The eight required contexts, and what must never be required

A *check* runs on a pull request and can be required, so a red one blocks the merge. The
eight in `ruleset.json`:

- `pr / CC labelling`
- `pr / CC label validation`
- `lint / CC title validation`
- `validate / Ruff, Pyright and Pytest`
- `audit / ha-integration conformance check`
- `HACS validation`
- `Hassfest manifest validation`
- `Dependency review`

The five carrying a `<caller job id> / ` prefix are named by GitHub's rule for called
workflows, *Check names* in release-flow's README, which also says why the three label
checks are not redundant. The last three are plain workflows, so GitHub names them after the
job itself; `Dependency review` is `dependency-review.yml`'s.

| Rule | Value |
|---|---|
| a process-automation context — the ones *Check names* in release-flow's README and *Calling the workflows* in ha-integration-ci's list | never required: it fires on a push or a release, so a PR waits on a context that never reports |
| a context the repo does not produce | blocks every PR permanently: in a conforming repo, add the workflow *What the audit checks now* in ha-integration-ci's README requires rather than drop the context |
| dropping a context | required, not merely permitted, where the repo has deliberately left the canonical set — no `quality-audit.yml`, no `dependency-review.yml` — since the PR otherwise waits for a check that never runs |
| `panel / Panel type-check and tests` | never required: it is path-filtered, so it does not report on a Python-only PR |
| a skipped job | satisfies its required check, so a job-level `if:` guard is fine |
| a cancelled run | does not, per *Calling the workflows* in release-flow's README on the `pr-checks` trigger types |
| a matrix job's context | suffixed with the matrix value, so it is not the job name — *Implementation notes* in ha-integration-ci's README |

## Supply chain

| file | when to read |
|---|---|
| `reference/github-actions.md` | placing `dependency-review.yml` and `issue_stale.yml`, which are two of the four plain workflows it describes |
| *The version model* in ha-integration-ci's README | pinning a release of a CI repository |
| *What the audit checks now* in ha-integration-ci's README | checking a `uses:` line, in a caller or a step, and the two refs the audit exempts |
| `reference/freshness.md` | asking what those two mutable refs cost and how the cost is capped |
| `reference/dependabot.md` | asking what keeps the pins moving |

## Cases

### The opener fails with `Resource not accessible by personal access token` — token Step 1

**Symptom:** the draft-PR opener fails with `Resource not accessible by personal access
token (repository.pullRequests)`.

**Fix:** the token is missing `Pull requests: write`; regenerate it with `Pull requests:
Read and write`.

### `Dependency review` is red on every PR — checks Step 3

**Symptom:** with the dependency graph off the action does not skip — it fails, so the
check is red on every PR forever.

**Fix:** enable it at Settings → Advanced Security, or run `bootstrap_repo.sh`, which
enables it and reports when it cannot.

### A ruleset must be overruled — checks Step 1

A ruleset granting admins `bypass_mode: always` does not constrain anyone holding admin; the
push reports `Bypassed rule violations` and proceeds, so the list stays empty.

**Fix:** disable the ruleset, merge, re-enable it, which is deliberate, reversible and
leaves an audit-log entry. The one sanctioned reason to merge red is *Merge discipline — never merge a red
check* in `reference/discipline.md`.

### An AI session runs with your `gh` credentials — checks Step 1

An agent merges exactly as you do, and bypass entries are evaluated by actor, so any bypass
you hold it inherits. Two things make that silent: a broad allow-rule such as
`Bash(gh pr *)` pre-approves `gh pr merge` with no prompt, and an agent with admin can lift
any rule it can see.

**Fix:** narrow the allow-rule to read-only verbs (`gh pr view`, `gh pr list`), and give the
agent a credential without **Administration** if it should not edit rulesets or force-push.
