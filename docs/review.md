# How a review is run

Repo-local. One procedure for every review of this repository and the CI repositories, so
the brief is never rewritten from memory. `docs/backlog.md` owns what happens to a finding
once it is a row; `docs/skill-file-hierarchy.md` owns which skill file owns which topic.
This file owns only the review itself.

## The three kinds

| Kind | When | Scope the reviewer is given | What it reports |
|---|---|---|---|
| **Diff review** | After every file pass, and before every push is handed over | The diff since the last review, the register rows the diff claims to close, and every shipped file the diff touches read in full | A row whose claim the diff does not bear out; an invariant below that the diff breaks |
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
3. **Copies match their source**, checked the way *Step 1: Callers, not bodies; copies, not
   paraphrases* in `plugins/ha/skills/ha-integration/reference/audit.md` says.
4. **One decision per commit.** The subject meets *Step 2: Write the subject in the
   Conventional Commits form* and *Step 3: Stop at the subject* in
   `plugins/ha/skills/ha-integration/reference/commits.md` and names the decision the
   commit makes; every hunk in the commit serves that decision, whichever files it touches.
   A commit is not split by file, and a subject that names one file of a four-file decision
   is the defect, not the four files.
5. **No AI attribution.** The rule is *Step 4: Carry no AI-attribution trailer* in
   `plugins/ha/skills/ha-integration/reference/commits.md`; the review checks PR bodies,
   comments and docs for the same.
6. **A sentence about code is checked against the code.** "The audit fails a repo that…"
   is read against the check that would fail it, in the repository that owns it.
7. **The `[marketplace-repo]` hook's rule holds under `plugins/`**; the hook, in
   `.claude/settings.json`, states it. The one exception is the evals directory, which its
   README says is maintenance of the skill and not copied into a scaffold (row 203).
8. **Every Home Assistant release number stated in a skill file is read back from core**, at
   the `.0` tag of the release the release row of
   `plugins/ha/skills/ha-integration/reference/freshness.md` names —
   `raw.githubusercontent.com/home-assistant/core/<tag>/…`. A deprecation deadline
   is quoted from the `breaks_in_ha_version` of the call site it describes, one per API, not
   summarised across a group of them.
9. **A rewrite is lossless.** Where a diff changes the *shape* of a passage — prose into a
   table, a bullet into a row, a block retitled — every fact the previous version stated is
   in the new one, or was deleted deliberately and named as deleted in the register. Checked
   against `git show <base>:<path>`, clause by clause, not by reading the new file alone: a
   deletion makes a structural audit greener, so nothing mechanical objects to it.
10. **Every shipped file has the shape `docs/skill-schema.md` gives it**, read section by
    section: the section order for its kind, every block one of the *Block types, and the
    only cases that earn one*, every
    table a canonical column set, no anti-pattern table in a router and every anti-pattern
    in the file that owns its topic with a `reference` cell naming where the rule was read
    or observed, a mode row for every action that has a file and naming only its entry
    file, and a pointer in the *Pointers* form. `scripts/skill_schema_audit.py` measures runs, columns and numbering; everything
    else in that document is a reading.

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
5. **One review per file pass, and its findings go to the author with a verdict on each
   before anything else moves.** A re-run happens only when a shipped file changed in
   response to a finding; a diff that touches only the register or a commit subject is
   checked by the author, not by another dispatch. Four passes over one register diff on
   2026-09-25 cost 265k, 160k, 144k and 143k subagent tokens, and the last three returned
   only wording, which is what this rule stops. The closing row records the passes and the
   count from each.
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
- Four review rounds over the 2026.9 refresh passed a deadline of `2027.10` that appears
  nowhere in `homeassistant/helpers/device_registry.py` at `2026.9.0`, while a second file
  gave `2027.8` for the same APIs. Core carries five distinct values there. No invariant
  asked for a release number to be read back, so none of the four rounds looked — hence
  invariant 8.
- A pass converting sixteen files to `docs/skill-schema.md` dropped fifteen facts and changed
  the meaning of six rules, and `scripts/skill_schema_audit.py` went greener with every one
  of them, because a deleted clause shortens a prose run. The sweep that found them was
  looking for schema violations, not for losses; hence invariant 9, and hence one file per
  pass, each diffed against its previous version before it is committed (row 228).
- Invariant 4, then "each subject covers the whole diff of its commit", was read on
  2026-09-26 as forbidding a commit that touches four files for one decision, and the
  history was recut by file three times before the author ruled that a commit is one
  decision (row 247); hence the invariant's present wording.
