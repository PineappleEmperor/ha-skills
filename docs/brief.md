# How a build brief is written

Repo-local. Every agent that changes a file in this repository or a CI repository is given a
brief in this shape, and nothing else. `scripts/brief_gate.py` refuses the dispatch when the
brief is missing, malformed, or has not passed its case review. `docs/review.md` owns
reviews of the work; this file owns the instructions that produce it.

## Why it exists

On 2026-09-28 five of seven defects a review found were written into the builder's brief:
each finding was turned into a one-line patch without reading the code around it or core's
version of it. The builder applied the patch, tested the case it was given, and the next
review found the siblings. The thinking happened after the building. This shape puts it
first, and the case review checks it before anything is built.

## Where a brief lives

`.tmp/briefs/<slug>.md` in this repository, whichever repository the work is in. The agent's
prompt is the line `Brief: .tmp/briefs/<slug>.md` and nothing that contradicts it.

## The sections, in this order

Every heading below is a `##` heading in the brief, spelt as here.

| Section | Holds | Refused when |
|---|---|---|
| `Goal` | What the user gets, in one to three sentences, in the user's terms | empty |
| `Repository` | The absolute path and the branch | no absolute path |
| `Sources read` | One bullet per file read before writing the brief — a repository path, or a core URL at a tag — each ending `(in full)` | empty, or a bullet without `(in full)`; the brief mentions core and no bullet names a core tag |
| `Defect class` | The rule that is broken, stated for every input it applies to, not for the reported one | empty |
| `Rules applied` | A table with columns `Rule`, `Applies`, `How the plan meets it` — below | a row missing, `Applies` other than `yes` or `no`, or `How` empty |
| `Cases` | A table with columns `#`, `Kind`, `Situation`, `Expected`, `Proof` | fewer than three rows; no row of each kind |
| `Single source` | A table with columns `Fact`, `Owner`, `Pointers`, one row per fact the change introduces or moves; or the line `No fact introduced or moved.` | neither |
| `Files` | Every file the change is expected to touch | empty |
| `Out of scope` | What must not change, and why | empty |
| `Commits` | One planned subject per decision | empty |
| `Checks` | The commands run after every commit, in a fenced block | no fenced block |
| `Stop and report if` | The conditions under which the builder stops instead of improvising | empty |

### The rules table

The rules a review holds the work to are answered here, before anything is written. A
finding a review would make from a rule it already has is a planning defect.

| Row | Required when | `How the plan meets it` says |
|---|---|---|
| `Invariant <n>` | always, one per invariant under *Invariants every kind checks* in `docs/review.md`; the gate reads that list, so a new invariant binds every brief | for `yes`, what in the plan satisfies it — the owner, the source compared, the commit split; for `no`, why the change cannot touch it |
| `Anti-patterns: <path>` | for every skill document under `Files` | which of that file's anti-pattern rows and rules the change meets, or that none bears on it |

Further rows are welcome — a `docs/skill-schema.md` block type, a `reference/commits.md`
step — and are held to the same two columns.

### Case kinds

| Kind | Means | Example |
|---|---|---|
| `reported` | the instance the finding or request named | a 404 for a mistyped tag stops at once |
| `sibling` | another input in the same class, which the reported one does not cover | a 503 is retried; a nested `tests/sub/` without `__init__.py` fails the step |
| `guard` | something that must keep working, or keep failing, after the change | `import async_timeout` in a test still fails ruff |

`Proof` names the test that shows the case — a test function, or a command and its
expected output. A documentation case is proved by the line that states it.

### The single-source table

`Owner` is the one file, and heading, that states the fact. `Pointers` lists every other
file that mentions it, each of which only points. A fact with two owners is the defect this
table exists to catch before it is written; `docs/skill-file-hierarchy.md` says which file
owns which topic.

## The case review

Before any builder is dispatched, a `reviewer` agent is given the brief and the files it
lists under `Sources read`, and answers two questions: is a case missing, and does any
`Rules applied` row claim something the plan does not do? It writes
`.tmp/briefs/<slug>.review` holding the brief's sha256 on the first line and
`VERDICT: complete` or `VERDICT: missing` on the second, with the missing cases after it.

The gate accepts a brief only when that file exists, names the brief's current sha256, and
says `complete`. Editing a brief after its review invalidates the review.

## Standing rules every builder follows

These are not repeated in a brief; the brief's prompt line makes this file part of it.

- Governed files are written only through the governance gate of the repository they are
  in: `get_docs`, then `get_file`, then `patch_file`.
- Every file changed is read in full first. Shell search is blocked; locate with the gate.
- A case's test is written first and seen to fail before the change that passes it.
- Subject-only Conventional Commits, one decision per commit, no AI attribution; the
  detail is `plugins/ha/skills/ha-integration/reference/commits.md`.
- Nothing is pushed, amended or rebased.
- Scratch goes in `.tmp/` of the repository being changed.

## The report

The builder reports, per case: the commit, the proof, and what the proof showed before the
change. A case it could not meet is reported as unmet with the reason — never dropped. Then
anything it changed outside `Files`, and the last line of every command under `Checks`.
