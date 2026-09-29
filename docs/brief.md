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

## What is read before a brief is written

Everything, not a search's hits. The corpus is every shipped text file of the skill, its
evals apart from their result records, the four `docs/` files that govern briefs and
reviews, and the three CI READMEs; `corpus()` in `scripts/brief_gate.py` is the list, and
it is about 5,400 lines. Every local file under `Sources read` is added to it.

`scripts/read_log.py` records each `Read` and governance `get_file` with the file's hash and
whether the whole file was read. The gate passes a brief only when every file in the corpus
was read whole, in the dispatching session, at the content it has now. A slice, a read from
an earlier session, or a file changed since it was read counts as unread. `(in full)` under
`Sources read` is the author's claim; the log is what the gate believes.

## The sections, in this order

Every heading below is a `##` heading in the brief, spelt as here.

| Section | Holds | Refused when |
|---|---|---|
| `Goal` | What the user gets, in one to three sentences, in the user's terms | empty |
| `Repository` | The absolute path and the branch | no absolute path |
| `Sources read` | One bullet per file read before writing the brief — a repository path, or a core URL at a tag — each ending `(in full)` | empty, or a bullet without `(in full)`; the brief mentions core and no bullet names a core tag |
| `Defect class` | The rule that is broken, stated for every input it applies to, not for the reported one | empty |
| `Facts` | A table with columns `ID`, `Fact`, `Owner`, `Pointers` — below | an ID not of the form `F1` to `F99`, or used twice; two rows making the same claim; a row with no owner; a fact no case cites; an ID cited anywhere in the brief that no row defines |
| `Rules applied` | A table with columns `Rule`, `Applies`, `How the plan meets it` — below | a row missing, `Applies` other than `yes` or `no`, or `How` empty |
| `Cases` | A table with columns `#`, `Kind`, `Situation`, `Facts`, `Expected`, `Proof`, `Seen` | fewer than three rows; no row of each kind; a row citing no fact under `Facts`, or with nothing under `Seen`; a `today:` quote no source contains |
| `Files` | Every file the change is expected to touch, a new one marked `(new)` | empty; a file not marked `(new)` that is not under `Sources read` |
| `Out of scope` | What must not change, and why | empty |
| `Commits` | One planned subject per decision | empty |
| `Checks` | The commands run after every commit, in a fenced block | no fenced block |
| `Stop and report if` | The conditions under which the builder stops instead of improvising | empty |

### The rules table

The rules a review holds the work to are answered here, before anything is written. A
finding a review would make from a rule it already has is a planning defect.

| Row | Required when | `How the plan meets it` says |
|---|---|---|
| `Invariant <n>` | always, one per invariant under *Invariants every kind checks* in `docs/review.md`; the gate reads that list, so a new invariant binds every brief | for `yes`, what in the plan satisfies it — the owner, the source compared, the commit split — and every document the invariant names in backticks is under `Sources read`; for `no`, why the change cannot touch it |
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

`Seen` is what the author observed while writing the brief: the Proof run against today's
code, or against a draft in a scratch sample, and what it returned. A case about a tool's
behaviour is an observation, never a prediction written as fact.

What a file says now is written after `today:`, each piece of it in double quotes and
copied from the file: the gate refuses a quote that no local file under `Sources read`
contains, line breaks aside. The `today:` part ends at the first `;` outside quotes, so tool
output observed for the case follows the `;` and is not held to a file.

### The facts table

Every fact the change rests on, introduces or moves is stated here once, as a row with an
ID, and nowhere else in the brief: a rules row or a case cites `F3`, it does not say again
what F3 says. A revision then edits one row, and no stale copy of it can survive elsewhere.

`Owner` is the one file, and heading, that states the fact after the change. `Pointers`
lists every other file that mentions it, each of which only points; a file that states it
in its own words is a second owner, and the defect this table exists to catch before it is
written. `docs/skill-file-hierarchy.md` says which file owns which topic.

The gate checks the table's mechanics: IDs unique and resolving, claims distinct, every fact
owned and proved by a case. Whether a rules or cases cell restates a fact in its own words
instead of citing it is judged in the case review.

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
