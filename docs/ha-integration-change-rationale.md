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
