# GitHub CI stack — rationale & required behaviours

The **file bodies** live in the skill's `templates/` dir (mirrors the target repo: `templates/.github/workflows/*.yml`, `templates/.github/*.yml`, `templates/scripts/*`, `templates/tests/*`, `templates/hooks/*`, `templates/requirements.test.txt`). Copy them as-is — they are self-contained, no external repo. This file is the **why**: the behaviours each workflow must preserve. Read it before changing any workflow.

- This file does not substitute for the templates
- PRs are opened by humans and by `auto_draft_pr.yml`
- Superseded — do not reinstate
- The `GITHUB_TOKEN` `opened`-suppression footgun is gone
- `.github/workflows/release_drafter.yml`
- `.github/workflows/release.yml`
- `.github/workflows/python_validate.yml`
- `pr-checks.yml`'s `version-gate` job
- `.github/dependabot.yml`



### This file does not substitute for the templates

⚠️ It describes required behaviour so you can *review* a workflow; a workflow written from these descriptions is a paraphrase, and paraphrases drift silently. Locate `templates/` per **Where `templates/` lives** in `reference/github-setup.md` and copy byte-for-byte; if you cannot locate it, stop and say so rather than authoring from prose. Sanctioned adaptations are the table in `reference/github-setup.md` — nothing else.

#### pr-checks.yml template (canonical — copy this, no external repo)

### PRs are opened by humans and by `auto_draft_pr.yml`
— draft-only, gated on the actor being the repo owner, and the only workflow permitted to open one. `pr-checks.yml` holds every PR-time job that reads or writes labels, in **one** workflow, ordered with `needs:`.

| Job | `needs:` | Does |
|---|---|---|
| `label` | — | sole labeler: autolabeler + removal-only superseded step |
| `title-check` | `label` | comments when the title maps to no label; suggests a type from the commits; withdraws itself when fixed |
| `version-gate` | `label` | last-published-release version gate via `scripts/manifest_gate.py`; skips itself in a tag-driven repo, where `release.yml` sets the version |

Must-preserve behaviours:

- **One workflow, because jobs can be ordered and workflows cannot.** `needs:` is the only sequencing primitive GitHub Actions offers, and it works *within* a workflow. Across workflows the only option is reacting to the `labeled` event — which never fires, because the autolabeler applies its label with the default `GITHUB_TOKEN` and GitHub suppresses events caused by that token. Every separate label-reader therefore either raced the autolabeler or polled for it. Both were workarounds; `needs:` is the fix. **Do not split these back into separate workflows.**
- **`pull_request_target`, and no PR-authored code ever runs.** A fork PR under plain `pull_request` gets a read-only token — it cannot be labelled, commented on, or have its body updated, which is the entire purpose of these jobs. `pull_request_target` supplies a writable token but runs in the base repo's context, so: `label` and the comment/body jobs check out **nothing**; `version-gate` checks out `base.sha` **explicitly** (never the head) and reads the PR's manifest **as data over the API**.
- **No `${{ }}` inside any `run:`.** Untrusted strings — the PR title, and the PR's own `manifest.json` version — reach the shell through `env:`. A fork PR controls its manifest `version` string completely; interpolated into a command line that is shell injection against a writable token. `skill_audit.py` enforces this mechanically.
- **`title-check` decides from the PR's real labels**, never a copy of the autolabeler's regexes — a duplicate drifts from `.github/release-drafter.yml`, and a checker that disagrees with the thing it checks is worse than none. It **suggests**; it never edits the title.
- **No job writes the PR body.** `auto_draft_pr.yml` opens a draft with a title derived from the commits and an empty body; the changelog is built from commit subjects at release time, so a generated body would only duplicate it and clobber whatever a human wrote.

### Superseded — do not reinstate

`create-dev-pr.yml` auto-opened a draft PR on every push to a non-main branch and derived the title from the commits. Four problems, the first fatal: it **cannot serve fork-based contributions** (a `push` workflow never fires for a contributor pushing to their own fork, and a fork's `pull_request` token is read-only), so the convention only ever worked for people with write access. It also auto-opened a PR for every WIP branch, clobbered human-edited titles, and tripped the `GITHUB_TOKEN` `opened`-suppression rule so no checks ran on first open.
>
> The separate `pr-labeler.yml`, `pr-title-check.yml`, `pr-commit-summary.yml` and `check-manifest-version.yml` are superseded by `pr-checks.yml` — the first three because they could not be ordered against the labeler, and `check-manifest-version.yml` because its `push` trigger was a no-op (both its steps were gated on `github.event_name == 'pull_request'`).
>
### The `GITHUB_TOKEN` `opened`-suppression footgun is gone
A human-opened PR is not a token-caused event, so every `pull_request` workflow runs on the first open, as it always should have.

#### Remaining workflow + config templates (canonical — copy these, no external repo)

All paths assume one integration per repo: `custom_components/<domain>/manifest.json` is resolved with `ls custom_components/*/manifest.json | head -1`. Action majors are a snapshot — see the **Freshness** table in `reference/freshness.md` for the captured values, the date, and the command to re-derive them. Dependabot (`github-actions`) keeps the *tag-pinned* ones bumped in a consuming repo, but it cannot bump the pins in these templates, nor the mutable `@main`/`@master` refs on `hacs/action` and `Hassfest manifest validation` (deliberate — rationale in the workflow headers and the Freshness note). The full release path is: `release_drafter.yml` drafts notes on `main`, publishing that draft creates the tag, and **`release.yml` (*Create Release ZIP*) attaches the `<domain>.zip` asset on publish** — the last is mandatory whenever `hacs.json` sets `zip_release: true` (omit it only on a repo that deliberately uses no `zip_release`).

**`.github/workflows/lint_pr.yml`** — semantic PR-title gate.

**`.github/workflows/auto_draft_pr.yml`** — the draft-PR opener; draft-only, actor-gated, uses `RELEASE_TOKEN` so checks actually run.

**`.github/workflows/quality_audit.yml`** — runs `skill_audit.py` and `version_sync.py` on every PR; the conformance gate.

**`.github/workflows/dependency_review.yml`** — blocks a PR introducing a dependency with a known advisory.

**`.github/workflows/frontend_build.yml`** — *Panel bundle staleness check*; rebuilds the panel and diffs the committed bundle. Path-filtered, panel repos only.

**`.github/workflows/stale.yml`** — marks stale issues; never closes them.

### `.github/workflows/release_drafter.yml`
— drafts release notes on pushes to `main`, and writes the final body on `release: published` (labelling lives in the `label` job of `pr-checks.yml`, so no autolabeler job here). Resolves the release version from the merged PRs' labels — never from a file.

**`.github/release-drafter.yml`** (config) — title-only autolabeler rules (breaking `!` first), a placeholder `template` that shows if the generator fails to run, label→semver `version-resolver`.

### `.github/workflows/release.yml`
— *Create Release ZIP*. Required when `hacs.json` has `zip_release: true`: builds `<domain>.zip` (integration files at the **zip root**) and attaches it to the published release, so HACS has the asset to download. `cd` into the package before zipping so paths are root-relative (not `custom_components/<domain>/…`). Uses the `gh` CLI to upload (the old `actions/upload-release-asset@v1` is archived — don't reinstate it).

**`.github/workflows/hassfest_validate.yml`** — HA manifest/services/quality-scale validation.

**`.github/workflows/hacs_validate.yml`** — HACS 9-check validation. **No `ignore:` input** — ignoring any check disqualifies the repo from the default store.

### `.github/workflows/python_validate.yml`

+ **`requirements.test.txt`** — ruff + pyright + **pytest** on HA's floor Python (no matrix, deliberately — a single-value matrix renames the check-run; keep the Python version in lockstep with `pyproject.toml` / `pyrightconfig.json`). **Tests run in CI, not local-only:** the quality scale requires a test per rule marked `done`, so a suite CI never runs lets those claims rot unverified. The pytest step fails the build on a red test, warns (doesn't fail) when `tests/` is absent so a fresh scaffold is loud rather than silently green, and hard-fails when `tests/` exists but `requirements.test.txt` doesn't — that combination means the suite was never actually installed. `pytest-homeassistant-custom-component` hard-pins `homeassistant==<matching release>`, so the pin in `requirements.test.txt` decides which HA the suite runs against; a mismatched pin fails at import, not at test time.

### `pr-checks.yml`'s `version-gate` job

+ **`scripts/manifest_gate.py`** + **`tests/test_manifest_gate.py`** — version gate **against the last published release** (not `main` HEAD). ⚠️ **The decision logic lives in a unit-tested Python script, NOT inline bash.** A real bug shipped from inline-bash logic: it used strict equality (`suggested == manifest`), so a `chore` PR sitting at `1.2.0` (riding a minor already merged this cycle) was rejected with "expected v1.1.1" — even though `1.2.0` is a perfectly valid in-cycle version. Inline gate logic is untested and regresses silently; extract it so it has a test suite. The gate must enforce a **floor** (≥ the label's minimum bump from the last release — catches under-bumps) **and** a **ceiling** (≤ the in-cycle version on `main`, or this PR's own label bump if it escalates the tier — catches over-bumps), with prerelease versions only needing to differ and `dependabot[bot]` exempt.

The workflow just gathers inputs and shells out:

`scripts/manifest_gate.py` — pure `evaluate()` + thin CLI (add `"scripts/*" = ["T20", "INP001"]` to ruff `per-file-ignores`):

`tests/test_manifest_gate.py` — load the standalone script by path (it isn't an importable package) and cover the matrix, **including the regression that shipped** (chore riding an in-cycle minor) and the over-bump it must still catch:

### `.github/dependabot.yml`
— `github-actions` is the real value; `pip` covers `requirements.test.txt`, which the template ships **pinned**, so this ecosystem now produces real PRs (it was near-useless while nothing was pinned). `chore` prefix → autolabeler maps to patch.

#### Optional: per-turn reminder hooks (personal `~/.claude`)

The repo `CLAUDE.md` rule is the **canonical, shareable** enforcement (it ships with the repo, applies to everyone). These two personal hooks are a *convenience* layer on top — they live in your own `~/.claude/` and re-arm the rules every session/turn so they don't drift down-context in a long session. **Marker-file gated** so each only fires where it applies: the skill anchor on an integration repo (`custom_components/*/manifest.json`), the CI-convention anchor on any repo using this workflow stack (`.github/workflows/pr-checks.yml`) — which includes this skill's own repo, not just scaffolded integrations.

`~/.claude/settings.json` (merge into existing `hooks`):

`~/.claude/hooks/ha-skill-reinvoke.sh` — re-arms the skill rule at session start (compaction drops the skill's guidance; stdout is injected as session context). ⚠️ **A bare "the skill is active" reminder is not enough** — it has fired while the skill was still not followed, twice, because the agent was following a faithful-sounding paraphrase of the skill rather than the artefacts it points at, and believed it was complying. A reminder cannot catch that unless it names the trap, so the template calls out the two highest-cost ones explicitly: **copy `templates/` byte-for-byte** and **docstrings are one line**:

`~/.claude/hooks/ha-resources-reminder.sh` — per-turn anchors; stdout is injected as prompt context, so keep each line terse:

`chmod +x` both scripts. Editing a hook *script* takes effect immediately (the hook re-execs it each turn); editing `settings.json` to add/remove a hook needs a `/hooks` open or restart to re-register.

---
