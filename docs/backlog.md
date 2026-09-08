# Backlog

Problems, not tasks. A row records what is wrong. The decision recorded against it is the
current best answer and may be replaced when new information arrives. A row closes when the
problem is gone, not when the fix once planned for it is done, and being in this file is
never a reason to finish work that has been overtaken.

Nothing here is edited during an audit: an audit adds rows, a later pass clears them, one
issue per commit. A finding discovered while fixing is added here rather than fixed inline.

Status: `open` · `decided` · `fixed` (with commit) · `superseded by <row>` · `wontfix` (with reason)

Live rows: 98, 143, 144, 149, 158, 159, 163, 168, 170, 171, 172 and 173. Every other row has
closed into a file under `docs/backlog/`, named for the phase it belongs to and linked from
the section it left. Numbers are globally unique and never reused, because commit messages
in five repositories address them.

Reading a Commit column: rows 100-102, 104-115, 120, 121, 129, 130 and 133 name the first
commit of the repository where the fix lives rather than a commit in this one, and rows
from 134 name that repository's later commits by hash. Without that, a bare hash in a phase
file resolves against nothing.

A closed row is not rewritten. A claim in one that turns out to be false becomes a new row
here, so the phase files stay a transcript that can be checked against git. Live rows take
the problem, decision and evidence shape as they are next worked, rather than in one pass:
rewriting a row nobody is touching is how this file drifted out of step with itself twice
in a day.

### From the reviews of the three new repositories (2026-09-05)

Moved to `docs/backlog/2026-09-05-three-new-repos.md`. Rows 100 to 116.

### From the single-source audit of 2026-09-05

Moved to `docs/backlog/2026-09-05-single-source.md`. Rows 117 to 128.

### From the fourth single-source review (2026-09-05, after rows 117-127 cleared)

Moved to `docs/backlog/2026-09-05-fourth-review.md`. Rows 129 to 133.

### From the v1.0.0rc1 cycle of the three CI repositories (2026-09-05)

Moved to `docs/backlog/2026-09-05-rc1-cycle.md`. Rows 134 to 140.

### From the audit of the two integrations still to migrate (2026-09-06)

`skill_audit.py` at ha-integration-ci `v1.0.0` run against clones of `ha-lego` (54 failures)
and `ha-pimoroni-unicorn` (53); with rows 141 and 142 fixed, 52 and 53. Most are the
pre-caller state row 98 replaces and are not rows of their own. These are the ones that
are not: two failures the audit reports wrongly, and five facts about the repositories and
the stack that the migration has to answer before it starts.

Rows 141, 142, 145, 146 and 147 moved to `docs/backlog/2026-09-06-integrations-audit.md`.

| # | Finding | Fix | Commit |
|---|---|---|---|
| 143 | **`ha-pimoroni-unicorn` has no required status checks on `main`.** Ruleset 17377193 "Protect main" is active over `~DEFAULT_BRANCH` but carries only `deletion` and `non_fast_forward`; no `required_status_checks` rule, and classic branch protection 404s. Every workflow in the stack is therefore advisory there and a red PR merges, the state `github-setup.md` names as making the stack decorative. It also carries a `bypass_actors` entry granting repository role 5 `bypass_mode: always`, which the same file says does not constrain anyone holding admin and should be empty. `ha-lego` has ruleset 20509564 with nine contexts, no bypass, and is fine | Add the `required_status_checks` rule and empty the bypass list as part of that repository's migration; the contexts cannot be chosen before it, because the migration renames them | open |
| 144 | **`ha-lego` still triggers `pr-checks.yml` on `labeled` and `unlabeled` with `cancel-in-progress`.** The five-runs-in-two-seconds cancel storm that made a PR unmergeable was observed on `ha-lego` #22 and is documented in release-flow's README; the repository that produced the incident is the one still carrying the trigger | Subsumed by the migration: release-flow's caller block omits both types. Until then, any Dependabot PR there can still hit it | open |

### From proving the panel path on the testbed (2026-09-06 to 2026-09-07)

Every row here was found by doing the work rather than by reading it: applying the
rulesets, giving the testbed a panel, building the path check against a reviewer's
counter-examples, and reviewing each branch that came out of it.

Rows 148, 150, 151, 152, 153, 154, 155, 156 and 157 moved to `docs/backlog/2026-09-06-panel-path.md`.

| # | Finding | Fix | Commit |
|---|---|---|---|
| 149 | **Both integrations carry a superseded shell audit.** `scripts/skill_audit.sh` in each, and the two differ. It pre-dates `skill_audit.py`: it looks for the underscore workflow names and calls itself "the mechanical subset of Mode 4", a mode the skill no longer has. Anyone who runs it gets a verdict against a contract that no longer exists, which is worse than no local audit. The migrated testbed keeps only `bootstrap_repo.sh`, so this is not something the caller model leaves behind by design. Both repositories also still carry the four release scripts and their tests that now live in release-flow | Delete both, with the copied release scripts, as part of each migration; the audit runs from ha-integration-ci through `quality-audit.yml`, and locally by checking that repository out. Listed in each repository's `docs/ci-migration-todo.md`, per row 146 | open, with the integrations |
| 158 | **Goal (6) of row 98 is a rule nothing enforces.** It says a release of a CI repository is proven on the testbed before it is tagged. `ha-panel-ci` was tagged `v1.0.0` while no repository anywhere called its one reusable workflow, and row 157 is what the first call then found. The same hole is open for any workflow a CI repository adds next | A check in each CI repository's own `ci.yml`: every workflow it defines with `on: workflow_call` must be named by a caller in `ha-ci-testing`, read over the API. Built in release-flow as `testbed-coverage.yml` over `scripts/testbed_coverage.py`, which that repository calls from its own `ci.yml`; a reusable workflow no consumer may call declares that in its own text rather than being named in an exception list. Run by hand against the live testbed it reports full coverage. The other two CI repositories still need their callers, which they cannot pin until release-flow releases | `release-flow` 5846703, on `feat/testbed-coverage`, pushed as PR #3 |
| 159 | **Neither panel defect needed a testbed to find, and one of them was mine to catch.** Row 157 trips only on `npm ci`; `npm install` writes the faulty lock file and exits 0. All four commands were run locally before pushing, but the install was run as `npm install`, which is not the command the workflow runs; `npm ci` is the one that reads the lock file back, and it was never run, so a lock file nobody could see was wrong reached a runner. Row 156 is older: the shipped `.gitignore` never covered `node_modules`, `ha-lego` hit that and added the line to *its own* copy, and nothing carries a consumer's fix to a copied file back to the template it was copied from. Row 98 solved that one-way street for workflow bodies and left it open for `.gitignore`, `pyproject.toml`, `conftest.py`, `ruleset.json` and the drafter config | For 157: ha-panel-ci's README now carries the four commands in order, install first, under *Proving a panel locally*, and the claim that it "fails only in CI" is corrected — it fails anywhere `npm ci` runs. For 156 the one-way street has no fix yet and is the open half of this row | `ha-panel-ci` 7ff2c39 |

### From readying the branch for merge (2026-09-08)

| # | Finding | Fix | Commit |
|---|---|---|---|
| 173 | **Striking goal (7) of row 98 removed the only thing that would have surfaced row 156.** Goal (7) had the audit compare what a scaffold still copies — `.gitignore`, `pyproject.toml`, `conftest.py`, `ruleset.json`, the drafter config, the commit hook — against the templates at the pinned version, and name the drift. It was struck on 2026-09-06 on the grounds that `check_callers`, `check_action_pins` and the config checks cover what matters. Row 156 is the counter-example, and it arrived after the strike: `ha-lego` had added `node_modules/` to its own copy of the template's ignore file, the template never learned of it, and it was found only because a panel install in the testbed offered the whole tree for staging. Row 159's open half is the same shape stated as a rule, and it currently has no path to a fix, because the check that would have reported the difference is the one that was struck. Goal (7) and row 159 point in opposite directions — one detects a consumer diverging from the template, the other carries a consumer's improvement back — but the detection is the first half of the second, and neither exists now | Re-decide goal (7) with row 156 as the evidence it did not have on 2026-09-06. This is the case the register's own rule describes: a decision is the current best answer and new information may replace it, so the strike is not binding. What a revived check would report is drift in either direction, which is a fact, not a verdict; who is ahead is a judgement for whoever reads it | open |
| 172 | **`Version validation` fails on PR #65 with a traceback, not a verdict.** `ValueError: cannot parse version: 'null'` out of `manifest_gate.py`. The job runs from `main`'s copied `pr-checks.yml` under `pull_request_target`, reads the branch's `plugins/ha/.claude-plugin/plugin.json`, and finds no version, because a Claude Code marketplace declares none and Claude Code resolves it from the commit SHA. Proven with the diff, which is what the narrow exception in `discipline.md` requires before it may be claimed: `main`'s copy defines the job and carries `7.3.0rc2`; the branch's `pr-checks.yml` is a caller with one `pr` job and no version gate, and its manifest carries no version at all. So the PR deletes both the job and the data the job reads, and the job can never go green on the PR that removes it. Ruleset 18081788 does not require this context, so it does not block the merge | Nothing on the branch. This is the one sanctioned `pull_request_target` case, and it disappears at the merge along with the copied body; whoever merges says so in the PR, as that rule demands, and verifies on the next PR. The crash itself is confined to the copy being deleted: release-flow's `pr-checks.yml` calls `manifest_gate.py --suggest` with `--last-release` and `--labels` only, never `--pr-version`, so the `parse_semver` call that raised is unreachable in the shipped model, and `--last-release` falls back to `0.0.0` when no full release exists | open, resolves at merge |

### From the reviews of 2026-09-07, after the gate reached the CI repositories

Four context-free reviewers, one per repository, run once the governance gate covered all
four CI repositories rather than only this one. Every finding below was verified live by
the reviewer that raised it, and every fix re-verified after. The rows here come from
three of the four; the testbed's own review has not reported yet.

Rows 160, 161, 162, 164, 165, 166, 167 and 169 moved to `docs/backlog/2026-09-07-gate-to-ci.md`.

| # | Finding | Fix | Commit |
|---|---|---|---|
| 163 | **This repository's own `.gitignore` has the gap row 156 closed in the template.** It names the Python caches and a dotfile rule and not `node_modules`. Live on 2026-09-07: an untracked Cloudflare wrangler install sits at the root, unrelated to this repository and left by work run from the wrong directory, one `git add .` from being committed. Row 156's fix was scoped to the template and the testbed, so the repository that ships the fix does not carry it. Separately, `docs/workflow-map.md` — deleted on purpose at `f5775ec` — is present again at that path, and not as a file: it is a character device, `1, 3`, the same masking that sits over `.mcp.json`. `git status` reports it untracked and `ruff format` exits non-zero unable to read it. The cause, established on 2026-09-08: the sandbox masks every `denyWrite` path that has no real file behind it, and leaves every one that does. Across the 21 unique such paths in the two settings layers together, exactly two are masked, and they are exactly the two absent from disk. This one is still a live entry in `~/.claude/settings.json`, in both its deny list and its `denyWrite`; `fac5156` removed only the repository's own copy, so the mask is current rather than left over, and an earlier draft of this row had that backwards. The other is `/home/juicebox/ha-panel-ci/scripts`, added on 2026-09-08 for a directory that repository has never had. So a `denyWrite` entry naming a path that is not there manufactures an unreadable file at it | The ignore line is carried, so the install no longer offers itself for staging. The masking entry for `docs/workflow-map.md` was removed from the user-level settings on 2026-09-08 and the device cleared with it, immediately and with no restart: that path no longer exists, `git status` no longer reports it, and `ruff format --check` exits 0 where it had exited 2. The duplicated `/home/juicebox/ha-integration-ci/scripts` entry went with `de6af28`. Left open: `/home/juicebox/ha-panel-ci/scripts` is still listed for a directory that repository has never had, so it still manufactures a phantom there; and the stray `package.json` with its lock file at this repository's root are the maintainer's, since this session created neither and deleting what it did not make is how the wrong thing gets deleted | `a210e3d`, `de6af28`; the panel-ci entry and the stray files open |
| 168 | **Merging this branch would leave three required contexts that nothing can report.** Ruleset 18081788 requires six contexts, and three of them — `CC labelling`, `CC label validation` and `CC title validation` — are unprefixed. This branch turns the workflows producing those three into callers with job ids `pr` and `lint`, and GitHub names a called workflow's check-run `<caller job id> / <called job name>` — so once the branch is on `main` they report as `pr / CC labelling`, `pr / CC label validation` and `lint / CC title validation` instead. PR #65 still shows the unprefixed names, because a `pull_request_target` workflow loads its definition from `main`, which still carries the copied bodies: the check that would catch this is the one thing that cannot see it. Every PR opened after the merge would block forever on three contexts nothing produces. That is the failure rows 138, 141 and 147 each describe from a different angle, arriving on the repository that wrote them | The ruleset and the merge move together: rename those three to their prefixed forms in the same change that merges this branch, and before any other PR is opened. Rename only those three. The other three — `Ruff, Pytest and the skill audit`, `Validate marketplace + plugin manifests` and `Dependency review` — come from ordinary jobs in this repository's own workflows, keep reporting unprefixed, and must stay exactly as they are; an earlier draft of this row said "rewrite to the three prefixed contexts", which read literally deletes three working gates at the moment of merge. A payload built from the live ruleset that changes those three strings and nothing else is at `.tmp/ruleset-ha-skills-after-merge.json`. It cannot be applied earlier, because the prefixed contexts do not exist until the callers are on `main`, and requiring a context that has never reported blocks every PR in the meantime | open |
| 170 | **The testbed's panel proves a template it does not match, and its own tests are never type-checked.** Four findings from the fourth review, each verified live. `tsconfig.json` includes `src/**/*.ts` only, so `npm run check` never sees `frontend/test/`; a deliberate type error appended to the panel's only test still exits 0, and vitest transpiles without checking types, so nothing anywhere catches it. That file is byte-identical to ha-panel-ci's template, so every scaffolded panel inherits it. The testbed's `package.json` asks for `esbuild: ^0.28.0` while the template at the tag its caller pins ships `^0.25.0`, and ha-panel-ci's README says only the two placeholders are ever edited — so the testbed installs cleanly by deviating, and proves the template as tagged for nothing. Resolving the released template's own ranges reproduces the two-copy split row 157 describes. The testbed's Dependabot configuration declares `github-actions` and `pip` and no `npm`, so the panel's four dependencies and its lock file are never bumped, while ha-panel-ci's own configuration does carry that entry. And the reviewer's brief told it `.tmp/` was gitignored there, which it is not: `git check-ignore` says no, so a `git add -A` during panel work would have staged the whole scratch tree | The type-check gap is the template's and is fixed there, with the testbed's copy following it. The esbuild mismatch closes itself when ha-panel-ci releases the branch carrying row 157's pin and the caller moves to that tag; until then the deviation is what makes the testbed installable and is left in place deliberately. Done so far: the template's `include` now covers `test/**/*.ts`, proven on a scratch consumer built from the template itself — a clean type-check passes, a deliberate error in the test fails, and the same error under the old `include` still passes. The scratch ignore is added to the testbed on `ci/ignore-scratch` and to the skill's own template, so no scaffolded repo starts without one. Left: the testbed's copy of the `tsconfig` and its missing `npm` entry, both of which need its panel branch checked out, which row 167 says to do from a shell the sandbox does not cover | `ha-panel-ci` 53d58a9; `ha-ci-testing` a5e3bd1; the rest open |
| 171 | **The register drifted again within a day, and one of its own remedies was destructive.** A fifth review found it. Rows 158 and 162 and the Open section all still said "unpushed" for branches already on GitHub — the second prose version of that index, drifting exactly as the first had. Row 168's remedy read "rewrite 18081788 to the three prefixed contexts", which carried out literally deletes the three required contexts this repository's own ordinary jobs produce, stripping three working gates at the moment of merge. Row 163 said it had checked six paths where the two settings layers hold 21, and had the cause backwards: `docs/workflow-map.md` is still a live entry in the user-level settings, so its mask is current rather than residual, and the remedy pointed at the wrong file. Row 166 claimed three places now say why the previous window counts when only the docstring does. Four already-cleared rows — 105, 108, 114 and 115 — carry a fifth cell that GitHub-flavoured markdown silently drops, the same defect fixed in three others the day before. And two subjects overstated their diffs: `f9a6331` says three rows and changed two, `9539148` says the template carries a comment it does not | All corrected. The Open section is no longer prose: it is a table with one state column per row, so there is a single place to keep true rather than a paragraph that restates what the Commit column already says. The four fifth cells are merged into their Fix columns. The two subjects stand, since they are committed and the rows they describe are right. Still open and the maintainer's: the restored `[read-the-file]` hook and the surviving `[read-dont-search]` hook state the same three facts and both fire every session | part fixed, part open |

### From the CI contract of 2026-08-21, reconciled 2026-09-04

The contract's gap list lived outside this repo, and the CI plan of 2026-08-31 was built
from this file alone, so its item 8 was never planned and the copy model it replaces was
audited and fixed for three days instead. Everything still outstanding from that list is
here now, so there is one list.

Row 99 moved to `docs/backlog/2026-08-21-ci-contract.md`.

| # | Finding | Fix | Commit |
|---|---|---|---|
| 98 | **Workflow bodies do not propagate to scaffolds.** Dependabot bumps the action pins inside a copied workflow and never its body, so the setup-python step of row 84, the panel guard of row 85 and every future change reach a scaffold only by hand-copying the templates, as `ha-ci-testing` #12 and #13 did. Contract item 8, agreed 2026-08-21, was never planned. **Aim:** a change to integration CI reaches every scaffold without anyone copying anything, and every scaffold can state which CI version it runs. **Goals:** (1) each workflow has one body in one home, and a scaffold's workflow file is a pointer to it, `uses: <repo>/.github/workflows/<name>.yml@<sha> # vX.Y.Z`, the shape every popular action already uses; (2) the body checks the CI repo out at its own SHA to run `scripts/`, so scripts, their tests, `patch_twins`, the byte-identical checks and `check_self_diff` all go; (3) no secret crosses except the draft-PR opener's `RELEASE_TOKEN`, declared required by that one workflow and supplied by name in its pointer, never inherited; the other eleven use the scaffold's own `GITHUB_TOKEN`; (4) Dependabot delivers a CI release to every scaffold as its existing weekly grouped PR, moving the SHA and the version comment together; (5) the version is a repo's release tag, pinned as `@<sha> # vX.Y.Z`, because GitHub versions repositories, not files, and the split below is by shared code so that a bump moves only the pieces that share it; (6) no repo runs integration workflows on itself; the testbed is where a release of any of them is proven before it is tagged; (7) what a scaffold still copies, the pointer files, `dependabot.yml`, the drafter config, `ruleset.json`, the commit hook, the `CLAUDE.md` snippet, `pyproject.toml`, `conftest.py`, `requirements.test.txt`, is compared by the audit against the templates at the pinned version and named on drift; (8) the audit otherwise judges the integration and the repo's GitHub side, nothing about copies. **Goal (7) struck 2026-09-06, discussed:** nothing compares a consumer's copies against a template; `check_callers` holds each caller to the repository and workflow it must call, `check_action_pins` to a SHA with a version comment, and the drafter-config and hook checks judge the copied configs on their content. **Decided 2026-09-06:** ha-skills becomes a plain consumer too: four release-flow callers and its own `ci.yml`; its copied bodies, the five release scripts, their tests and both `templates/` mirrors go, and `patch_twins` with them. **Decided 2026-09-04, repos created:** `release-flow` holds `pr-checks`, `lint_pr`, the draft-PR opener, the release drafter, the four scripts they share through the commit classifier, the drafter config template and the commit hook, generic to any repo using Conventional Commits; `ha-integration-ci` holds `python_validate`, `release` and `quality_audit` with `skill_audit.py` and `version_sync.py`, the three that encode what a validated integration is; `ha-panel-ci` holds `panel_bundle` and the `frontend/` templates; `ha-skills`, this repo renamed, holds the skills and the copied files only, so a skill release moves no pointer. The four workflows that are settings over a third-party action, stale, dependency review, HACS and hassfest, stay as plain files in the scaffold pointing at the action directly; they carry nothing worth versioning. **Done when:** the testbed carries pointers only and its full cycle is green; one CI release is observed arriving at the testbed as a Dependabot PR and going green with no hand edit; `ha-lego` and `ha-pimoroni-unicorn` are migrated the same way; `templates/` holds no workflow body and no script; the copy-model checks are deleted, not kept; row 99 has removed every sentence describing copying. **Standing 2026-09-06:** the testbed carries callers only and its cycle is green (`ha-ci-testing` #14-#16); `templates/` holds no body and no script; the copy-model checks are gone; this repo calls release-flow (63df160, ad0ed5d, 18c6721); row 99 is cleared; `patch_twins` is out of the gate (a83cd76). The label gate was re-proven under the callers on the testbed the same evening: PR #9, titled `fix:` over one `feat!:` commit, went `pr / CC label validation` FAILURE with the comment naming `feat!:`, beside `lint / CC title validation` and `pr / CC labelling` green. Goal (4) is half proven: the testbed's dependency graph lists all seven reusable workflows it calls as `github-actions` dependencies at their pinned SHAs, so Dependabot sees them; what has not happened is the bump PR, and the reason is in the updater's own log (`ha-ci-testing` run 34062514133, and the same on the other two): it reads `Checking if PineappleEmperor/release-flow/.github/workflows/auto-draft-pr.yml 1.0.0 needs updating`, then `Available release version/ref is 1.0.1`, then `Days since release : 0 (cooldown days 3)` and `All versions are in cooldown period, returning current version`. Dependabot resolves the SHA pin to its tag, sees `v1.0.1`, and holds it for three days by default. So every step of goal (4) is proven except the PR itself, which is a matter of waiting until 2026-09-09 or setting `cooldown: {default-days: 0}`; ha-integration-ci's README now states the delay. The testbed's `github-actions` interval moves to `daily` separately (`ha-ci-testing` PR #17, green, awaiting merge). Left: that bump PR, and `ha-lego` and `ha-pimoroni-unicorn`, whose audit is rows 141-148 | open | — |

### From the independent review of rows 84-90 (2026-09-04)

Moved to `docs/backlog/2026-09-04-review-84-90.md`. Rows 91 to 97.

### From the testbed run (2026-09-04)

Moved to `docs/backlog/2026-09-04-testbed-run.md`. Rows 85 to 90.

### From the ruff survey (2026-09-04) — cleared 2026-09-04

Moved to `docs/backlog/2026-09-04-ruff-survey.md`. Rows 82 to 84.

### From the gate rebuild (2026-09-03) — cleared 2026-09-04

Moved to `docs/backlog/2026-09-03-gate-rebuild.md`. Rows 79 to 81.

### From the CI audit pass (2026-08-31) — cleared 2026-09-03

Moved to `docs/backlog/2026-08-31-ci-audit.md`. Rows 73 to 78.

### From the post-fix independent audit (2026-08-26) — all fixed

Moved to `docs/backlog/2026-08-26-post-fix-audit.md`. Rows 44 to 72.

## Fixed

Moved to `docs/backlog/2026-08-25-earlier-fixes.md`.
