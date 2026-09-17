# Five-repo sweep: prove and improve the ha-integration skill

Design, agreed 2026-09-15. Written for the maintainer and for the sessions that carry it
out. Not shipped with the plugin.

## Goal

Use the skill on five real repositories, feed every place it was wrong or silent back into
the skill, and leave behind a mechanism that keeps the skill current with Home Assistant's
monthly release.

The skill is judged by what an agent following it literally produces, not by re-reading it.

## The five repositories

| Repository | Starting state | Scope |
|---|---|---|
| `ha-foreca-weather` | one placeholder README; no Foreca integration exists in core, brands or HACS | scaffold from zero, from the skill alone |
| `settleup-ha` | platinum claim, ten test files, hook, disclaimer; copied workflow bodies, tag-pinned actions, a ruleset with no required checks and an admin bypass, no root `conftest.py` | callers onto the stack; ruleset; 2026.9 code pass; audit clean |
| `parcel-ha` | `jmdevita/parcel-ha`, on which the maintainer is a collaborator; `v1.8.3`, eight copied workflows of an older era, tests present | fresh clone of upstream `main`; 2026.9 code pass, bugs and legacy; **local only — no upstream PR**; **no CI changes**; and, in a second worktree, a written comparison of what the stack's CI would buy the repository |
| `ha-lego` | 11 copied bodies with copied release scripts in `scripts/`; nine required contexts on the old names; panel; 3.3k lines and 3.5k of tests; last full release `v0.4.0`, `v1.0.0rc1` open | callers; contexts renamed; panel via ha-panel-ci; 2026.9 code pass; audit clean; rc published on the repo |
| `ha-pimoroni-unicorn` | 13 copied bodies, two of which the stack has no equivalent for (`firmware_test`, `check-engine-version`) and a third, `cut_rc`, which it replaces with release-flow's living rc draft; gold claim; a ruleset with no required checks and an admin bypass; 11.9k lines | as ha-lego, plus a decision per extra workflow, made on evidence and stated in the PR |

"2026.9 code pass": deprecated helpers and signatures off, current patterns on, per the
refreshed skill; nothing rewritten for its own sake.

The old integration clones under `/home/juicebox/<repo>` are not used: they cannot fetch
inside the sandbox, and `parcel-ha`'s is a clone of a fork the maintainer has said to leave
alone. The four CI-repository clones (`release-flow`, `ha-integration-ci`, `ha-panel-ci`,
`ha-ci-testing`) are writable and are read at `origin/main` for the READMEs, the drafter
config and the hook.

## Decisions

Every decision the maintainer has taken on this sweep is recorded in
`.tmp/plan/decisions.md`, numbered, with what each changes. The plans are edited to match
it; it is the record to check them against, not this session's memory. Read it before
executing any task here.

## A review stage comes first

Before any repository is worked it gets a dossier under `.tmp/dossier/`, whose scope is
decisions 1 and 2; all five were written 2026-09-17. A repository is not worked until its
dossier has been read and its decisions answered, because a friction log from a repository
full of unrelated debris blames the skill for the debris.

## Ground rules

- Fresh clones under `claude-skills/.tmp/work/<repo>/`: writable, gitignored, survive the
  session. **The session never pushes to any of the five repositories**: every commit it
  produces is local, and the maintainer pushes. That is unconditional and is not the
  `.github/workflows/` rule, which governs this repository's own branches.
- Every branch goes through the reviewer agent (`docs/review.md`) before the maintainer is
  handed a push. No rule in `docs/review.md` or the hooks changes.
- The register (`docs/backlog.md`) gets one sweep per wave: rows for what the wave found,
  in the finding / decision / evidence / hashes shape, no per-pass narrative.
- Nothing is committed or pushed until the maintainer says go; this spec and the plan are
  files on disk until then.
- Formatting is its own commit, `style: apply ruff format`, landing before a migration
  rather than inside its diff, with deliberately aligned blocks kept by `# fmt: off`
  fences (decisions 22–28). Done 2026-09-17, local and unpushed: ha-lego needed none,
  settleup-ha is `95ed0db` (21 files), ha-pimoroni-unicorn is `7e29ce6` (210 files, 6,079
  insertions). Each wave's Task 1 fetches its commit out of `.tmp/dossier-work/` into the
  working clone and checks it against those numbers, which is why the step repeats them:
  there they are the expected output of a command, not a second telling of the story.

## Step 0: refresh the skill to 2026.9

Before any repository is touched, or five repositories get stale guidance.

1. Gather what changed for a custom-integration author in HA 2026.6 through 2026.9: the
   developer blog, the release notes' developer sections, the quality-scale index and its
   rules, hassfest at the `2026.9.2` tag, the `pytest-homeassistant-custom-component`
   pin. Core files are read at the tag over the GitHub API; no local core clone is needed.
2. Read every reference file in full and diff it against that: the thirteen the
   reference map in `SKILL.md` lists (`scaffold.md`, `patterns.md`, `testing.md`,
   `commits.md`, `github-setup.md`, `github-actions.md`, `versioning.md`,
   `dependabot.md`, `quality-scale.md`, `panels.md`, `discipline.md`, `audit.md`,
   `freshness.md`) and `SKILL.md` itself.
3. Fix what is stale, grouped by file; re-derive every `freshness.md` row; bump the
   template pins that moved.
4. One ha-skills PR, reviewed once. Its diff is the first run of the monthly procedure
   (below), so the procedure is proven before it is written down.

## Waves

**Wave 1**, three subagents in parallel, each in its own clone: `ha-foreca-weather`
scaffold, `settleup-ha`, `parcel-ha`. The maintainer answers the ten scaffold questions
in `reference/scaffold.md` for Foreca before the wave starts (domain, API product and
auth, platforms, licence…).

**Consolidate**: the three friction logs become one skill PR and one register sweep.

**Wave 2**, two subagents in parallel: `ha-lego`, `ha-pimoroni-unicorn`. They run against
the skill as improved by wave 1, since they are the heaviest and the panel path is the
least proven.

**Consolidate** again. An eval scenario is added only where a real failure got past the
skill, per `evals/README.md`; the agent's verbatim rationalisation is recorded.

## The friction log

One file per repository, `claude-skills/.tmp/friction/<repo>.md`, one entry per event:

```
- <reference file> · <heading> · said: <what the skill said> · true: <what was actually
  the case> · did: <what the agent did about it>
```

Subagents are briefed: follow the skill literally; when it is silent or wrong, log the gap
and then use judgement; never fill a gap from memory without an entry. The log is the whole
feedback channel. The consolidating session reads each in full and turns entries into edits
in the reference file that owns the topic; an entry that turns out to be the agent's error
rather than the skill's is recorded as such and not edited in.

Each subagent's brief also names the audit, ruff, pyright and pytest as the local gate:
green before any push is handed over, and the friction log includes every audit finding
the skill did not warn about.

**Check every claim against the file that owns it before writing it down.** Two dossier
agents reported `brands` as failing because the integrations are absent from
`home-assistant/brands`; `reference/scaffold.md` says the inline `brand/` folder is the
supported path from the HA version `reference/freshness.md` records — `2026.3.0` — and that
`custom_integrations/` PRs are auto-closed. Note that the two files split that fact between
them, which is the pattern: the reference file states the rule, the freshness table holds
the version it turns on. The skill was right and was not consulted. A friction line
asserting the skill is wrong is worth nothing unless the owning file was read first.

## Verification

Per repository: ruff, pyright and pytest green locally and `skill_audit.py --root`
clean — for `parcel-ha`, whose CI is untouched, clean on its integration checks with the
caller and GitHub-side checks reported as expected failures, and with no PR to be green
since nothing is sent upstream; CI green on the PR of the four that have one; for `ha-lego` and `ha-pimoroni-unicorn` an rc published on the repo
itself, since the testbed proves the stack and each repo proves its own release. For
`ha-foreca-weather`, HACS's nine checks and the first release with a zip asset.

For the skill: after each consolidation, the eval scenarios whose fixtures or guidance
changed are run in both arms, 3–5 samples each, per `evals/README.md`; results recorded
under `evals/results/`.

## Monthly release mechanism

Two layers, both in the skill repository.

**Nudge.** `reference/freshness.md` gains a row `HA release the skill is current for`,
value the minor (`2026.9`), captured date, re-derive command
`curl -s https://pypi.org/pypi/homeassistant/json | jq -r .info.version`. A step in
ha-skills' own `ci.yml` reads that value from the file and PyPI's latest, and fails when
the captured minor is behind. Red CI in the week a release lands; nothing silent. The
check is a small tracked script with a test, since it parses a table cell.

**Procedure**, in `freshness.md` beside the row: on red, read that release's developer
blog posts and the release notes' developer section; list deprecations, removals and new
guidance affecting a custom integration; update the reference files that own each topic;
re-derive the other rows; bump the captured minor; one PR. Step 0 is its first run.

**Follow-up, not in this plan**: a scheduled cloud agent that runs the procedure on the
first Wednesday after each release and opens the PR unattended. It spends money and needs
the maintainer's opt-in; the procedure above is written so that agent has something exact
to run.

## What must change in the CI repositories first

Two of them, both found by the dossiers, both needing a release before wave 2:

- **`ha-integration-ci`'s `release.yml` builds a second asset when `firmware/` exists** —
  `<domain>_firmware.zip`, the way it already rebuilds a panel bundle before packing. The
  first flash of a Pimoroni device is physical over USB, so the asset is how a new user
  starts; unicorn builds it today from a copied body the migration deletes. Decision 12.
- **`skill_audit.py` measures the two logos, as it already measures the two icons.**
  `check_brand_assets` compares `icon.png` with 256×256 and `icon@2x.png` with 512×512, but takes
  `logo.png` and `logo@2x.png` on existence alone, so an out-of-spec logo passes the audit
  silently. Three repositories checked, two of them out of spec — unicorn's logos are
  square copies of the icon (256×256, 512×512), settleup's are landscape but under the
  minimum shortest side (256×79, 512×157) — and nothing anywhere reports it. The new check
  is a range, not an exact size: shortest side 128–256 for `logo.png` and 256–512 for
  `logo@2x.png`, landscape. Decision 31.

Both ship in one `ha-integration-ci` release, before wave 2. That release makes the new
logo check fail on unicorn and settleup, so **each repository's logo files are replaced in
its own wave**, before its migration PR: the artwork is the maintainer's to draw, a 512×256
landscape wordmark with a 1024×512 companion. Until then the wave plans' audit expectations
hold as written, because the logo half of the check does not exist yet.

## Out of scope

Two of the register's live rows, which `docs/backlog.md`'s header lists, are worked here
on purpose: the refresh plan closes row 177's enforcement half, and both waves enable the
dependency graph row 206 found switched off. Every other live row stays parked unless a
wave trips over it. `ocado-ha` and the other consumers outside the five are not touched.
No change to the CI repositories' code beyond the two under *What must change in the CI
repositories first*; anything a wave itself finds is row-then-fix as before.

## Risks

- A subagent routes around the skill and produces a good repo with an empty friction log.
  Mitigation: the brief forbids unlogged gap-filling; the audit and the reviewer both read
  the result against the skill; an empty log on a non-trivial repo is itself a finding.
- The 2026.9 refresh is large and delays everything. Mitigation: it is bounded to the four
  releases since the last capture and to the reference files listed; anything older is a
  separate row.
- Wave 2's panel repos expose ha-panel-ci gaps. Mitigation: that is the point; a gap
  becomes a ha-panel-ci row and fix, released bottom-up as before.
