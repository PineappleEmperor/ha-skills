# Backlog

Findings only. **Nothing here is edited during an audit** — an audit adds rows, a later
fix pass clears them, one issue per commit. New findings discovered while fixing are added
here rather than fixed inline.

Status: `open` · `fixed` (with commit) · `wontfix` (with reason).

## Open — contradictions a reader would act on

| # | Finding | Where | Notes |
|---|---|---|---|
| 1 | Sanctioned-adaptations table forbids substitutions the skill orders you to make | `github-setup.md:196`, `audit.md:14` vs `panels.md:40,44`, `github-setup.md:150` | `frontend/package.json` ships `<domain>`/`<name>` placeholders; the frontend pin must be uncommented; a repo without `quality_audit.yml` must drop a ruleset context. All three are unlisted, so an auditor reverts working repos |
| 2 | Hierarchy assigns template fidelity to `github-actions.md`; it lives in `github-setup.md` and three files defer there | `skill-file-hierarchy.md:29` | Decide which is right, then make the other match |
| 3 | Shipped `pr-checks.yml` comment claims rulesets require `Version validation` by name | `templates/.github/workflows/pr-checks.yml:196` | Docs correctly say it is deliberately absent |
| 4 | "Three requirements… **Both** verified by ablation… remove **either**" | `testing.md:24` | Count says three, prose says two |
| 5 | "**Three** things are non-obvious" above five numbered items | `panels.md:15` | |

## Open — false claims about code

| # | Finding | Where |
|---|---|---|
| 6 | Audit item tells you to re-derive "stale-pin patterns" that do not exist in `skill_audit.py` | `audit.md:20`, narrated as present tense at `freshness.md:7` |
| 7 | `dependency_review.yml` described as blocking "a known advisory"; it gates `fail-on-severity: high` | `github-actions.md:63` |
| 8 | Matrix example names the job *id* where GitHub uses the job *name* | `github-setup.md:103` |
| 9 | "`templates/ruleset.json` once shipped exactly this bug" — a JSON ruleset cannot carry a matrix | `github-setup.md:106` |
| 10 | Two lists of what `templates/` contains both omit `conftest.py`, `.gitignore`, `ruleset.json`, `frontend/` | `github-actions.md:3`, `github-setup.md:177` |
| 11 | Adaptations table and scaffold list reference `pyproject.toml`/`pyrightconfig.json` templates that do not exist | `github-setup.md:196`, `scaffold.md:64` |
| 12 | `check_scripts_present` justifies `commit_summary.py` by a `commit-summary` job that was removed | `scripts/skill_audit.py` |

## Open — ownership breaches (content in the wrong file)

| # | Finding | Owner per hierarchy |
|---|---|---|
| 13 | Dependabot value proposition restated | `dependabot.md` — breach in `github-actions.md:95` |
| 14 | Tag-driven version model restated in a blockquote | `versioning.md` — breach in `scaffold.md:57` |
| 15 | Required-check semantics restated | `github-setup.md` — breach in `dependabot.md:24` |
| 16 | PR-opener policy set | `github-actions.md` — breach in `dependabot.md:18` |
| 17 | Gold per-rule behavioural-test list duplicated in full | `quality-scale.md` — breach in `testing.md:75` |
| 18 | Drafter config contents and "why not `$CHANGES`" | `github-actions.md` — breach in `commits.md:56` |
| 19 | Label→category mapping | `versioning.md` — breach in `commits.md:44` |
| 20 | Brand-assets HA version restated instead of cited | `freshness.md` — breach in `scaffold.md:84` |
| 21 | Code style section | `patterns.md` — breach in `scaffold.md:145`, compounded by "the code style **below**" at `github-setup.md:210` |

## Open — navigation and corruption

| # | Finding | Where |
|---|---|---|
| 22 | Empty heading, no body | `github-actions.md:25` |
| 23 | Points at a `test_commit_summary.py` description that exists nowhere | `scaffold.md:68` |
| 24 | "The code style **below**" — it is in another file | `github-setup.md:210` |
| 25 | Headings missing from their file's index | `github-actions.md:53,98`, `github-setup.md:179,192`, `versioning.md:101`, `panels.md:62` |
| 26 | Cites "Eval 05" — `evals/` is not shipped, so the reader has no referent | `audit.md:27,33` |
| 27 | Steps 1-4 (the whole procedure) nested under `## Cached facts` | `ha-triage/SKILL.md:35` |
| 28 | Same sentence twice in one blockquote | `scaffold.md:60,62` |
| 29 | Section body opens with the orphan word `Its` | `dependabot.md:30` |
| 30 | Four-plus blank lines | `github-actions.md:16`, `versioning.md:14` |
| 31 | Headings duplicating their own H1 | `quality-scale.md:10`, `freshness.md:5`, `panels.md:13` |
| 32 | Dangling colons where code blocks were removed | `github-actions.md:91,93,102,104,106` |

## Open — meta-commentary (about writing skills, not doing the task)

| # | Where |
|---|---|
| 33 | `audit.md:40` "Keep the gate in lockstep" — instruction to the skill's maintainer, inside a repo auditor's checklist |
| 34 | `ha-triage/SKILL.md:124` "Don't add a home's specific errors to this skill" |
| 35 | `commits.md:95` "Why this is stated as a rule" |
| 36 | `github-actions.md:120` "These templates are a dependency other repos inherit…" |
| 37 | `github-setup.md:207` "Traps this section exists to close" |
| 38 | `SKILL.md:122,127`, `github-actions.md:21`, `audit.md:3` — milder, same shape |

## Open — other

| # | Finding | Where |
|---|---|---|
| 39 | Six modes advertised, four defined; Test and Release/repo setup have no numbered section | `SKILL.md:32` |
| 40 | Docs say the gate checks existence not content; `check_self_diff` and `check_template_pins` do compare | `SKILL.md:134`, `audit.md:7` |
| 41 | Gate enforces title/commit breaking-marker agreement; documented nowhere | `test_manifest_gate.py` |
| 42 | Ablation evidence pinned to HA 2026.8.0 / p-h-c-c 0.13.354 while the shipped pin is 0.13.357 → 2026.8.3 | `testing.md:24` |
| 43 | `requirements.test.txt` comment names a frontend build for HA 2026.8.0 under a pin for 2026.8.3 | `templates/requirements.test.txt` |

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
| `versioning.md` index listed a deleted heading; a section duplicated the one above it | `9575203` |
| `commits.md` heading with no body | `7c61647` |

## Uncommitted work in progress

`check_document_integrity` in `skill_meta_audit.py`, plus repairs to `commits.md`,
`testing.md`, `versioning.md`, `discipline.md`, `dependabot.md`, `github-setup.md`.
Four integrity findings were fixed; the remainder are rows above.
