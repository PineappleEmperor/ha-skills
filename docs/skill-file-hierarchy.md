# File hierarchy for the ha-integration skill

Repo-local. Decides which file owns which topic, so a fact has one home and every other
file points at it. Derived by counting where each topic is actually discussed, then
resolving each conflict deliberately — not by guessing intent.

## The rule

**A file owns a topic when it is the file a reader opens *for that task*.** Not the file
that mentions it most, and not the file where it is most interesting. Everything else
links.

Three tiers:

1. **SKILL.md** — routes. Owns the mode table — whose shape, and that it is the reference
   map as well, is *`SKILL.md` — section order, fixed* in `docs/skill-schema.md` — and the
   commands of a mode no reference file holds. It carries no anti-pattern table, for the
   reason *Anti-patterns, and where they live* in `docs/skill-schema.md` gives. Any fact
   stated here is stated *only* here.
2. **Task files** — one per trigger. Own their topic outright, including every anti-pattern
   for that topic.
3. **The currency ledger** (`freshness.md`) — owns the values the skill copies from outside
   itself and must keep in step with their source: the Home Assistant release it is written
   for, the Python floor, the harness pin, the action versions, the revision of an external
   spec it was read against. Each row carries when the value was captured, the command that
   re-derives it, the files that hold a copy, and the check that keeps the copies in step. A
   reader opens it to ask whether the skill is still current, and what moves if it is not.
   A task file cites a row; where a file has to hold the value itself — a config file's
   schema, a release read at a tag — the row lists it as a consumer. A fact read from core
   and stated once in its owning file needs no row.

## Ownership

| Topic | Owner | Why that file, and who defers |
|---|---|---|
| version model, labels, semver | `versioning.md` | The reader is cutting or gating a release. `commits.md`, `scaffold.md`, `audit.md` link. |
| commit subjects, PR body | `commits.md` | The reader is writing a commit. `discipline.md` keeps the *behaviour* (what to do under pressure), not the format. |
| what the release notes are built from | `commits.md` | It is a consequence of commit discipline. `github-actions.md` describes the workflow that runs it; `versioning.md` links. |
| repo setup on GitHub: token, required checks, ruleset, dependency graph | `github-setup.md` | The reader is configuring a repo. `discipline.md` and `versioning.md` link. |
| workflow contracts — what each must do and must not | `github-actions.md` | The reader is reviewing a workflow. Owns template fidelity, since that is a workflow-review concern. |
| PR openers | `github-actions.md` | It is a workflow contract. `github-setup.md` owns only the *token* the opener needs. |
| merge under a red check, and tracing before naming a root cause | `discipline.md` | Two behavioural rules with no artefact of their own. Everything about *format* left for `commits.md`; ruleset config is `github-setup.md`. |
| test harness prerequisites, mocking | `testing.md` | The reader is writing a test. `scaffold.md` lists the files and links here for why. |
| code patterns, typing, file structure | `patterns.md` | The canonical lookup for code inside `custom_components/`: pattern → rule → copyable snippet. Other files cite it; none restate it. |
| building a panel-serving integration — registration, the committed bundle, staleness, the frontend pin, websocket backing | `panels.md` | The reader is building or fixing a panel integration. `patterns.md` states the general async-setup race rule and points here for the panel code. |
| quality scale rules and evidence | `quality-scale.md` | The reader is claiming a tier. |
| Dependabot: ecosystems, grouping, floors, exemption | `dependabot.md` | The reader is configuring or debugging Dependabot. `versioning.md` and `github-setup.md` link. |
| scaffolding: what to ask, what to generate | `scaffold.md` | The reader is starting a repo. |
| `manifest.json` — its keys, what each requires, their order | `scaffold.md` | The manifest is written at scaffold time and its rules do not change after; a later key change reads the same step. `patterns.md` and `SKILL.md`'s Manifest row point here. |
| audit procedure — the judgement items | `audit.md` | The reader is auditing. Owns no facts of its own; it cites the owners. |
| the skill's currency — the values it copies from outside itself, each with its capture date, re-derivation command, the files holding a copy, and the check that keeps them in step | `freshness.md` | The reader is asking whether the skill is still current. A task file cites the row; a file that must hold the value is listed as its consumer. |
| how a panel looks — type scale, theme tokens, spacing, touch targets, disclosure | `panel-design.md` | The reader is changing a panel's CSS or markup. `panels.md` and `SKILL.md`'s Panel design row point here; it points at `panels.md` for the bundle. |

## Conflicts found, and how each was resolved

| Topic | Split | Resolution |
|---|---|---|
| panel | `panels.md` 28 · `patterns.md` 23 | panels.md owns delivery; patterns.md keeps the parallel-setup race only |
| Dependabot | 4 files, 8/8/7/3 | dependabot.md owns; the other three link |
| merge rule | `discipline.md` 6 · `github-setup.md` 6 | discipline.md owns the rule; github-setup.md owns the ruleset config |
| commit subjects | `commits.md` 10 · `discipline.md` 7 | commits.md owns format; discipline.md owns behaviour |
| labels | `versioning.md` 16 · `github-actions.md` 8 | versioning.md owns the mapping; github-actions.md owns the job that applies it |
| test harness | `testing.md` 10 · `scaffold.md` 5 | testing.md owns; scaffold.md lists the files and links |

## Why not enforce this with a checker

Tried, reverted. A phrase deny-list is unbounded — "bumped manually" slipped past a list
containing "bump the manifest". Ownership-by-keyword flags legitimate mentions and cannot
tell a restatement from a pointer without reading. The hierarchy is a decision to be
applied by whoever edits, checked in review, not a regex.
