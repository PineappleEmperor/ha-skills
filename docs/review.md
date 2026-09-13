# How a review is run

Repo-local. One procedure for every review of this repository and the CI repositories, so
the brief is never rewritten from memory. `docs/backlog.md` owns what happens to a finding
once it is a row; `docs/skill-file-hierarchy.md` owns which skill file owns which topic.
This file owns only the review itself.

## The three kinds

| Kind | When | Scope the reviewer is given | What it reports |
|---|---|---|---|
| **Diff review** | Before every push is handed over | The diff since the last pushed commit, and the register rows the diff claims to close | A row whose claim the diff does not bear out; an invariant below that the diff breaks |
| **Single-source sweep** | After any pass that touched more than one prose file, and on request | Every shipped file, read in full, against the hierarchy and the three CI READMEs | A fact stated in two places (both locations); a fact stated outside its owner; a pointer whose target file or heading does not exist |
| **Purpose audit** | On request, when the shape of the plugin is in question | Every file, read in full, against the goal each `SKILL.md` states in its `description` and the three tiers in the hierarchy | A file or section that serves no task a reader opens it for; two files serving the same one |

Eval scenarios under `plugins/ha/skills/ha-integration/evals/` are a fourth thing with
their own README and are not reviews.

## Invariants every kind checks

1. **Each register row's claim holds.** The Fix column describes what the diff does, and the
   Commit column names hashes that exist and touch only what the row names.
2. **One fact, one source**, the rule *The rule* in `docs/skill-file-hierarchy.md` states. Checked as: a
   restatement is deleted, never synced; a pointer names the owning file and the heading
   verbatim; the target exists.
3. **Copies match their source**, checked the way the first item under *Judgement
   checklist (read the code — a grep can't decide these)* in
   `plugins/ha/skills/ha-integration/reference/audit.md` says.
4. **Commit subjects** meet *Keep messages short* in
   `plugins/ha/skills/ha-integration/reference/commits.md`, and each subject covers the
   whole diff of its commit.
5. **No AI attribution.** The rule is *No AI-attribution trailers* in
   `plugins/ha/skills/ha-integration/reference/commits.md`; the review checks PR bodies,
   comments and docs for the same.
6. **A sentence about code is checked against the code.** "The audit fails a repo that…"
   is read against the check that would fail it, in the repository that owns it.
7. **The `[marketplace-repo]` hook's rule holds under `plugins/`**; the hook, in
   `.claude/settings.json`, states it. The one exception is the evals directory, which its
   README says is maintenance of the skill and not copied into a scaffold (row 203).

## Protocol

1. **The reviewer is context-free.** The `reviewer` agent in `.claude/agents/`, a fresh
   subagent with no access to the session, given the kind, the scope and nothing else.
   It reads every file it judges in full and never searches to verify.
2. **Discrepancies only, with `file:line`.** One line per finding: the location, the claim,
   what the file actually says. No praise, no fixes, no suggestions.
3. **Every finding is verified against the file before it is recorded.** A finding that
   does not survive is recorded as not upheld, with the reason.
4. **An upheld finding is a register row before it is a fix.** From there the row's life is
   `docs/backlog.md`'s header.
5. **Re-run the same kind over the new diff until a pass returns nothing.** The closing row
   records the passes and the count from each.
6. **The closing report** says, in this order: what was found per pass, which rows closed and
   in which commits, which rows remain open, and a `## Your turn` table for the push or the
   merge. A push whose PR opener is still queued is still a hand-over.

## What has gone wrong before

- A context-free reviewer found seven discrepancies on 2026-09-04
  (`docs/backlog/2026-09-04-review-84-90.md`) and, on 2026-09-10, three that self-review
  had passed (row 176).
- Two findings reported on 2026-08-26 did not survive verification
  (`docs/backlog/2026-08-26-post-fix-audit.md`); a reviewer's word is a claim too.
- Hiding files does not withhold guidance, as `plugins/ha/skills/ha-integration/evals/README.md`
  records for the control arm; a context-free reviewer is told what it may not read.
- A brief paraphrased from memory drops an invariant; the brief is this file, quoted.
- A patch the gate had refused was recorded as done, seven times in one pass (row 200); a
  Fix column is checked against the file, not the intent.
- The first review under this file found eight things, five of them in this file: four
  claims a named source does not make and one restatement (row 202); the standard is
  reviewed like anything else.
