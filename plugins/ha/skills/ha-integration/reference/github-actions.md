# GitHub CI stack — contracts and template fidelity

What each shipped workflow must do, and how to copy them without drifting. The file bodies
live in the skill's `templates/`; this file is the *why*, so you can review a workflow
against it. A workflow written from these descriptions is a paraphrase, and paraphrases drift
silently — locate the templates and copy them.

GitHub-side settings (token, ruleset, required checks) are `reference/github-setup.md`.

- Where `templates/` lives
- If none of those find it, stop and say so
- Copying a template
- Sanctioned adaptations — the complete list
- `pr-checks.yml` — every PR-time job that touches labels
- Must-preserve behaviours
- The rest of the stack
- Workflows orchestrate; scripts decide
- Superseded — do not reinstate

## Where `templates/` lives

`templates/` sits next to the `SKILL.md` you are reading, in this skill's own directory.
Resolve it in this order:

1. **The base directory announced when the skill loaded.** Invoking a skill prints
   `Base directory for this skill: <path>` — `templates/` is `<path>/templates/`. Always
   correct; try it first.
2. **Installed as a plugin:** `~/.claude/plugins/cache/*/ha/*/skills/ha-integration/templates/`
3. **Personal or repo skill:** `~/.claude/skills/ha-integration/templates/`, or
   `plugins/ha/skills/ha-integration/templates/` inside a checkout of the skill repo.
4. **Last resort:** `find ~/.claude ~/.agents . -type d -path '*ha-integration/templates' 2>/dev/null`

It contains the whole stack, mirroring the target repo: `.github/workflows/*.yml`,
`.github/dependabot.yml`, `.github/release-drafter.yml`, `scripts/*`, `tests/*`, `hooks/*`,
`frontend/*`, plus `conftest.py`, `requirements.test.txt`, `ruleset.json` and `.gitignore` at
the root.

### If none of those find it, stop and say so

Report which paths you checked and ask for the skill's location. Do **not** author the
workflows, `skill_audit.py`, `manifest_gate.py`, `dependabot.yml`, `release-drafter.yml` or
`pr-checks.yml` from this document. A hand-written CI stack passes a hand-written audit, and
every divergence stays invisible until something breaks in production. Fifteen files drifted
this way once and passed the audit clean.

## Copying a template

Read the template, write it to the target path byte-for-byte, then apply only the
substitutions below. Do not reformat, reorder keys, rename jobs, add comments, or improve a
copied file. Verify with `cmp` per file rather than `diff -r` per directory — a tree still
being assembled reads as identical when individual files differ.

### Sanctioned adaptations — the complete list

Any other difference is drift.

| File | Allowed change |
|---|---|
| `.github/workflows/release.yml` | `<domain>` → the integration's domain (3 occurrences) |
| `.github/workflows/python_validate.yml` | `python-version`, **only** when HA's minimum Python has moved and the template is stale — fix the template too |
| lint/format config (`pyproject.toml`, ruff) | exclusions needed to leave copied files unformatted |
| any workflow | an action pin **newer** than the template's, where Dependabot has already bumped yours — keep the newer pin and update the template |
| `frontend/package.json` | `<domain>` and `<name>` placeholders → this integration's values |
| `requirements.test.txt` | uncomment the `home-assistant-frontend` pin, panel repos only |
| `ruleset.json` | drop a context the repo does not produce |
| `.github/workflows/auto_draft_pr.yml` | mint the token from a GitHub App instead of `RELEASE_TOKEN` — the `create-github-app-token` step and the `steps.app-token.outputs.token` substitution, nothing else. `reference/github-setup.md` has the step |

**This table is the only list.** `reference/audit.md` points here; if they ever appear to
disagree, this table wins.

## `pr-checks.yml` — every PR-time job that touches labels

One workflow, ordered with `needs:`. `auto_draft_pr.yml` opens draft PRs — draft-only, gated
on the actor being the repo owner, and the only shipped workflow permitted to open one.

**A repo that needs a second opener declares it.** `skill_audit.py` fails any other workflow
containing `gh pr create`; the one way through is a comment line
`# skill-audit: sanctioned-opener` in that workflow, carrying the reason. The marker is the
declaration — a workflow that opens PRs without one is a workflow acting as an author. There
is a second marker of the same kind for scripts: a `scripts/*.py` or `.sh` that no workflow
step runs fails the audit unless it carries `# skill-audit: local-tool`, which says it is a
developer utility rather than a CI check that silently stopped running.

| Job | `needs:` | Does |
|---|---|---|
| `label` | — | sole labeler: autolabeler + removal-only superseded step |
| `title-check` | `label` | comments when the title maps to no label; suggests a type from the commits; withdraws itself when fixed |
| `version-gate` | `label` | version gate via `scripts/manifest_gate.py`; skips itself in a tag-driven repo, where `release.yml` sets the version |

### Must-preserve behaviours

- **One workflow, because jobs can be ordered and workflows cannot.** `needs:` is the only
  sequencing primitive Actions offers, and it works *within* a workflow. Across workflows the
  only option is reacting to the `labeled` event — which never fires, because the autolabeler
  applies its label with the default `GITHUB_TOKEN` and GitHub suppresses events caused by
  that token. Every separate label-reader either raced the autolabeler or polled for it.
  **Do not split these back into separate workflows.**
- **`pull_request_target`, and no PR-authored code ever runs.** A fork PR under plain
  `pull_request` gets a read-only token — it cannot be labelled or commented on, which is the
  entire purpose of these jobs. `pull_request_target` supplies a writable token but runs in
  the base repo's context, so `label` and the comment jobs check out **nothing**, and
  `version-gate` checks out `base.sha` explicitly and reads the PR's manifest as data over the
  API.
- **No `${{ }}` inside any `run:`.** Untrusted strings — the PR title, the PR's own manifest
  version — reach the shell through `env:`. A fork PR controls its manifest `version` string
  completely; interpolated into a command line, that is shell injection against a writable
  token. `skill_audit.py` enforces this across every workflow.
- **`title-check` decides from the PR's real labels**, never a copy of the autolabeler's
  regexes — a duplicate drifts from `.github/release-drafter.yml`. It suggests; it never
  edits the title.
- **No job writes the PR body.** The changelog is built from commit subjects at release time,
  so a generated body would duplicate it and clobber whatever a human wrote.

## The rest of the stack

All paths assume one integration per repo: `custom_components/<domain>/manifest.json`,
resolved with `ls custom_components/*/manifest.json | head -1`. Pinned action versions are a
snapshot — `reference/freshness.md` holds the values, the date and the re-derivation command.

**`lint_pr.yml`** — semantic PR-title gate.

**`auto_draft_pr.yml`** — the draft-PR opener. Uses `RELEASE_TOKEN`, because a PR opened with
the default token fires no `pull_request_target` and would be permanently unmergeable.

**`quality_audit.yml`** — runs `skill_audit.py` and `version_sync.py` on every PR; the
conformance gate.

**`dependency_review.yml`** — fails a PR that adds a dependency carrying a **high-severity**
advisory. Lower severities are deliberately not gated.

**`frontend_build.yml`** — *Panel bundle staleness check*: rebuilds the panel and diffs the
committed bundle. Path-filtered, panel repos only. Details in `reference/panels.md`.

**`stale.yml`** — labels stale issues; never closes them.

**`hassfest_validate.yml`** — HA manifest, services and quality-scale validation.

**`hacs_validate.yml`** — HACS 9-check validation. **No `ignore:` input** — ignoring any check
disqualifies the repo from the default store.

**`release_drafter.yml`** — maintains the draft on pushes to `main` and writes the final body
on `release: published`. Resolves the version from the merged PRs' labels, never from a file.
Labelling lives in `pr-checks.yml`, so there is no autolabeler job here.

**`.github/release-drafter.yml`** (config) — `name-template`/`tag-template` (both
`v$RESOLVED_VERSION`, which is what names the tag), title-only autolabeler rules with breaking
`!` first, the label→semver `version-resolver`, `categories` carrying the `semver-increment`
values, and a placeholder `template` visible if the generator fails to run. The drafter owns
the draft and the tag; `release_drafter.yml` then writes the generated body over the top and
`check_release_notes.py` validates the result. Nothing else belongs in this file — its
autolabeler vocabulary must stay in step with `lint_pr.yml`'s allowlist.

**`release.yml`** — *Create Release ZIP*. Required when `hacs.json` sets `zip_release: true`:
builds `<domain>.zip` with the integration files at the **zip root** — `cd` into the package
before zipping — and attaches it to the published release so HACS has an asset to download.
Uploads with the `gh` CLI; `actions/upload-release-asset@v1` is archived, so do not reinstate
it.

**`python_validate.yml`** + **`requirements.test.txt`** — ruff, pyright and pytest on HA's
floor Python. No matrix, deliberately: a single-value matrix renames the check-run out of the
ruleset. Keep the Python version in lockstep with `pyproject.toml` and `pyrightconfig.json`.
The pytest step fails on a red test, warns when `tests/` is absent so a fresh scaffold is loud
rather than silently green, and hard-fails when `tests/` exists without
`requirements.test.txt` — that combination means the suite was never installed.

**`scripts/manifest_gate.py`** + **`tests/test_manifest_gate.py`** — the version gate's
decision logic, in a unit-tested script rather than inline bash. A real bug shipped from
inline logic: strict equality rejected a `chore` PR sitting at `1.2.0` while riding a minor
already merged that cycle. The gate enforces a floor (≥ the label's minimum bump from the last
release) and a ceiling (≤ the in-cycle version on `main`), lets prereleases merely differ,
exempts `dependabot[bot]`, and requires the PR title and its commits to agree about whether
the change is breaking.

**In the canonical tag-driven repo the whole `Version gate` step is skipped** — the committed
manifest is a placeholder, so there is nothing to compare; `release.yml` sets the version at
publish. That takes the breaking-marker agreement with it, since it runs inside the same step:
in a tag-driven repo nothing mechanically checks that a `feat!:` commit reached a `!` PR title,
so the label is on the author. All the job does there is write the advisory summary — what
this PR's labels imply the next release will be. The version model is
`reference/versioning.md`.

**`.github/dependabot.yml`** — configuration and consequences are `reference/dependabot.md`.

**`templates/hooks/`** — optional per-turn reminders for your own `~/.claude`, gated on marker
files so each fires only where it applies. Install per the header in each script.

## Workflows orchestrate; scripts decide

A `run:` block may invoke a tool, pass data between steps, and guard on one condition.
Anything that classifies, compares or computes belongs in `scripts/`, where it has unit tests
— logic inside a workflow can only be tested by running CI, so its first failure is a real PR.
If a change to a workflow needs a `case`, a loop or a regex, write it in Python and call it
from the step.

## Superseded — do not reinstate

`create-dev-pr.yml` auto-opened a draft PR on every push to a non-main branch. Four problems,
the first fatal: it **cannot serve fork-based contributions**, since a `push` workflow never
fires for a contributor pushing to their own fork and a fork's `pull_request` token is
read-only. It also opened a PR for every WIP branch, clobbered human-edited titles, and
tripped the `GITHUB_TOKEN` suppression rule so no checks ran on first open.

`pr-labeler.yml`, `pr-title-check.yml`, `pr-commit-summary.yml` and
`check-manifest-version.yml` are superseded by `pr-checks.yml` — the first three because they
could not be ordered against the labeler, and the last because its `push` trigger was a no-op
(both its steps were gated on `github.event_name == 'pull_request'`).

A human-opened PR is not a token-caused event, so every `pull_request` workflow runs on first
open. The suppression footgun applies only to PRs opened by a workflow using the default
token.
