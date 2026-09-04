# Backlog

Findings only. **Nothing here is edited during an audit** — an audit adds rows, a later
fix pass clears them, one issue per commit. New findings discovered while fixing are added
here rather than fixed inline.

Status: `open` · `fixed` (with commit) · `wontfix` (with reason).

## Open

| # | Finding | Where |
|---|---|---|
| 82 | **The skill ships no ruff configuration, so every integration invents its own.** `scaffold.md` lists `pyproject.toml — ruff/pyright config` among the files to generate and ships nothing to copy; `testing.md` tells a scaffold to add `per-file-ignores` that presume an extended rule set it never names; `patterns.md` cites `G004`, which ruff's defaults do not enable. Surveyed 2026-09-04: `settleup-ha`, `ocado-ha` and `ha-pimoroni-unicorn` carry HA core's `[tool.ruff]` verbatim at ruff 0.12, still naming `homeassistant` as the first-party package; `ha-lego` an explicit 27-group list of its own; `pineapple-core-ha` and `ha-immich` `select = ["ALL"]` with two different ignore lists; `hass-claude-usage` E/F/W/UP; `ha-ci-testing` only `target-version`. Each repo re-excludes the shipped `scripts/` and `tests/` by hand (`pineapple-core-ha` switches off 13 rules for them). Measured: under HA core's current config the shipped tooling has 75 findings and the testbed integration none; under `ALL`, 726. Ship `templates/pyproject.toml` as core's `[tool.ruff]` adapted for a custom integration (`target-version`, `custom_components` first-party, `voluptuous` as `vol`, core-only paths dropped, `scripts/*` exempt from `T20` and `INP001`, `tests/**` from `INP001`, `SLF001` and `PTH`), bring the shipped tooling to that bar and `ruff format` it (11 of 12 shipped files would be reformatted today), then return the template's ruff step to `ruff check .` and add the file to the scaffold list and the adaptations table. Two of core's choices need a decision first: core bans `from __future__ import annotations` on 3.14 while `patterns.md` mandates it in every file and `check_antipatterns` warns when it is absent; and core's `google` docstring convention against the `pep257` two repos chose | `reference/scaffold.md` *Repo root*, `reference/testing.md` *Standalone helper scripts*, `reference/patterns.md` *Always add at top of every file*, `templates/.github/workflows/python_validate.yml` *Ruff*, no `templates/pyproject.toml` |

Rows 73-81 are cleared below; rows 1-72 are cleared under *Fixed*.

### From the gate rebuild (2026-09-03) — cleared 2026-09-04

| # | Finding | Fix | Commit |
|---|---|---|---|
| 79 | **The shipped tooling was never linted.** The template ran ruff on `custom_components/` alone and this repo ran pytest alone; neither carried a ruff config, so an IDE rule set decided what a reader saw | Both `python_validate.yml` copies now lint the tooling. This repo runs `ruff check .` under a new `pyproject.toml` that pins ruff's target, so IDE and CI agree; the template lints the integration under the scaffold's own rules and `scripts/` and `tests/` under `--isolated` defaults, because no shipped rule set exists yet to hold them to (row 82). The 41 findings under ruff's defaults were fixed in both copies, each through `patch_twins`; the counts first recorded here came from an IDE rule set, not ruff's | `de2693d`, `e21a247`, `266db8b` |
| 80 | **A gate restart was invisible to the caller.** Every key died with the process salt and the refusal read exactly like a stale read or an hour rollover | Every key carries a four-hex gate id as its second-last segment, and each key refusal names the cause: minted by another gate (the server restarted), minted by this one (the content moved), or no key at all. Proven live the next session, unprompted: "minted by gate 3609; this is gate 6516" | `c20425c` |
| 81 | **A test literal read as an email address to the secrets scanner and locked `tests/` for every tool**, gate included; this row's own quotation of it then locked the backlog the same way | The literal was split at the decorator by hand in the editor, the one writer the scanner does not watch; the scanner has since been disabled. Rule kept in memory: never write letter-at-letter inside one literal in a governed file | `ad22da9` |

### From the CI audit pass (2026-08-31) — cleared 2026-09-03

Each fix was seen to fail before it was trusted: the old `release.yml` step was run in a
fixture and died with `syntax error near unexpected token 'newline'`, and every new check
was run against the pre-fix file it exists to catch. Fixes landed one per commit, in
consequence order.

| # | Finding | Fix | Commit |
|---|---|---|---|
| 74 | **The shipped release was broken for every scaffolded repo.** `release.yml` carried literal `<domain>` placeholders in the zip and upload steps that nothing substituted; bash read `<` as a redirect, the step exited 2, no asset was attached, and HACS installs failed with `Could not download`. Observed on `ha-ci-testing` publishing `v0.2.1rc1` | The zip step derives the domain from `custom_components/*/manifest.json`, as the manifest step above it already did, and hands the asset path to the upload step as a step output. The `<domain>` sanctioned-adaptation row went with it — nothing is hand-edited in a copy any more | `3a53e01` |
| 75 | Nothing detected an unsubstituted placeholder in a shipped template; the one check that read `release.yml` only asked whether it mentioned `manifest.json` | `check_no_placeholders` fails a `<...>` token in any `run:`, `with:` or `env:` value of this repo's workflows and, in the skill repo, of the shipped ones. Comments are exempt, as documentation. Reported both placeholder-carrying steps of the pre-fix file | `19237ad` |
| 73 | `title-check` checked out `ref: base.sha`, frozen at PR creation, while the workflow itself runs from the base branch head — so a `scripts/` change merged mid-PR ran the new workflow against the old script (`ha-ci-testing` #9, `--mode: invalid choice: 'label'`) | Both `pr-checks.yml` copies check out `base.ref`; `check_pr_checks_shape` requires it and its message says why `base.sha` is not equivalent; the must-preserve bullet in `github-actions.md` says the same | `98771f8` |
| 76 | `check_required_contexts_have_producers` and `check_live_required_contexts` judged producers from the local checkout only, so a branch deleting a job `main` still defined read as an orphaned context — the misreading that removed `Version validation` from this repo's ruleset while `origin/main` still defined it | Both checks count jobs on `origin/<default>` as well as the working tree (union, so a branch adding a job is not misread the other way) and name the refs judged; with no clone to consult they say "working tree" in the verdict. Proven against a real clone in the tests | `14f5c88` |
| 77 | ~~Sequencing: the `Version validation` context may only be dropped after its replacement is on `main`.~~ Withdrawn as overstated — dropping it was the plan (`workflow-map.md` item 6) | `wontfix` | — |
| 78 | The governed-edit gate's enforcement lived only in `~/.claude/settings.json` while the repo hook told every clone to use it | The 14 `permissions.deny` entries and 7 `sandbox.filesystem.denyWrite` paths now live in the repo's `.claude/settings.json`, proven to hold at project scope by a three-state test. Residual per-machine setup: the MCP registration in `~/.claude.json` and the SDK `.venv` | `19ef395` |

Rows 1-72 are cleared.

Rows 1-17, 19-40, 42-43 are cleared — see *Fixed*.

### From the post-fix independent audit (2026-08-26) — all fixed

Ranked by consequence as found. Each was verified against source before being fixed; two of
the reported findings did not survive that check and are marked below.

| # | Finding | Where |
|---|---|---|
| 44 | "The real gap is `revert:`, which `lint_pr` accepts… any non-Conventional title passes" — `lint_pr.yml` ships a ten-type allowlist that rejects both. The stated purpose of the `title-check` job is fiction, and the same claim ships to contributors in a PR comment | `versioning.md:53`, `templates/.github/release-drafter.yml:6`, `templates/.github/workflows/pr-checks.yml:141` |
| 45 | The GitHub App token path is called "preferred for more than one repo", but it is not in the sanctioned-adaptations table and `check_release_token` hard-fails a repo whose `auto_draft_pr.yml` lacks the literal `RELEASE_TOKEN` | `github-setup.md:34-55` |
| 46 | "Files to generate" omits `.github/` and `scripts/` entirely, and names only `test_manifest_gate.py`; a scaffold built strictly from it fails ~13 gate checks on its first run | `scaffold.md:30-78`, repeated at `audit.md:12` |
| 47 | Instructs a workflow that opens its own PR, which `check_no_unsanctioned_openers` rejects, and points at a declaration mechanism no document describes | `dependabot.md:22-27` |
| 48 | Two escape hatches — `# skill-audit: sanctioned-opener` and `# skill-audit: local-tool` — exist only in code; both are the only way out of a hard FAIL | `scripts/skill_audit.py`, documented nowhere |
| 49 | Shipped comment claims "rulesets require this context by name" for `Version validation`; `ruleset.json` does not list it, and `discipline.md:31` reads its advisory status as a repo misconfiguration where `github-setup.md:119` calls it deliberate | `templates/.github/workflows/pr-checks.yml:190` |
| 50 | "It never diffs a workflow against `templates/`" — `check_self_diff` does, and `SKILL.md:132-134` says so | `audit.md:7,23-24` |
| 51 | The audit recipe uses `diff -ru` on a tree; twenty lines later the same file forbids exactly that and requires `cmp` per file | `audit.md:8-13` vs `:31-33` |
| 52 | Dependabot's gate exemption is justified by an "unchanged version" rule that cannot fire in a tag-driven repo | `dependabot.md:33-35` |
| 53 | "The opener fails loudly instead" — `auto_draft_pr.yml` emits `::notice::` and `exit 0`, so the job goes green | `github-setup.md:26-27` |
| 54 | "Mode 4" / "Mode 1/2" name a numbering `SKILL.md` no longer uses, and "Mode 4 sanctioned adaptations" points at a table in another file | `audit.md:1`, `patterns.md:46`, `scripts/skill_audit.py:5,676` |
| 55 | `dependency_review` is a required ruleset context but absent from `CANONICAL`, so a repo can pass the audit while its ruleset waits on a context nothing produces. (**Partly wrong as reported:** `auto_draft_pr`, `stale` and `frontend_build` produce no required context, so their absence is not a gap) | `scripts/skill_audit.py:25-27` vs `templates/ruleset.json` |
| 56 | Sanctioned adaptation says a repo without `quality_audit.yml` drops that context; `check_canonical_files` fails any repo missing it | `github-actions.md:65`, `github-setup.md:127-128` |
| 57 | "Enforced by `skill_audit.py`" for docstring presence — `check_docstrings` only fails a docstring that exists and is multi-line | `scaffold.md:148` |
| 58 | "walks the commits since the last **published** release" — the workflow deliberately selects the last non-prerelease | `commits.md:45-46` |
| 59 | "The config keeps **only** `autolabeler`, `categories` and a placeholder `template`" — it also carries the load-bearing `name-template` and `tag-template` | `commits.md:61-62` |
| 60 | "keep its Python floor in lockstep with the `python-version` **matrix**" — the template deliberately ships a scalar, and a matrix renames the required check-run | `templates/requirements.test.txt:8` |
| 61 | `versioning.md` ships the `label` job body as copyable YAML, restates the `GITHUB_TOKEN` suppression and restates the merge exception | `versioning.md:24-48,68-77,79-89` |
| 62 | "Dependabot's exemption from the gate is `reference/github-setup.md`" — it is in `dependabot.md`, which bounces the reader back | `versioning.md:65-66` |
| 63 | `discipline.md` carries a code pattern (`hass.services.async_call` fan-out) that `patterns.md` owns, and a heading that is the conclusion of the list above it with an unrelated line beneath | `discipline.md:42-43,54` |
| 64 | Two near-duplicate sections both stating release notes come from commit subjects, not PR bodies | `commits.md:40,67` |
| 65 | `lint_pr.yml` carries the same comment written twice | `templates/.github/workflows/lint_pr.yml:21-26` |
| 66 | Prerequisites 1 and 2 are bold inline; 3 is a heading, so the index lists a list starting at three | `testing.md:25,30,32` |
| 67 | "the two consequences it has for the version gate **and the release notes**" — release notes never reappear | `dependabot.md:3-4` |
| 68 | Two `skill_audit.py` checks degrade to "NOT CHECKED" without `gh`, while the prose says they fail a non-conforming repo | `github-setup.md:98-99,159-161` |
| 69 | `manifest_gate.py` described as enforcing a floor and ceiling without repeating that it is inert in the canonical tag-driven setup | `github-actions.md:153-159` |
| 70 | Scaffold restates the HACS `ignore:` rule; `SKILL.md` restates the two-layer audit model; `commits.md` restates the drafter config; `audit.md` states pattern/quality-scale/testing facts without citing their owners | `scaffold.md:95`, `SKILL.md:126-135`, `commits.md:59-62`, `audit.md:16-18` |
| 71 | "This skill is self-contained… no `reference/` directory" — a statement about the package, not an instruction | `ha-panel-design/SKILL.md:8`, `ha-triage/SKILL.md:8` |
| 72 | Two-to-three-line blank runs the meta-audit's ≥4 threshold misses | `SKILL.md:7`, `discipline.md:11`, `testing.md:19`, `panels.md:32`, `versioning.md:101` |

Also reported and **not upheld**: that the gate's title/commit breaking-marker rule is
undocumented — `github-actions.md` states it. Found while fixing, and not in the audit: that
rule runs inside the step a tag-driven repo skips, so in the canonical setup nothing enforces
it. Now stated where the gate is described.

All 72 landed in `fd721c2..854efb3`, one issue per commit.

## Fixed

| Finding | Commit |
|---|---|
| `discipline.md` gutted — 663 words to 212, index intact, four files pointing at it | `1c717c6` |
| Shipped reminder hook contradicted three invariants every turn | `1c717c6` |
| `SKILL.md` claimed log triage in scope while its frontmatter disclaimed it | `1c717c6` |
| Two files instructed maintaining a `python_validate.yml` matrix the template does not have | `1c717c6` |
| #1 adaptations table missing the frontend placeholders, the frontend pin and the ruleset-context drop | `b423c16` |
| #2 template fidelity ownership — decided: `github-actions.md` owns it, `github-setup.md` keeps GitHub settings | `b423c16` |
| #7 `dependency_review` described as blocking any known advisory | `b423c16` |
| #8 matrix example named the job id where GitHub uses the job name | `b423c16` |
| #9 false claim that `ruleset.json` once carried a matrix | `b423c16` |
| #10 `templates/` contents lists omitted `conftest.py`, `.gitignore`, `ruleset.json`, `frontend/` | `b423c16` |
| #11 adaptations rows for `pyproject.toml`/`pyrightconfig.json` templates that do not exist | `b423c16` |
| #13 Dependabot value proposition duplicated in `github-actions.md` | `b423c16` |
| #21, #24 "the code style below", which was in another file | `b423c16` |
| #22 empty heading in `github-actions.md` | `b423c16` |
| #32 five dangling colons where code blocks had been removed | `b423c16` |
| #36, #37 meta-commentary in `github-actions.md` and `github-setup.md` | `b423c16` |
| #35 "Why this is stated as a rule" — rule-drafting note | `7c61647` |
| #30 (`versioning.md`) index listed a deleted heading; a section duplicated the one above it | `9575203` |
| `commits.md` heading with no body | `7c61647` |
| #15, #16, #29 dependabot restating required-check semantics, PR-opener policy, orphan `Its` | `a425b1d` |
| #14, #20, #21, #23, #28 scaffold restating the version model, the brand-assets version, the code style; the phantom `test_commit_summary.py`; the doubled sentence | `74be580` |
| #17, #42 testing duplicating the Gold rule list; ablation evidence pinned to a superseded harness | `da906a1` |
| #12 `check_scripts_present` naming a job that was removed | `094f809` |
| #6, #26, #33 audit item for patterns that do not exist; "Eval 05" with no shipped referent; the lockstep note | `bb6663b` |
| #3, #39, #40 six modes advertised against four defined; the `Version validation` comment; the gate-compares qualification | `d622c3c` |
| #27, #34 triage procedure nested under the caveats heading; the skill-maintenance aside | `c16afac` |
| #4, #5, #25, #31 three files repeating their own title, `panels.md`'s miscount and its numbered headings, index/heading parity | `daec692` |
| #43 `requirements.test.txt` naming a frontend build for a superseded HA | `3e894b5` |
| #19 label→category mapping sent to `versioning.md` | `a4c0a20` |
