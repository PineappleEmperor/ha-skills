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

What the grant allows:

- `Contents: write` covers creating releases, tags and commits in the repos it is scoped
  to.
- `Pull requests: write` lets it open the draft PR — and, unavoidably, merge one, since
  GitHub does not separate those.
- Neither permission can edit rulesets or branch protection, change repository settings, or
  reach any repo outside its scope, so a required-checks ruleset still holds.

### Step 2: Store it as the `RELEASE_TOKEN` repository secret

Repo → **Settings** → **Secrets and variables** → **Actions** → **Secrets** tab → **New
repository secret** → Name `RELEASE_TOKEN`, paste into **Secret** → **Add secret**

### Step 3: Rotate by pasting a new value into the same secret

Nothing else changes.

## Make the checks required — a workflow is not a gate until it can block a merge

**GitHub will let a PR merge with every workflow red, so until a ruleset requires them the
stack is decorative.**

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

| artefact | taken from |
|---|---|
| `pr / CC labelling` | the `pr` caller job |
| `pr / CC label validation` | the `pr` caller job |
| `lint / CC title validation` | the `lint` caller job |
| `validate / Ruff, Pyright and Pytest` | the `validate` caller job |
| `audit / ha-integration conformance check` | the `audit` caller job — `quality-audit.yml` |
| `HACS validation` | a plain workflow, unprefixed |
| `Hassfest manifest validation` | a plain workflow, unprefixed |
| `Dependency review` | `dependency-review.yml`, unprefixed |

The five with a prefix are named by GitHub's rule for called workflows, *Check names* in
release-flow's README, which also says why the three label checks are not redundant.

- Everything else the stack produces — the process-automation contexts listed under *Check
  names* in release-flow's README and *Calling the workflows* in ha-integration-ci's — fires
  on pushes and releases, and requiring one blocks every PR on a context that never reports.
- **A context the repo does not produce blocks every PR permanently.** Each of the eight
  comes from a workflow the audit requires (*What the audit checks now* in
  ha-integration-ci's README), so in a conforming repo the fix is to add the missing
  workflow, never to drop the context.
- **Dropping a context is only for a repo that has deliberately left the canonical set** —
  no `quality-audit.yml`, no `dependency-review.yml`. Drop the matching context, or PRs wait
  forever for a check that never runs.
- **A path-filtered workflow blocks every PR permanently.** `panel / Panel type-check and
  tests` is absent from the shipped ruleset for the reason ha-panel-ci's README gives: it
  never reports on a Python-only PR. Do not require it.
- A skipped job satisfies a required check, so job-level `if:` guards are fine; a cancelled
  run does not (release-flow's README, *Calling the workflows*, on the `pr-checks` trigger
  types).
- Never assume a context equals the job name: a matrix suffixes it (ha-integration-ci's
  README, *Implementation notes*).

## Supply chain

- `dependency-review.yml` and `issue_stale.yml` are two of the four plain workflows
  described in `reference/github-actions.md`.
- How a consumer pins a release of a CI repository, and why, is *The version model* in
  ha-integration-ci's README.
- What the audit requires of every `uses:` line in the scaffold, callers and steps alike,
  and the two refs it exempts, is *What the audit checks now* there.
- What that mutability costs, and how it is capped, is `reference/freshness.md`.
- How Dependabot maintains the pins is `reference/dependabot.md`.

## Cases

### The opener fails with `Resource not accessible by personal access token` — token Step 1

**Symptom:** the draft-PR opener fails with `Resource not accessible by personal access
token (repository.pullRequests)`.

**Fix:** the token is missing `Pull requests: write`; regenerate it with `Pull requests:
Read and write`.

### `Dependency review` is red on every PR — checks Step 3

**Symptom:** with the dependency graph off the action does not skip — it fails, so the
check is red on every PR forever.

**Fix:** enable it at Settings → Advanced Security. `bootstrap_repo.sh` enables it, and says
so loudly if it cannot.

### A ruleset must be overruled — checks Step 1

A ruleset granting admins `bypass_mode: always` does not constrain anyone holding admin; the
push reports `Bypassed rule violations` and proceeds, so the list stays empty.

**Fix:** disable the ruleset, merge, and re-enable it — deliberate, reversible, and it
leaves an audit-log entry. *Merge discipline* in `reference/discipline.md` gives exactly one
sanctioned reason, proven by diff.

### An AI session runs with your `gh` credentials — checks Step 1

An agent merges exactly as you do, and bypass entries are evaluated by actor, so any bypass
you hold it inherits. Two things make that silent: a broad allow-rule such as
`Bash(gh pr *)` pre-approves `gh pr merge` with no prompt, and an agent with admin can lift
any rule it can see.

**Fix:** narrow the allow-rule to read-only verbs (`gh pr view`, `gh pr list`), and give the
agent a credential without **Administration** if it should not edit rulesets or force-push.
