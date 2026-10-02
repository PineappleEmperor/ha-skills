# 06 — Router selection (KAT)

Known-answer test for the split introduced when SKILL.md became a router: does an agent
reach the right skill, and then the right reference file, without reading everything?

## Setup

No fixture. The agent needs read access to `plugins/ha/skills/` — both skills.

## Prompt

> For EACH request below, decide which single skill you would load, then open that
> skill's SKILL.md and state exactly which reference file you would read next before
> doing any work. Do not do the work.
>
> A. "Every entity of my integration went unavailable after the device's firmware update,
> and the log says `Unexpected error fetching` — what's actually wrong?"
> B. "Add a reconfigure flow so users can change the host without deleting the entry."
> C. "The panel I serve looks wrong in dark mode — tiny headings, hardcoded colours."
> D. "Set up the release process for my new integration repo."
> E. "Write a test that the config entry sets up successfully."
>
> Report a table: request → skill → next reference file → the sentence that led you
> there. Then name any request where routing was ambiguous or you had to guess.

## Pass

| Request | Skill | What to read next |
|---|---|---|
| A | `ha-triage` | `ha-integration/reference/patterns.md`, from the Unexpected reply row; naming its case *A reply the code does not expect — Step 1* as well is correct |
| B | `ha-integration` | `reference/patterns.md` |
| C | `ha-integration` | `reference/panel-design.md`, from the Panel design row, plus the Material 3 / HA theming sources it names |
| D | `ha-integration` | `reference/scaffold.md`, from the Scaffold row. Also correct: `reference/versioning.md` from the Release row, for an answer that reads the repository as already released |
| E | `ha-integration` | `reference/testing.md` |

Each answer must cite a sentence from the skill, not an inference. **An answer reached
"by elimination" is a routing failure even when the destination is right** — it means the
router did not say it, and the next reader may eliminate differently.

⚠️ **"No `reference/` directory" is not "nothing else to read".** `ha-triage` carries no
reference layer of its own: every fault class in its table names a file of
`ha-integration`. An
answer for A that stops at the triage file, or names the class without the file that owns
the fix, is a fail.

**E is the deliberate edge case.** Testing rules used to sit in `patterns.md` and moved to
`testing.md` when the skill split; the mode table is the only thing that now distinguishes
them. An answer of `patterns.md` means the router's Test row was not read.

## Fail

Any request routed to a skill whose frontmatter disclaims it; any reference file named
that does not exist; reading more than three reference files to answer.
