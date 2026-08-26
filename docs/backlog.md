# Backlog

Findings only. **Nothing here is edited during an audit** — an audit adds rows, a later
fix pass clears them, one issue per commit. New findings discovered while fixing are added
here rather than fixed inline.

Status: `open` · `fixed` (with commit) · `wontfix` (with reason).

## Open

| # | Finding | Where |
|---|---|---|
| 18 | Drafter config contents and "why not `$CHANGES`" — `github-actions.md` owns the drafter | breach in `commits.md:54-62` |
| 41 | Gate enforces title/commit breaking-marker agreement; documented nowhere | `test_manifest_gate.py` |

Rows 1-17, 19-40, 42-43 are cleared — see *Fixed*. Anything the post-fix independent
audit turns up is added below as a new numbered row, not merged into an old one.

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
