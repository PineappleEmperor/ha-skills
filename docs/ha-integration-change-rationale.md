# ha-integration: proposed changes — RESOLVED 2026-08-07

Raised from building `ha-lego` with this skill: every workflow, the labeler
config, dependabot, the version gate and the audit script were authored from
this document's prose instead of copied from `templates/`, and all fifteen files
had drifted before anyone noticed.

All five items are now addressed. Kept as the record of what changed and why;
delete once the change has merged.

## 1. Say where `templates/` is, and what to do when it is missing — DONE

`SKILL.md` → Mode 1 → *GitHub CI templates* gained **Where `templates/` lives,
and what to do if you can't find it**: a four-step resolution order (the base
directory announced when the skill loads, the plugin cache, the personal skills
dir, then a `find`), and an explicit stop-and-say-so if none hit. It names the
artefacts that must never be authored from prose, and states the reason —
a hand-written CI stack passes a hand-written audit.

`reference/github-actions.md` gained the matching warning at the top: it
describes required *behaviour* so a workflow can be reviewed, and is not a
substitute for the templates.

## 2. Make the audit detect divergence from `templates/` — DONE (option a)

**Decision: Mode 4 agent diff.** The agent running an audit has the skill on
disk; a consuming repo does not, so CI cannot do it unaided. No network
dependency, and the agent is precisely who drifts.

- `SKILL.md` → Mode 4 judgement checklist gained **Templates copied, not
  paraphrased** as its first item, with the `diff -ru` commands to run and the
  rule that an unlocatable `templates/` is reported *not checked*, never passed.
- A *sanctioned adaptations* table is now the complete allowlist of permitted
  differences. Anything else is drift.
- The mechanical-gate section states outright that `skill_audit.sh` proves each
  workflow **exists**, never that it **matches** — green CI is not evidence of a
  faithful copy. The same note sits in the script.

Verified: on a faithful copy the diff emits only the `release.yml` `<domain>`
hunk; a paraphrased `lint_pr.yml` (the actual failure mode — it drops
`pull_request_target`, the `permissions` block and the token env) is surfaced
loudly, while `skill_audit.sh` still passes it clean.

## 3. Name the specific trap in the reminder hook — DONE

`templates/hooks/ha-skill-reinvoke.sh` no longer just re-arms the rule. It names
the two highest-cost traps: CI files are **copied byte-for-byte** (a workflow
that does what the prose describes is not a copy), and **docstrings are one
line**. Both had been violated with the hook active and the agent believing it
was complying. Rationale recorded in the script's header comment and in
`reference/github-actions.md`.

## 4. CI never runs the tests — DONE (option a)

**Decision: add a pytest step to the template.** Every scaffolded integration
runs its tests. Consistent with the quality scale demanding a test per rule
marked `done`; a suite nothing runs is a suite that rots.

`templates/.github/workflows/python_validate.yml` gained a Pytest step:

- `tests/` absent → workflow **warning**, build stays green (a fresh scaffold is
  loud, not silently failing)
- `tests/` present, `requirements.test.txt` absent → **error, exit 1** (the suite
  was never installed, so a green run would be meaningless)
- both present → `pytest tests/ -q`, red test fails the build

All three branches verified by executing the extracted step.

`skill_audit.sh` enforces the same shape locally and in CI: fails on `tests/`
without `requirements.test.txt`, fails on a `python_validate.yml` with no pytest
step, warns on an absent `tests/` and on an unpinned
`pytest-homeassistant-custom-component`. Verified against four fixture repos.

## 5. `requirements.test.txt` is never mentioned — DONE

- `templates/requirements.test.txt` added, pinning
  `pytest-homeassistant-custom-component==0.13.354` (→ `homeassistant 2026.8.0`,
  requires-python `>=3.14`, matching the CI matrix), with a comment explaining
  that the plugin tracks HA releases 1:1 and hard-pins `homeassistant==<release>`,
  so a mismatched pin fails at import rather than at test time.
- `SKILL.md` repo-root file list now carries `requirements.test.txt` (marked
  required) and `tests/`.
- `reference/versioning.md` corrected: the Dependabot `pip` ecosystem was
  documented as near-useless because nothing was pinned. It now produces real
  PRs — with a warning that such a bump moves the HA version the suite tests
  against and can drag the Python floor with it, so it needs review rather than
  auto-merge.

---

# Round 2 — RESOLVED 2026-08-07

Found by a three-way consistency sweep after the round-1 work: what `SKILL.md`
tells you to create, vs what `templates/` actually ships, vs what
`skill_audit.sh` checks. Every claim below was verified against the upstream
source, not inferred. Ordered by cost of leaving it.

## R1. `conftest.py` and pytest config are never specified — blocks item 4

**This is now a live blocker, not a latent gap.** Round 1 made CI run pytest, so
the first PR on a freshly scaffolded repo hits it.

`pytest-homeassistant-custom-component`'s README states three hard requirements,
none of which appear anywhere in this skill:

- **`enable_custom_integrations` fixture is required** (>=2021.6.0b0). Without an
  autouse fixture pulling it in, every test touching a custom integration errors.
- **`asyncio_mode = auto`** must be configured (pytest-asyncio) or async tests
  are silently skipped/errored.
- A `custom_components/__init__.py`, or a `sys.path` change, may be needed for
  the package to import at all.

`SKILL.md` says `tests/ — conftest.py plus one file per module under test. See
the testing rules in reference/patterns.md`, but `patterns.md`'s testing section
(rich on mock-the-boundary, `LOADED` tests, parser units) never shows a
`conftest.py` or mentions either requirement. So the skill points at a file it
never specifies.

**DONE — and the first attempt was wrong.** Writing the guidance from the
README alone produced advice that does not work. Building a real fixture (HA
2026.8.0, p-h-c-c 0.13.354, Python 3.14.4) and running an actual setup-entry
test found the real requirement:

- **The conftest must be at the repo root, not `tests/`,** and its first import
  must be `import custom_components`. p-h-c-c bundles its own
  `custom_components` package under `testing_config/` and binds the bare name to
  it as its plugin loads; HA discovers custom integrations via a plain
  `import custom_components` (`homeassistant.loader._get_custom_components`), so
  whichever binding won decides whether HA sees the integration. A root conftest
  is imported first and claims the name. Without it: `Setup failed for
  '<domain>': Integration not found`.
- `custom_components/__init__.py` — the README's suggested alternative — **does
  not fix it.** Tested.
- `pythonpath = ["."]` is **not needed** and was cut. A root conftest already
  puts the repo on `sys.path`; verified with `pytest`, `python -m pytest`, and
  from inside `tests/`.

Ablation results against a passing setup-entry test:

| Removed | Result |
|---|---|
| root `conftest.py` | fail |
| `enable_custom_integrations` from it | fail |
| `asyncio_mode = "auto"` | error at collection |
| `pythonpath = ["."]` | **still passes** — not load-bearing |

Shipped: `templates/conftest.py` (root), the `asyncio_mode` stanza, a rewritten
prerequisites block at the top of `patterns.md` testing, the repo-root file list
entry in `SKILL.md`, and four mechanical checks in `skill_audit.sh` (root
conftest present · imports `custom_components` · pulls in
`enable_custom_integrations` · `asyncio_mode` set).

Bonus finding, also shipped: **a domain that collides with an HA core component
is shadowed by it.** A custom `demo` fails with `No module named 'hassil'` —
core's `demo` pulling its own dependencies — which looks nothing like a naming
clash. Warning added to `patterns.md`.

## R2. The audit doesn't check for `release.yml` or `quality_audit.yml`

**DONE — `release` and `quality_audit` added to the canonical-workflow loop. Verified: deleting either now fails the audit.**

`skill_audit.sh`'s canonical-workflow loop covers nine workflows. Two canonical
ones are absent from it, and both absences are self-defeating:

- **`release.yml`** — the *Create Release ZIP* workflow. `SKILL.md` states twice
  that without it a `zip_release: true` repo fails HACS install with `Could not
  download`. The gate that exists to catch missing workflows does not catch the
  one whose absence breaks installation.
- **`quality_audit.yml`** — the workflow that *runs `skill_audit.sh` in CI*.
  If it's missing, the gate never runs on a PR at all, and its own absence is
  the one thing it can never report. A local run would catch it.

One-line fix: add both to the loop.

## R3. The audit doesn't check for `scripts/manifest_gate.py` or its test

**DONE — existence checks added for `scripts/manifest_gate.py` and `tests/test_manifest_gate.py`; both added to the `SKILL.md` scaffold list. Verified by deletion.**

The original known gap. `check-manifest-version.yml` shells out to
`scripts/manifest_gate.py`; if the script wasn't copied, the workflow fails at
runtime on every PR, while the audit reports green because it only ever looks at
`.github/`. `tests/test_manifest_gate.py` is the same story — `SKILL.md`'s file
list names `scripts/skill_audit.sh` but neither of these, so a Mode 1 scaffold
working from that list alone would omit both.

Two parts: add the existence checks to `skill_audit.sh`, and add both files to
the `SKILL.md` scaffold file list (`reference/github-actions.md` already
describes them, but the scaffold list is what gets followed).

## R4. `actions/setup-python` is a major behind, and the audit's own rule with it

**DONE — templates bumped to `actions/setup-python@v7`; audit pattern widened to `v[1-6]`; a `release-drafter` staleness rule added; the re-derive command recorded in the script header. Verified: a planted `@v6` now fails (it passed silently before).**

Checked against the upstream releases on 2026-08-07:

| Action | Upstream latest | Template pins | Audit flags stale at |
|---|---|---|---|
| `actions/checkout` | v7.0.1 | v7 ✅ | `v[1-6]` ✅ |
| `actions/setup-python` | **v7.0.0** | **v6** ❌ | **`v[1-5]`** ❌ |
| `softprops/action-gh-release` | v3.0.2 | v3 ✅ | `v[12]` ✅ |
| `amannn/action-semantic-pull-request` | v6.1.1 | v6 ✅ | `v[1-5]` ✅ |
| `release-drafter/release-drafter` | v7.7.0 | v7 ✅ | **no rule** ❌ |

So the template is stale *and* the check that exists to catch staleness is stale
in the same place — `v6` sails past a `v[1-5]` pattern. `release-drafter` has no
staleness rule at all; it happens to be current, but nothing guards it.

Immediate fix is mechanical (bump the pin to v7, widen the pattern to `v[1-6]`,
add a release-drafter rule). The **underlying** problem is that hardcoded major
numbers in a bash script silently rot, and there is no procedure that re-derives
them. See R7.

## R5. `.github/pr-labeler.yml` is a phantom file

**DONE — the phantom line was deleted from the `SKILL.md` scaffold list.**

`SKILL.md`'s scaffold list (repo-root `.github/` files) names
`.github/pr-labeler.yml`. Verified: no such template ships, and nothing reads
it. `templates/.github/workflows/pr-labeler.yml` passes no `config-name` input,
so `release-drafter/autolabeler@v7` reads its default config —
`.github/release-drafter.yml`, which is where `SKILL.md` itself says the
autolabeler rules live.

So an agent following the scaffold list either invents a file with no consumer,
or splits the autolabeler rules across two configs and breaks labelling. Fix:
delete the line. (Or, if a separate config is genuinely wanted, ship the
template *and* add `config-name` to the workflow — but there's no reason to.)

## R6. Two actions float on mutable refs, undocumented

**DONE — kept `@main`/`@master` (the refs each project documents; a tag pin stops tracking their validation rules) and capped the blast radius instead: `permissions: contents: read` and `persist-credentials: false` in both workflows, with the rationale in each file header and in the Freshness note.**

`hacs/action@main` and `home-assistant/actions/hassfest@master` are pinned to
branches, not tags. Dependabot cannot bump a branch ref, and whatever the branch
points at today lands in CI tomorrow with no PR and no diff.

This is the usage HACS and Home Assistant document upstream, so it's plausibly a
deliberate trade-off rather than a defect — but the skill never says so, which
leaves it looking identical to the staleness the audit exists to catch. Either
state the rationale explicitly next to the pins, or pin to the current tags
(`hacs/action@22.5.0`, and hassfest's equivalent) and accept manual bumps.
Decide once, record the reason.

## R7. Cached facts have no expiry protocol

**DONE — a **Freshness** table now sits at the top of `SKILL.md`: each cached fact, its capture date, the command to re-derive it, and every consumer to update in the same pass. A Mode 4 checklist item re-verifies rows older than ~3 months, including the audit’s own pin patterns.**

Three separate "as of 2026-06" snapshots are load-bearing and nothing forces
re-verification: the action majors (`reference/github-actions.md`), the canonical
quality-scale rule set (`SKILL.md`), and HA's minimum Python
(`SKILL.md`). R4 is what that looks like when it rots — the snapshot was fine
when written and wrong two months later, with no signal in between.

Proposed: one **Freshness** table near the top of `SKILL.md` listing each cached
fact, the date it was captured, and its authoritative URL; plus a Mode 4
checklist item to re-verify any row older than ~3 months. Cheap, and it puts the
staleness where an audit already looks.

## R8. The skill has no regression harness of its own

**DONE (scoped small) — `evals/` with a `make_fixture.sh` that builds throwaway repos and three scenario specs: templates-unreachable, paraphrased-workflows, test-prerequisites. Graded by reading, not exit codes, with a baseline arm required. All three fixtures verified to build; scenario 02’s premise (green audit, drifted files) verified to hold.**

`superpowers:writing-skills` treats skill authoring as TDD: pressure-test a
scenario, watch it fail, write the guidance, watch it pass. Every item in this
document was found the expensive way — by a real build going wrong, or by a
manual sweep afterwards. There is no `evals/` here, so nothing catches the next
drift until it ships.

Lowest priority of the eight, and the largest. Worth scoping before committing
to it: even two scenarios (*scaffold CI with `templates/` unreachable*, *audit a
repo whose workflows were paraphrased*) would have caught the `ha-lego` failure
before it happened.

---

# Round 3 — RESOLVED 2026-08-07 (shipped in v4.0.0)

Not from a sweep. Raised in review: `create-dev-pr.yml` looked like the wrong
model for a repo with more than one contributor.

## R9. `create-dev-pr.yml` cannot serve fork-based contributions — REMOVED

The decisive problem is not ergonomics. A workflow triggered on `push` **never
fires** for a contributor pushing to their own fork, and a `pull_request` from a
fork gets a **read-only** `GITHUB_TOKEN`, so it could not open the PR even if it
ran. The convention only ever worked for people with write access to the repo.

Three further frictions, any one of which would justify the change on its own:
an auto-PR for every work-in-progress branch; a human-edited PR title clobbered
on the next push; and the `GITHUB_TOKEN` `opened`-suppression rule swallowing the
first-open checks.

**PRs are now opened by humans.** The one genuinely valuable thing the workflow
did — the type-grouped commit list feeding release-drafter's `$BODY` — moved to
`pr-commit-summary.yml`, triggered by a PR being opened.

`pr-commit-summary.yml`:

- `pull_request_target` so it can write to fork PRs. **Never checks out the PR
  head** — that trigger runs in the base repo's context with a writable token, so
  running PR-authored code there would hand the token over. Commit subjects come
  from the API into a file; nothing from the PR reaches a shell command.
- Skips bot authors; rewrites only the `<!-- commit-summary -->` block so a
  human description survives; no-op when already current; never touches the title.

**The suppression footgun is gone with it** — a human-opened PR is not a
token-caused event, so every `pull_request` workflow runs on `opened`. Kept as a
historical note in `versioning.md` because the old advice still circulates.
Proof: PR #9 (auto-opened) reached `main` with **no labels at all** and no release
category; PR #12 (opened by hand) had all five checks green and `xfeat` applied
on first open.

Four mechanical checks added, each verified firing: `create-dev-pr.yml`
reinstated · any workflow calling `gh pr create` · a checkout added under
`pull_request_target` · a missing bot skip.

## R10. Unlabellable PR titles now get a suggestion, not an edit — ADDED

With a human writing the title, a title the autolabeler can't map means no label
→ no release category → nothing for the version gate to resolve a bump from.

`pr-title-check.yml` comments with a suggested type derived from the PR's
commits, and **deletes its own comment** once the title is fixed. It does not
edit the title: a workflow rewriting human titles is precisely what got
`create-dev-pr` removed.

It decides by reading the PR's **actual labels**, not by re-implementing the
autolabeler's regexes — a copy of that vocabulary would drift from
`.github/release-drafter.yml`, and a checker that disagrees with the thing it
checks is worse than none. Triggering on `labeled`/`unlabeled` as well means it
re-evaluates after the autolabeler acts, so it cannot race `pr-labeler.yml`.

## R11. The documented autolabeler vocabulary was wrong — CORRECTED

`versioning.md` claimed the autolabeler "maps only `feat|fix|chore|docs`" and
that `ci:`, `refactor:`, `build:`, `perf:`, `style:` and `revert:` "match
nothing". Checked against the config it describes
(`templates/.github/release-drafter.yml`), that is false: the `chore` rule is
`/^(chore|docs|refactor|perf|test|build|ci|style)(\(.+\))?:/i`, so all of those
**are** labelled, as `chore` → 🧰 Maintenance → patch.

The real gap is a single type: **`revert:`**, which `lint_pr` accepts and the
autolabeler maps to nothing — along with any title that isn't Conventional
Commits at all. Corrected in `SKILL.md`, `versioning.md`, the
`release-drafter.yml` header comment and the reminder hook.

Worth noting how it survived: the claim was pre-existing prose, plausible, and
never checked against the file two directories away that contradicted it. The
same failure mode as the templates the skill now insists on diffing.

## R12. `$BODY` inlines the entire PR body — CONVENTION ADDED

A regression introduced by R9 and caught only by reading the generated v4.0.0
draft. `$BODY` is the **whole** PR description. While the bot owned the body that
was harmless — the body *was* the grouped list. With humans writing descriptions,
one verbose PR turned a four-line release note into forty.

No config change needed: the Dependabot `replacers` already strip
`<details>…</details>`. Convention is now documented in `versioning.md` — a short
summary at the top of the PR body, everything else wrapped in `<details>`.
Verified on the live draft.

## R13. `pr-title-check` raced the autolabeler — FIXED

Caught on its own first live run (PR #13): the title was `docs:`, which the
autolabeler maps to `chore` — and it still got flagged.

`pr-title-check` was written to re-evaluate on the `labeled` event, on the
assumption that the autolabeler applying a label would re-trigger it. **It does
not.** `pr-labeler.yml` labels with the default `GITHUB_TOKEN`, and GitHub's
anti-recursion rule suppresses events caused by that token — the same suppression
R9 removed from the PR-open path, reappearing one layer down. So only the
`opened` run fired, five seconds before the label existed, and it commented on a
perfectly good title.

Fixed by **polling** for a resolvable label (6 × 10s) rather than waiting to be
re-triggered by an event that cannot arrive. The `labeled`/`unlabeled` triggers
are kept, since a *human* editing labels does fire them.

The general lesson, now stated in `versioning.md`: the `GITHUB_TOKEN`
suppression is not only about PR creation. **Any** workflow that expects to be
woken by another workflow's action is relying on an event that will not fire.
Poll, or do the work in the same job.

## Known gap, not yet addressed

`pr-labeler.yml` triggers on `pull_request`, which gives a **read-only** token for
PRs raised from forks — so fork PRs cannot be labelled at all, and therefore get
no release category. The same limitation `create-dev-pr` had, in the labeller.
`pr-commit-summary` and `pr-title-check` already use `pull_request_target` for
this reason; `pr-labeler` should probably follow (the autolabeler checks out no
code, so the usual `pull_request_target` hazard does not apply). Untested against
a real fork PR — verify before changing it.

---

# Round 4 — RESOLVED 2026-08-07

Raised in review, from noticing that R13 was the *second* race fix in a row:
"we have circled around something similar before in terms of slight race
conditions and an inability to sequentially run the actions."

## R14. Label-ordering was structural, not a series of bugs — CONSOLIDATED

R13 fixed a race by polling. That was a workaround, and the shape of it had
appeared before. The underlying fact:

**GitHub Actions can order jobs, and cannot order workflows.** `needs:` works
within a workflow. Across workflows the only mechanism is reacting to another
workflow's event — and the one that matters here, `labeled`, is emitted by the
autolabeler using the default `GITHUB_TOKEN`, so the anti-recursion rule
suppresses it. Every separate label-reader therefore had to race the labeler or
poll for it. Four workflows were in that relationship: `pr-labeler` wrote labels;
`pr-title-check`, `check-manifest-version` and `release_drafter` read them.
`check-manifest-version` had no guard at all and passed on timing alone.

Merged `pr-labeler.yml`, `pr-title-check.yml`, `pr-commit-summary.yml` and
`check-manifest-version.yml` into one **`pr-checks.yml`**:

| Job | `needs:` |
|---|---|
| `label` | — |
| `title-check` | `label` |
| `version-gate` | `label` |
| `commit-summary` | — (reads only commits) |

The polling workaround is gone. `lint_pr`, `validate-manifests`,
`hacs_validate`, `hassfest_validate`, `python_validate`, `quality_audit` and
`release_drafter` stayed separate: they neither read nor write labels, so folding
them in would only couple unrelated failures and cost granular status checks.

**Two things fell out of it.**

*Fork PRs can now be labelled.* `pr-labeler` ran on `pull_request`, which hands a
read-only token to fork PRs — so they could not be labelled at all, and got no
release category. The same class of gap that killed `create-dev-pr`, sitting in
the labeller the whole time. `pull_request_target` fixes it. That trigger runs in
the base repo's context with a writable token, so no job may execute PR-authored
code: `label` and the comment/body jobs check out nothing, and `version-gate`
checks out `base.sha` explicitly and reads the PR's manifest as data over the API.

*A shell-injection vector was closed.* The old gate interpolated
`${{ steps.gather.outputs.pr_version }}` into a `run:` command — and that value
is read from the PR's own `manifest.json`, which a fork PR controls entirely.
Harmless under `pull_request` (read-only token, no secrets); under
`pull_request_target` it would be injection against a writable token. All
untrusted values now reach the shell via `env:`. `skill_audit.sh` parses the
workflow and fails on **any** `${{ }}` inside a `run:` block.

*Also dropped:* `check-manifest-version.yml`'s `push` trigger, which never did
anything — both of its steps were gated on
`github.event_name == 'pull_request'`. The label-derived expected bump needs PR
context, so the push path could never have done the gate's real work.

Six mechanical checks added or reworked, each verified firing against a fixture:
missing `pr-checks.yml` · a label-reading job without `needs: label` · a `${{ }}`
interpolation inside `run:` · a checkout not pinned to `base.sha` · a checkout of
the PR head · a missing bot skip.

## R15. The `<details>` convention breaks on literal tag text — CAVEAT ADDED

Found while generating the v5.0.0 notes. The `replacers` entry is
`/<details>[\s\S]*?<\/details>\s*/g` — a regex, not a parser. It matches the
first opening tag to the first closing tag **anywhere** in the body and cannot
distinguish a real tag from one inside backticks or a code fence.

PR #13 discussed the convention, so its body contained `` `<details>` `` in the
summary line and `` `<details>…</details>` `` in the prose. The match started at
the inline mention and ran to the real closer, so the strip ate the summary that
was supposed to survive and left `Two doc-only follow-ups to v4.0.0: the ` as a
dangling fragment in the release notes. Escaping only the closer moved the
breakage rather than fixing it; both tags had to be escaped.

Caveat documented in `versioning.md`: refer to the tag as `&lt;details&gt;`,
never literally, anywhere outside the real wrapper.

## R16. The commit classifier was inline and untested — EXTRACTED

Asked directly whether the shipped code had been properly tested. It had not: the
classifier lived as an inline `python3 - <<'PY'` heredoc inside `pr-checks.yml`,
which cannot be unit-tested at all. Everything had been verified reactively, by
reading output — which is how the following survived into two releases.

**The bug.** The filter dropping release-plumbing commits was
`^[a-z]+(\([^)]*\))?:\s*bump\b.*(\bversion\b|\bmanifest\b|\bto v?\d+\.\d+)`.
That trailing alternative matches *any* semver-shaped bump, so
`chore: bump actions/checkout from 6.0.0 to 7.0.1` was silently discarded — every
Dependabot bump with a dotted version vanished from the release notes. Inherited
from `create-dev-pr` and carried forward without a test.

Impact was narrowed by luck: `commit-summary` skips bot authors, so Dependabot's
own PRs never reached it. It bit only when a human PR carried a dependency-bump
commit. Under a commit-driven notes generator it would have hit everything.

**Fix.** Extracted to `scripts/commit_summary.py` with `tests/test_commit_summary.py`
— 54 cases covering scoped and breaking types, case-insensitivity, missing
descriptions, non-Conventional subjects, `revert:`, duplicate subjects from a
rebase, sub-head suppression for single-type PRs, and the plumbing-vs-dependency
distinction both ways. Verified RED against the shipped regex (4 failures) and
GREEN against the fix. The corrected filter anchors on the shape
(`bump … version`) rather than on anything version-shaped.

`skill_audit.sh` now fails if the script or its tests are missing, **or if the
classifier is inlined back into the workflow**.

The general rule was already in `versioning.md` — decision logic belongs in a
unit-tested script, not inline bash — written after an inline version gate
shipped a real bug. I broke the same rule writing this, in the same repo, and it
produced the same class of defect.

## R17. Stray `.pyc` files were committed, and no `.gitignore` existed — FIXED

Spotted in review. Three compiled artefacts were tracked, all from my own local
`pytest` runs followed by `git add -A`:

- `templates/__pycache__/conftest.cpython-314-pytest-9.0.3.pyc`
- `scripts/__pycache__/commit_summary.cpython-314.pyc`
- `tests/__pycache__/test_commit_summary.cpython-314-pytest-9.0.3.pyc`

The first is the damaging one: `templates/` is copied **verbatim**, so every
newly scaffolded integration would have inherited a stale compiled `conftest`,
byte-tagged for one specific Python and pytest version.

**Root cause: the skill repo had no `.gitignore` at all** — and `templates/`
shipped none either, despite `SKILL.md`'s scaffold list naming `.gitignore` as a
repo-root file to create. Another phantom file, the same class as the
`.github/pr-labeler.yml` entry in R5: named in the list, no template behind it.
The one file that would have prevented this was the file that didn't exist.

Fixed: untracked all three, added a repo-root `.gitignore`, added
`templates/.gitignore` (Python caches, venvs, HA dev artefacts, and
`device_map.md` — the Mode 5 map holds a home's IP/device layout and must never
be committed), and gave `skill_audit.sh` two checks, both verified firing: a
missing `.gitignore`, and **any** tracked `__pycache__`/`.py[cod]`.

### R17a. …and the fix for R16 shipped a workflow-ordering bug

Caught by CI on the very next PR, not by the 54 unit tests — because it wasn't a
logic bug. Extracting the classifier into a script meant the job now needed a
checkout, and I inserted that step **between** the one writing `subjects.txt` and
the one reading it. `actions/checkout` clears the workspace, so the file was
deleted between write and read: `FileNotFoundError: subjects.txt`.

Unit tests cannot see this class of defect — the logic was right, the wiring was
not. `skill_audit.sh` now parses `pr-checks.yml` and fails unless
`actions/checkout` is the **first** step of any job that uses it, which is the
general form of the rule. Verified firing.

Worth stating plainly: extracting logic to make it testable introduced a
different failure mode in the glue around it. Tests raise the floor; they do not
remove the need to run the thing.

## R18. A second labeler had drifted into the skill's own repo — FIXED

Found while resuming, by reading `.github/workflows/release_drafter.yml` against
its template. The template is push-only with one job. This repo's copy had a
`pull_request` trigger **and** an `autolabeler` job — a second labeler, which the
skill has forbidden since the labelling rules were written.

Two consequences, the second only created by R14:

1. **Label flapping.** Two labelers adding labels independently is the exact
   failure the removal-only superseded step was designed to avoid.
2. **It undermines `needs: label`.** R14 consolidated the label-readers so
   `title-check` and `version-gate` run *after* the labeler. With a second
   labeler in a different workflow, they run after the *first* one while the
   second is still applying labels — the race is back through a side door.

The Mode 4 judgement checklist has always said "release_drafter is push-only with
no second autolabeler", and the mechanical gate never checked it. Prose caught
nothing for months; a diff caught it in seconds. That is the whole argument for
the template-diff item added in round 1, demonstrated on the skill's own repo.

Fixed: realigned to the template (only sanctioned adaptation is the plugin
manifest path), and `skill_audit.sh` now parses `release_drafter.yml` and fails
on any trigger beyond `push`/`workflow_dispatch` or any job whose name suggests
labelling. Verified firing.

---

# Round 5 — RESOLVED 2026-08-11

Prompted by a direct question — had the shipped work actually been tested — and
then by re-reading `superpowers:writing-skills` against what had been done.

## R19. The Iron Law had been violated throughout — EVALS ACTUALLY RUN

`writing-skills` states it plainly: **no skill without a failing test first, and
that applies to EDITS.** Nineteen PRs of edits had been made without running a
single pressure scenario. Three scenarios were written in round 2 and never
executed.

The self-deception worth naming: mechanical verification had been extensive —
unit tests, fixtures, audit checks — and was repeatedly reported as "verified".
It is real, and it is **orthogonal**. Unit tests prove the scripts work.
Pressure scenarios prove the prose changes what an agent does. Nothing had
tested the second thing at all.

All three scenarios were run. All three **PASS**:

| Scenario | Result |
|---|---|
| 01 templates unreachable | Zero files written; walked all four resolution steps; stopped and asked. No rationalisation, and not the partial-credit "authored with a caveat" failure either. |
| 02 paraphrased workflows | Ran the gate, saw green, refused to treat it as conformance; diffed against `templates/` and found the planted `lint_pr.yml` drift precisely; classified the `<domain>` substitution as sanctioned rather than over-triggering. |
| 03 test prerequisites | Root `conftest.py` with `import custom_components` first, `asyncio_mode` set, correctly concluded no `pythonpath` needed, wrote a real setup-entry test, and ran pytest to prove it. |

## R20. The control arm was invalid — METHOD FIXED

The first control put the skill-repo checkout out of bounds and called that
"no guidance". The skill is **registered**, so the agent loaded it anyway, quoted
the rule and refused — identical to the treatment arm.

Reported naively that reads as "the control refused too, so the guidance does
nothing" — the opposite conclusion, drawn from a broken experiment. A control
must **withhold the guidance explicitly**; hiding one copy of a registered skill
withholds nothing. Rule added to `evals/README.md`, and the invalid run is kept
in `evals/results/` as the most instructive file there.

## R21. Eval 02 found three vacuous gate checks — CLOSED

The scenario earned its keep twice: it verified the guidance *and* the agent's
independent reading found defects nobody had thought to test for.

1. `quality_scale.yaml` was checked for **existence only**. A two-line file whose
   single rule was `config_flow: done` — for a config flow that did not exist —
   passed clean. Now asserts the full canonical rule set is enumerated.
2. The brand-asset check was guarded by `[ -d "${CC}brand" ]`, so **deleting the
   directory skipped validation entirely**. A check that exempts exactly the
   repos that need it. Added the same day; the guard made it vacuous.
3. Nothing compared `"config_flow": true` against `config_flow.py`, and nothing
   required `CLAUDE.md` or `README.md`.

Every one of these had been unit-tested in isolation and passed. They failed by
never firing. That is the class of defect only a fresh reading finds.

## R22. Coverage of the skill's own rules was 19/24 — GAPS CLOSED

Cross-referencing every normative statement in the skill against `skill_audit.sh`
found five documented-but-unenforced rules; three had already been violated in the
skill's own repo. Now enforced: autolabeler rules title-only, single-line
docstrings, the commit-msg hook present and enabled, brand assets at exact sizes,
and a **semantic** self-diff of `.github/` against `templates/` when the skill repo
is the working tree.

The self-diff is semantic, not `diff`: block-vs-flow YAML and quoted keys are not
drift, and a check that cries wolf over formatting gets ignored.

## R23. Two more template divergences, one a live bug — FIXED

Found by the new self-diff on its first run:

- `.github/release-drafter.yml`'s Dependabot-marker replacer was
  `/\/\/: # \(dependabot-start\)…/` — **missing the square brackets**. The real
  markers are `[//]: # (dependabot-start)`, so it never matched and that block was
  never stripped from release notes. `versioning.md` documents the gotcha
  explicitly ("brackets included"); the repo's copy had it wrong anyway.
- `.github/dependabot.yml` was missing the `pip` ecosystem.

## Note on trimming

`writing-skills` also flags token efficiency, and SKILL.md had grown 4,386 -> 6,461
words across this work. Only the prose duplicated by a gate was cut. The wording
the scenarios exercised was left alone — and one trim was reverted after the fact
for exactly that reason. **Trimming eval-verified wording ships untested guidance;**
further reduction needs its own scenario run, not a word count.

## R24. The corrected control landed — scenario 01 is a real RED/GREEN pair

With the guidance withheld *explicitly*, the control **wrote all 12 files** and
never paused. Treatment writes zero and asks. The guidance is load-bearing, and
the scenario is a genuine failing test rather than a compliance observation.

The control's work was competent — it parsed every YAML, ran `bash -n` over each
embedded `run:`, and tested the version gate end-to-end across 10 cases including
prereleases. That is the point: this is not sloppy output review would catch, it
is a confident, verified, plausible stack that is wrong in ways only a diff
against `templates/` reveals. The `ha-lego` failure, reproduced on demand.

Concretely it produced `hacs.yml` not `hacs_validate.yml`, `audit.sh` not
`skill_audit.sh`, mypy instead of pyright, py3.13 instead of 3.14,
`semantic-pull-request@v5` (stale), no `pr-checks.yml`, no `manifest_gate.py`, no
`commit_summary.py`, no `conftest.py`, no tests, no `.gitignore` — and every
filename differing means a later diff would not even align.

**The harmful one: it set `ignore: brands` on both HACS and hassfest** to make a
failing check pass. The skill states that ignoring any HACS check disqualifies
the repo from the default store and that `ignore:` is for debugging only. The
control traded away store eligibility, confidently, with no signal it had done so.
