# Setting the repository up on GitHub

One-time setup that lives in GitHub's settings rather than in the repo: the release token, the required checks, the CI templates and the supply-chain guards. `scripts/bootstrap_repo.sh` does most of it in one command.

## `RELEASE_TOKEN` — set this up before the first release

⚠️ **One secret, once per repo, or `auto_draft_pr.yml` cannot open a PR that checks can
run on.** GitHub suppresses workflow events caused by `GITHUB_TOKEN`, so a PR opened with
it fires no `pull_request_target`: no checks run, the required ones never report, and the
PR is permanently unmergeable. That is how `create-dev-pr.yml` was removed. The opener fails
loudly instead, and `skill_audit.py` fails a repo that ships it without the secret.

The **release** path needs no token: both the full release and its next rc are kept as
drafts, and publishing a draft is a human action, so its events fire normally.

**Two ways to provide it. Pick by how many repos you maintain.**

**A GitHub App (preferred for more than one repo).** An App is installed once and then
covers every repo you install it on, its tokens are minted per run and expire in an hour,
and it survives you rotating your own credentials. Events it causes DO trigger workflows,
which is the whole requirement.

1. github.com → Settings → Developer settings → GitHub Apps → **New GitHub App**
2. Name it (e.g. `<you>-release-bot`), untick **Webhook → Active**
3. **Repository permissions**: `Contents: Read and write`, plus `Pull requests: Read and
   write` if you use `auto_draft_pr.yml` — nothing else
4. Create it, note the **App ID**, then **Generate a private key** (downloads a `.pem`)
5. Install it: the App's page → **Install App** → pick the repos
6. In each repo: Settings → **Secrets and variables** → **Actions** → **Secrets** tab →
   **New repository secret** → `APP_ID` (the numeric ID), then again for `APP_PRIVATE_KEY`
   (the whole `.pem` contents, including the BEGIN/END lines) → **Add secret**
7. In `auto_draft_pr.yml`, mint the token before the step that needs it:
   ```yaml
   - uses: actions/create-github-app-token@v2
     id: app-token
     with:
       app-id: ${{ secrets.APP_ID }}
       private-key: ${{ secrets.APP_PRIVATE_KEY }}
   # then use ${{ steps.app-token.outputs.token }} wherever RELEASE_TOKEN appears
   ```

**A fine-grained PAT (fine for a single repo).** Simpler, but tied to your account and it
expires on a date you have to remember.

1. github.com → Settings → Developer settings → Personal access tokens →
   **Fine-grained tokens** → **Generate new token**
2. **Resource owner**: your account · **Repository access**: Only select repositories →
   this repo
3. **Repository permissions**: `Contents: Read and write`, plus `Pull requests: Read and
   write` if you use `auto_draft_pr.yml` — nothing else. (`Metadata: Read` is added
   automatically and cannot be removed.)
4. **Expiration**: 90 days or less
5. **Generate token**, copy the `github_pat_…` value — it is shown once
6. Repo → **Settings** → **Secrets and variables** → **Actions** → **Secrets** tab →
   **New repository secret** → Name `RELEASE_TOKEN`, paste into **Secret** → **Add secret**

**What the grant actually allows.** `Contents: write` covers creating releases, tags and
commits in the repos it is scoped to. Adding `Pull requests: write` lets it open the
draft PR — and, unavoidably, merge one, since GitHub does not separate those. Neither
permission can edit rulesets or branch protection, change repository settings, or reach
any repo outside its scope, so a required-checks ruleset still holds.

Without `Pull requests: write`, `auto_draft_pr.yml` fails with
`Resource not accessible by personal access token (repository.pullRequests)`. That
matters because this token exists to *trigger* workflows — anything it can do, a workflow
it starts can do too.

**Rotating.** Paste a new value into the same secret; nothing else changes. An App's
private key is rotated the same way, and its tokens expire hourly regardless.


## Make the checks REQUIRED — a workflow is not a gate until it can block a merge

> **A cancelled check blocks; a skipped one does not.** GitHub is explicit that a
> skipped job satisfies a required check, so job-level `if:` guards are fine.
> Cancelled runs are the hazard. Trigger on `labeled`/`unlabeled` with
> `cancel-in-progress` and a bot applying several labels at once starts a run per
> label; the concurrency group cancels all but the last, and those cancelled
> check-runs make the rollup `FAILURE` with nothing broken. The PR then reports
> `mergeable: MERGEABLE` and still cannot merge. Drop those two types: the
> in-workflow autolabeler cannot fire them anyway, because the default token
> suppresses events it causes.
>
> Confirmed by re-running a single cancelled run on ha-lego #22: the rollup went
> from `FAILURE` to `SUCCESS` with nothing else changed.

> **A matrix renames the check.** GitHub names a matrix job's check-run
> `<job> (<value>)`, so a job `Ruff, Pyright and Pytest` with `python-version: ["3.14"]`
> reports as `lint-and-type (3.14)` and a ruleset requiring the bare name waits
> forever. `templates/ruleset.json` shipped exactly this bug. Either drop a
> single-value matrix or put the suffixed name in the ruleset; never assume the
> context equals the job name.

**`scripts/bootstrap_repo.sh` does all of this once**, from the repo root after the first
push: description, topics, issues, the ruleset, `core.hooksPath`, and the `RELEASE_TOKEN`
secret (prompted, never an argument). Every item in it is a GitHub-side setting no file in
the repo can carry, and each fails quietly until the first CI run.

```bash
bash scripts/bootstrap_repo.sh "One-line description of the integration"
```

**A gate that cannot fail is not a gate.** `Version validation` skips its own steps in a
tag-driven repo, so requiring it there guarantees a green check that proves nothing — it
is not in `ruleset.json`. What it still does is useful and advisory: it writes the version
the PR's labels imply into the job summary, where the checks tab shows it.

**Two kinds of workflow, and only one is a gate.** A *check* runs on a pull request and can
be required, so a red one blocks the merge. The eight in `ruleset.json`: `CC labelling`,
`CC label validation`, `CC title validation`, `HACS validation`,
`Hassfest manifest validation`, `Ruff, Pyright and Pytest`,
`ha-integration conformance check`, and `Dependency review`. `Version validation` is
deliberately absent — see above. `Panel bundle staleness check` also runs on pull requests
and can be required in a repo that ships a panel; it is path-filtered, so it reports only
when the panel changed. Everything else — `Auto draft PR`, `Auto release zip`,
`Auto draft releases` — is process automation firing on pushes and releases. It is not a
weaker check; it is not a check at all, and requiring one would block every PR on a context
that never reports.

⚠️ **Every workflow here is advisory by default.** GitHub will let a PR merge with all of it red, so without this step the gate stack is decorative. Copy `templates/ruleset.json` and apply it once:

```bash
gh api -X POST repos/<owner>/<repo>/rulesets --input ruleset.json
```

It requires the eight job-name contexts the templates produce and keeps deletions and force-pushes blocked. `skill_audit.py` FAILs a repo whose default branch has no required checks, so skipping this shows up rather than going unnoticed.

Two ways to get it wrong, both of which block every PR permanently:

- **A context that never reports.** Requiring a check the repo doesn't produce (a repo without `quality_audit.yml` must drop `ha-integration conformance check`) leaves PRs waiting for a check that will never run.
- **A path-filtered workflow.** `build` from `frontend_build.yml` is deliberately absent for this reason: it only triggers on `frontend/` changes, so requiring it would block every unrelated PR.

⚠️ **`bypass_actors` must stay empty to mean anything.** A ruleset granting admins `bypass_mode: always` does not constrain anyone holding admin; the push reports `Bypassed rule violations` and proceeds. Overrule deliberately instead: set the ruleset's enforcement to `disabled`, merge, set it back, which leaves an audit-log entry.

> **For AI sessions.** An agent running with your `gh` credentials merges exactly as you do, and `bypass_actors` is evaluated by actor, so any bypass you hold it inherits. Two things make that silent: a broad allow-rule such as `Bash(gh pr *)` in `.claude/settings.local.json` pre-approves `gh pr merge` with no prompt, and an agent with admin can lift any rule it can see. Narrow the allow-rule to read-only verbs (`gh pr view`, `gh pr list`), and give the agent a credential without **Administration** if it genuinely should not edit rulesets or force-push. A restriction the agent can lift is friction, not a limit.

## Supply chain

Two cheap workflows ship with the stack. `dependency_review.yml` fails a PR that adds a
dependency with a high-severity advisory, reading the PR's own diff. `stale.yml` labels
issues and PRs untouched for 60 days and **never closes them** (`days-before-close: -1`)
— a closed report is a lost report.

Actions are pinned by commit SHA with the version in a trailing comment, because a tag
is mutable — whoever owns the action can repoint it at new code, which then runs with the
workflow's token. Dependabot updates both the SHA and the comment, and `skill_audit.py`
fails a workflow that uses a bare tag or a SHA with nothing saying what it is.

⚠️ **Dependabot keeps your workflows current, not the skill's copies.** Its
`github-actions` ecosystem only scans `.github/workflows` at the repo root. Your workflows
are therefore bumped for you once `dependabot.yml` is in place; the skill's `templates/`
are maintained separately, in the skill's own repo. **Consequence for you:** re-copying
from `templates/` can move a pin *backwards* if the skill's copies are older than what
Dependabot has already given you. Diff before overwriting, and keep the newer pin.

## GitHub CI templates

The full, self-contained CI stack ships in the skill's **`templates/`** dir (mirrors the target repo layout — `templates/.github/workflows/*.yml`, `templates/.github/*.yml`, `templates/scripts/*`, `templates/tests/*`, `templates/hooks/*`). Copy as-is; no external repo. One file per workflow/config/script.

##### Where `templates/` lives, and what to do if you can't find it

`templates/` sits **next to the `SKILL.md` you are reading**, in this skill's own directory. Resolve it in this order:

1. **The base directory announced when this skill loaded.** Invoking a skill prints `Base directory for this skill: <path>` — `templates/` is `<path>/templates/`. Use this first; it is always correct.
2. **Installed as a plugin:** `~/.claude/plugins/cache/*/ha/*/skills/ha-integration/templates/`
3. **Personal or repo skill:** `~/.claude/skills/ha-integration/templates/`, or `plugins/ha/skills/ha-integration/templates/` inside a checkout of the skill repo.
4. **Last resort — search:** `find ~/.claude ~/.agents . -type d -path '*ha-integration/templates' 2>/dev/null`

**If none of those find it, stop and say so.** Report which paths you checked and ask for the skill's location. Do **not** author the workflows, `skill_audit.py`, `manifest_gate.py`, `dependabot.yml`, `release-drafter.yml` or `pr-checks.yml` from this document — the prose *describes* the templates, it does not *replace* them. A hand-written CI stack passes a hand-written audit, and every divergence stays invisible until something breaks in production.

##### Copying the templates

For each canonical file: read the template, write it to the target path byte-for-byte, then apply **only** the substitutions listed below. Do not reformat, reorder keys, rename jobs, add comments, or "improve" a copied file.

**Sanctioned adaptations — the complete list. Any other difference is drift:**

| File | Allowed change |
|---|---|
| `.github/workflows/release.yml` | `<domain>` → the integration's domain (3 occurrences) |
| `.github/workflows/python_validate.yml` | `python-version`, **only** when HA's minimum Python has moved and the template is stale — fix the template too |
| lint/format config (`pyproject.toml`, ruff) | exclusions needed to leave copied files unformatted |

**Traps this section exists to close** (both have happened, with the reminder hook active and the agent believing it was complying):

- **Writing a faithful-sounding paraphrase instead of copying the artefact.** Producing a workflow that does what the prose says is *not* copying the template. Fifteen files drifted this way and passed the audit clean.
- **Multi-line docstrings.** The code style below says *short single-line* docstrings on all public functions and classes. Single line means single line.

## Workflows orchestrate; scripts decide

A `run:` block may invoke a tool, pass data between steps, and guard on one condition.
Anything that classifies, compares, or computes a value belongs in `scripts/`, where it
has unit tests — logic inside a workflow can only be tested by running CI, so its first
failure is a real PR. If a change to a template workflow needs a `case`, a loop, or a
regex, write it in Python first and call it from the step.

These templates are a dependency other repos inherit, so they are held to that standard
even where a repo's own one-off workflow would not be.

**Read `reference/github-actions.md` before changing any workflow** — it holds the must-preserve behaviours: the sole title-only labeler + removal-only superseded-label step, `$BODY` + bounded Dependabot `replacers`, the last-published-release version gate (with `dependabot[bot]` exempt and the unit-tested `manifest_gate.py`), the `pr-checks` job ordering, its `pull_request_target` safety rules and the marked-block contract, and the optional personal reminder-hook recipe.

---
