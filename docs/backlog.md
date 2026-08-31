# Backlog

Findings only. **Nothing here is edited during an audit** — an audit adds rows, a later
fix pass clears them, one issue per commit. New findings discovered while fixing are added
here rather than fixed inline.

Status: `open` · `fixed` (with commit) · `wontfix` (with reason).

## Open

| # | Finding | Where |
|---|---|---|
| 73 | `title-check` runs the workflow from the base branch **head** but checks out `ref: base.sha`, the base commit frozen at PR creation. A PR opened before a `scripts/` change merges therefore runs the NEW workflow against the OLD script: observed on `ha-ci-testing` #9, where the gate died with `commit_summary.py: error: argument --mode: invalid choice: 'label'` (exit 2) instead of reporting the label mismatch it exists to report. The check-run is red either way, so the failure is silent in the rollup and misleading in the log. `base.ref` would keep the tree consistent with the workflow and is equally safe — both are base-side, neither is PR-author code. `check_pr_checks_shape` currently *requires* `base.sha`, so the audit and its test change with it | `templates/.github/workflows/pr-checks.yml:93`, `.github/workflows/pr-checks.yml:93`, `scripts/skill_audit.py` `check_pr_checks_shape` |

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
