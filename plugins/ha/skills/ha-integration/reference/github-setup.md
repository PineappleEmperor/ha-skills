# Setting the repository up on GitHub

One-time setup that lives in GitHub's settings, not in the repo: the release token, the
required checks, the dependency graph and the supply-chain guards. Every item here is a
setting no file in the repo can carry, and each one fails quietly until the first CI run.
`scripts/bootstrap_repo.sh` does most of it in one command.

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
draft is a human action, so its events fire normally. `skill_audit.py` fails a repo that
carries the opener's caller with no `RELEASE_TOKEN` set.

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

A GitHub App cannot stand in for it yet: a caller is one job that only forwards secrets, so
the token would have to be minted inside release-flow's opener, which it does not do.

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
force-pushes blocked. `skill_audit.py` fails a repo whose default branch has no required
checks — **but only where it can ask GitHub.** With `gh` missing, unauthenticated, or holding
a token without `Administration: read`, that check and the `RELEASE_TOKEN` one downgrade to a
warning reading `NOT CHECKED, not passed`, and the audit still reports green overall. A clean
run in a sandbox or a token-limited CI is not evidence the ruleset exists; read the warnings.

**`scripts/bootstrap_repo.sh` does all of this once**, from the repo root after the first
push: description, topics, issues, the dependency graph, `core.hooksPath`, the ruleset (only
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

Everything else — `draft / Auto draft PR`, `release / Auto release zip`,
`release / Auto draft releases` — is process automation firing on pushes and releases. Not a
weaker check: not a check at all, and requiring one blocks every PR on a context that never
reports.

Two ways to get this wrong, both of which block every PR permanently:

- **A context the repo does not produce.** Each of the eight comes from a canonical
  workflow, and `skill_audit.py` fails a repo missing any of them — so in a conforming repo
  the honest fix is to add the missing workflow, not to drop the context. Dropping is for a
  repo that has deliberately left the canonical set (no `quality-audit.yml`, no
  `dependency-review.yml`); drop the matching context or PRs wait forever for a check that
  never runs.
- **A path-filtered workflow.** `panel / Panel type-check and tests` is absent from the
  shipped ruleset for the reason ha-panel-ci's README gives: it never reports on a
  Python-only PR. Do not require it.

A skipped job satisfies a required check, so job-level `if:` guards are fine; a cancelled
run does not, which is why the `pr-checks` caller's trigger types are what they are
(release-flow's README, *Calling the workflows*). A matrix job's check-run is named
`<job name> (<value>)`, which is why the reusable workflows carry a scalar `python-version`
(ha-integration-ci's README, *Implementation notes*); never assume a context equals the job
name.

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

`dependency-review.yml` and `issue_stale.yml` are the two plain workflows described in
`reference/github-actions.md`. Every `uses:` in the scaffold, callers included, is pinned by
commit SHA with the version in a trailing comment, for the reason the version model in
ha-integration-ci's README gives; `skill_audit.py` fails a bare tag or an uncommented SHA.
How Dependabot maintains those pins is `reference/dependabot.md`.
