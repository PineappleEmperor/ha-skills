# Schema for skill files

Repo-local. Decides the **shape** of what a skill file says. Which file owns which topic is
`docs/skill-file-hierarchy.md`; this is the other half, and it was missing until 2026-09-20.

**Core rule:** every block is a labelled field or a table row. Unlabelled prose is a defect.

Derived by reading the `home-assistant-best-practices` skill served by the `ha` MCP server —
`SKILL.md` and `references/safe-refactoring.md` — which is the format this repo was asked to
match and did not.

## Why the shape is the fix

| Failure | Cause | What the schema removes |
|---|---|---|
| The 2026.9 refresh took four review rounds | facts written as prose, so reviews spent themselves on interpretation rather than facts | a fact in a cell is wrong about a release number or it is not wrong |
| `pending_release` was invented mid-build and broke `patterns.md` | design reasoning had somewhere to live in the file being edited | no field accepts it, so it goes to the rationale doc or nowhere |
| A `freshness.md` row lists five files that hold the same number | the ledger records duplication instead of the schema forbidding it | a long consumers list is a defect to fix, not a fact to maintain |

## Files, by when they are read

Not by what they are. The reader's trigger is what decides where a fact goes, and it is what
the signposting has to answer. Signposting is layered on purpose: nobody finds a pattern by
reading every pattern.

| Read when | File | Answers | Ships |
|---|---|---|---|
| deciding | `SKILL.md` | should I act, and where do I go | yes |
| doing | `reference/<topic>.md` | what shape does this take | yes |
| checking currency | `reference/freshness.md` | is this value still true, and what moves with it | yes |
| maintaining | `docs/*.md` | why it is this way, what is still wrong | no |

## `SKILL.md` — section order, fixed

| # | Section | Form |
|---|---|---|
| 1 | frontmatter | `name`; `description` as TRIGGER and SYMPTOMS bullet lists, never a prose blob |
| 2 | core principle | one bold line |
| 3 | signpost | mermaid flowchart: task → file |
| 4 | decision workflow | numbered gates; gate 0 is "read X first" when one exists |
| 5 | anti-patterns | the anti-pattern table |
| 6 | reference files | the reference table |

## A task file — section order, fixed

| # | Section | Form |
|---|---|---|
| 1 | scope | one line: when the reader opens this file |
| 2 | core rule | one bold line |
| 3 | contents | numbered, one line per `##`/`###`, when the file has more than three sections; the anchors are added in the pointer pass, not at conversion |
| 4 | the procedure | `### Step N:` — the generic path, once |
| 5 | cases | `## Cases`, then `### <case> — Step N` per case |

**A section that is only pointers is a reference table**, not a procedure and not a case —
`github-setup.md`'s *Supply chain* is five pointers and one fact, and `file | when to read`
is what that shape is for.

**A case is a heading, not a bold label.** The reference implementation labels its deltas in
bold (`**Device-sibling discovery (Step 1):**`), and that is the one place we deliberately
diverge: a pointer must name a heading that exists verbatim, and nothing can anchor to a
bold line. `freshness.md` already carries a pointer at a bold line in
`ha-panel-design/SKILL.md` that resolves to nothing, which is the failure this avoids.

**A table belongs inside the step or case it qualifies**, never in a section of its own. The
reference implementation does this throughout — its *Search ALL consumers* step carries the
table of where to search, because the table is how that step is carried out.

**A file may hold more than one procedure**, but only when `docs/skill-file-hierarchy.md`
assigns it more than one topic — `discipline.md` owns merge behaviour and debugging
behaviour, which are unrelated and must not share a numbering. Each topic takes its own `##`
with its own `### Step 1:`, and a case names which one it attaches to (`— merge Step 2`).
The file's core rule is the primary topic's; a second topic states its own rule as the bold
line opening its section.

## Canonical tables

Fixed column sets. A table that invents its own shape cannot be diffed across a refresh.

| Table | Columns |
|---|---|
| anti-pattern | `anti-pattern \| use instead \| why (one clause) \| reference` |
| rebuttal | the anti-pattern table — an excuse *is* an anti-pattern, its rebuttal splits into *use instead* and *why* |
| scheduled change | `what \| lands in \| do now \| do then` |
| reference | `file \| when to read` |
| source | `artefact \| taken from` — what a scaffold carries and where each piece comes from |
| tier | `tier \| adds` — a level and what it requires beyond the one below |
| cached fact | `fact \| value \| captured \| re-derive with \| consumers \| gate` |
| decision | `scenario \| choice` |

A table whose columns fit none of these is a finding, not a licence to invent one — but a
table degraded into a bullet list is a loss, so report it and the set gains a row. The
`source` and `tier` shapes were added exactly that way, after three tables in
`github-actions.md` and `quality-scale.md` were flattened for want of them.

**A single-column enumeration is a bullet list, not a table.** The eight required contexts
are eight names; a second column exists only if this file knows what goes in it, and
`github-setup.md` knows the producing workflow for two of the eight. A column padded with
what another file owns is a restatement waiting to drift.

In a file with two procedures, the anti-pattern table's `reference` column names the topic
as well as the step — `commit Step 2`, `PR body Step 3` — matching the case-heading form.

## Block types, and the only cases that earn one

| Block | Written as | Earned when |
|---|---|---|
| row | a table line | always the default |
| substitution | `X` → `Y` on one line | a swap with no conditions |
| bullet list | `- ` per line | every bullet is one fact or one substitution; a bullet that runs to a paragraph is prose wearing a dash |
| ordered list | `1.` per line | a sequence inside a single step, where the order is load-bearing but each item is too small to be a step of its own |
| lead-in label | `**<label>:**` on the line above a list | the list needs a name to be read — the reference implementation labels every delta this way |
| numbered steps | `### Step N:` | order is load-bearing — doing 3 before 2 breaks it |
| code block | fenced | the reader copies it |
| mermaid | fenced ```mermaid | a branch a reader must navigate, not a sequence they follow |
| `**Symptom:**` | one line | the failure misattributes its own cause |
| `**Timing:**` | one line | the change must happen before or after some other event |
| `**Fix:**` | one line | there is a fix path, or there is provably none |
| `> **Note:**` | blockquote, ≤ 3 lines | a caveat that changes the action in one case |

Anything not on this list is not a block. If a fact will not fit one, it is either in the
wrong file (`docs/skill-file-hierarchy.md`) or it is rationale.

## Cached facts

| Rule | Value |
|---|---|
| when a row exists | only where the duplication is unavoidable — a different tool's config schema, or a different repository |
| anywhere else | the duplicate is deleted, not tracked |
| the `gate` column | names the check that keeps the copies in step, or says `none` |

A row with no gate is where drift happens, and it already has: the harness pin reads
`0.13.365` in the template and `0.13.364` in the only repository that runs it, and the 54
quality-scale rules match `TIER_RULES` today with nothing asserting that they still will.
Writing `none` in that column is what turns an unavoidable duplication into a known one.

## Pointers

| Rule | Value |
|---|---|
| form | `[<file> #<heading>](path#slug)` |
| the heading | must exist verbatim in the target |
| what a pointer never does | restate the fact it points at |

## What a release changes

A refresh has three outcomes. Only the first is an edit; the schema must hold the other two
or they are rediscovered every month.

| Outcome | Lands as |
|---|---|
| changed or removed | edit the row it invalidates |
| new capability | a new row in the file that owns the topic |
| announced for a future release | a row in the scheduled-change table, cleared when it lands |

There is no release-history table. A reader acts on the current rule, never on when it
changed; the release is a clause in the row — "removed in 2026.3, use `color_temp_kelvin`".

## What never appears in a skill file

| Not this | What happens to it |
|---|---|
| why a rule was chosen over an alternative | deleted — the commit that introduced the rule is the record |
| what a past pass got wrong | deleted — git holds it |
| rhetoric, exhortation, framing | deleted |
| evidence for a fact | becomes a re-derivation command in `reference/freshness.md`, or is deleted |
| a problem that is still open | one row in `docs/backlog.md` |

**The test:** if knowing it does not change an action, it is not in a skill file.

Nothing on that list is relocated except an open problem. A destination for rationale is a
filing system for text nobody reads, and it grows at the rate the skill is edited —
`docs/ha-integration-change-rationale.md` reached 1,340 lines that way, organised by the
pass that wrote them rather than by the rule they explain.
