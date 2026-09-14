# Setting the repository up on GitHub

One-time setup that lives in GitHub's settings, not in the repo: the release token, the
required checks, the dependency graph and the supply-chain guards. Every item here is a
setting no file in the repo can carry, and each one fails quietly until the first CI run.
`scripts/bootstrap_repo.sh` does the settings side in one run.

What the scaffold carries, and what may be changed in a copy, is `reference/github-actions.md`.

- `RELEASE_TOKEN` — set this up before the first release
- What the grant allows
- Make the checks required — a workflow is not a gate until it can block a merge
- The eight required contexts, and what must never be required
- `Dependency review` needs the dependency graph enabled
- Bypass configuration
- For AI sessions
- Supply chain

## `RELEASE_TOKEN` — set this up before the first release

One secret, once per repo, passed by the `auto-draft-pr.yml` caller to release-flow's
draft-PR opener. Why the opener needs a token of its own, and what happens without one, is
*The one secret* in release-flow's README. The release path needs no token: publishing a
draft is a human action, so its events fire normally. The audit checks the secret is set
(ha-integration-ci's README, *What the audit checks now*).

A fine-grained PAT:

1. github.com → Settings → Developer settings → Personal access tokens →
   **Fine-grained tokens** → **Generate new token**
2. **Resource owner**: your account · **Repository access**: Only select repositories →
   this repo
3. **Repository permissions**: `Contents: Read and write` and `Pull requests: Read and
   write` — nothing else. (`Metadata: Read` is added automatically and cannot be removed.)
4. **Expiration**: 90 days or less
5. **Generate token**, copy the `github_pat_…` value — it is shown once
6. Repo → **Settings** → **Secrets and variables** → **Actions** → **Secrets** tab →
   **New repository secret** → Name `RELEASE_TOKEN`, paste into **Secret** → **Add secret**

A GitHub App cannot stand in for it; *The one secret* in release-flow's README says why.

### What the grant allows

`Contents: write` covers creating releases, tags and commits in the repos it is scoped to.
Adding `Pull requests: write` lets it open the draft PR — and, unavoidably, merge one, since
GitHub does not separate those. Neither permission can edit rulesets or branch protection,
change repository settings, or reach any repo outside its scope, so a required-checks ruleset
still holds.

Without `Pull requests: write`, the opener fails with
`Resource not accessible by personal access token (repository.pullRequests)`. That matters
because this token exists to *trigger* workflows — anything it can do, a workflow it starts
can do too.

**Rotating.** Paste a new value into the same secret; nothing else changes.

## Make the checks required — a workflow is not a gate until it can block a merge

GitHub will let a PR merge with every workflow red, so until a ruleset requires them the
stack is decorative. Copy `templates/ruleset.json` to the repo root and apply it once:

```bash
gh api -X POST repos/<owner>/<repo>/rulesets --input ruleset.json
```

It requires the eight contexts the scaffold's workflows produce, and keeps deletions and
force-pushes blocked. Whether the audit sees the ruleset, and what it reports when it
cannot ask GitHub, is *What the audit checks now* in ha-integration-ci's README.

**`scripts/bootstrap_repo.sh` does the GitHub-side settings in one run**, from the repo root
after the first push: description, topics, issues, the dependency graph, `core.hooksPath`, the ruleset (only
if `ruleset.json` is at the repo root — it skips otherwise), and the `RELEASE_TOKEN` secret,
prompted rather than passed as an argument.

```bash
bash scripts/bootstrap_repo.sh "One-line description of the integration"
```

### The eight required contexts, and what must never be required

A *check* runs on a pull request and can be required, so a red one blocks the merge. The
eight in `ruleset.json`: `pr / CC labelling`, `pr / CC label validation`,
`lint / CC title validation`, `validate / Ruff, Pyright and Pytest`,
`audit / ha-integration conformance check`, `HACS validation`,
`Hassfest manifest validation` and `Dependency review`. The five with a prefix are named
by GitHub's rule for called workflows, *Check names* in release-flow's README, which also
says why the three label checks are not redundant.

Everything else the stack produces — the process-automation contexts listed under *Check
names* in release-flow's README and *Calling the workflows* in ha-integration-ci's — fires
on pushes and releases.
Not a weaker check: not a check at all, and requiring one blocks every PR on a context that
never reports.

Two ways to get this wrong, both of which block every PR permanently:

- **A context the repo does not produce.** Each of the eight comes from a workflow the
  audit requires (*What the audit checks now* in ha-integration-ci's README) — so in a
  conforming repo the honest fix is to add the missing workflow, not to drop the context. Dropping is for a
  repo that has deliberately left the canonical set (no `quality-audit.yml`, no
  `dependency-review.yml`); drop the matching context or PRs wait forever for a check that
  never runs.
- **A path-filtered workflow.** `panel / Panel type-check and tests` is absent from the
  shipped ruleset for the reason ha-panel-ci's README gives: it never reports on a
  Python-only PR. Do not require it.

A skipped job satisfies a required check, so job-level `if:` guards are fine; a cancelled
run does not (release-flow's README, *Calling the workflows*, on the `pr-checks` trigger
types). Never assume a context equals the job name: a matrix suffixes it
(ha-integration-ci's README, *Implementation notes*).

### `Dependency review` needs the dependency graph enabled

Settings → Advanced Security. With it off the action does not skip — it fails, so the check
is red on every PR forever. Verified on a test repo: seven workflows green, this one red
alone. `bootstrap_repo.sh` enables it, and says so loudly if it cannot.

### Bypass configuration

A ruleset granting admins `bypass_mode: always` does not constrain anyone holding admin; the
push reports `Bypassed rule violations` and proceeds, so the list stays empty. If you must
overrule — and *Merge discipline* in `reference/discipline.md` gives exactly one sanctioned
reason, proven by diff — disable the ruleset, merge, and re-enable it. That is deliberate,
reversible, and leaves an audit-log entry.

### For AI sessions

An agent running with your `gh` credentials merges exactly as you do, and bypass entries are
evaluated by actor, so any bypass you hold it inherits. Two things make that silent: a broad
allow-rule such as `Bash(gh pr *)` pre-approves `gh pr merge` with no prompt, and an agent
with admin can lift any rule it can see. Narrow the allow-rule to read-only verbs
(`gh pr view`, `gh pr list`), and give the agent a credential without **Administration** if it
should not edit rulesets or force-push. A restriction the agent can lift is friction, not a
limit.

## Supply chain

`dependency-review.yml` and `issue_stale.yml` are two of the four plain workflows described
in `reference/github-actions.md`. How a consumer pins a release of a CI repository, and why,
is *The version model* in ha-integration-ci's README; what the audit requires of every
`uses:` line in the scaffold, callers and steps alike, and the two refs it exempts, is
*What the audit checks now* there; what that mutability costs, and how it is capped, is
`reference/freshness.md`. How Dependabot maintains the pins
is `reference/dependabot.md`.
