# From the post-fix independent audit (2026-08-26) — all fixed

Closed rows, moved here from the register when they cleared. Formatting may be repaired; a
claim later found false gets a new row in the register rather than an edit here, so this
stays a transcript that can be checked against git.

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
