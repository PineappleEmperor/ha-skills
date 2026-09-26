# Audit — the judgement checklist

Read this when auditing a repo against the skill: the items a grep cannot decide. The
mechanical ones are ha-integration-ci's `skill_audit.py --list`.

**A green gate is not a green suite — the mechanical audit compares no copied file against
its source, and never runs the repo's tests.**

## Contents

1. The audit
2. Step 1: Callers, not bodies; copies, not paraphrases
3. Step 2: Patterns applied
4. Step 3: `quality_scale.yaml` honest
5. Step 4: Tests mock the boundary
6. Step 5: Commit and PR discipline
7. Step 6: Cached facts still true
8. Step 7: Run what CI runs
9. Step 8: Report

## The audit

| Rule | Value |
|---|---|
| what runs it on every PR | the `quality-audit` caller, per *Calling the workflows* in ha-integration-ci's README |
| running it by hand | `python3 scripts/skill_audit.py --root <repo>`, from a checkout of ha-integration-ci |
| the list of mechanical checks | `--list`, and *What the audit checks now* in that README |
| what this file adds | the items below, which a grep cannot decide |

### Step 1: Callers, not bodies; copies, not paraphrases

`reference/github-actions.md`, checked per file.

| Rule | Value |
|---|---|
| a workflow the scaffold carries | either a caller matching its README block with the tokens resolved, or a copy matching this skill's `templates/` |
| where `templates/` is | *Step 1: Locate `templates/`* in `reference/github-actions.md` |
| every difference from the source | in that file's sanctioned-adaptations table, or it is a finding |
| what the mechanical audit checks | *What the audit checks now* in ha-integration-ci's README |
| `.github/` and `scripts/` | scan for extras the template does not have |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `cmp` a template directory against the repo's | `cmp` file against file | a tree still being assembled reads as identical when individual files differ | *Step 1: Locate `templates/`* in `reference/github-actions.md` |

> **Note:** if `templates/` cannot be located, report this item as **not checked**; do not
> mark it passed.

### Step 2: Patterns applied

Judged section by section, citing the section beside each finding:

- the `__init__.py` wiring list of *Step 3: Wire the entry setup and unload* in `reference/patterns.md`
- *Entity platform files — Step 1* in `reference/patterns.md`
- *Notify platform (modern pattern — HA 2023.8+) — Step 1* in `reference/patterns.md`
- *Typed `ConfigEntry` — Step 4* in `reference/patterns.md`

### Step 3: `quality_scale.yaml` honest

Judged against *Step 1: Scaffold `quality_scale.yaml` from the start* in
`reference/quality-scale.md`, plus the one thing no check sees — an optimistic `exempt`
masking a gap, such as `stale-devices` exempt while a device *is* created.

### Step 4: Tests mock the boundary

Judged against *Step 1: Mock only at the external boundary* and *Step 4: Minimum coverage
before claiming a tier* in `reference/testing.md`.

### Step 5: Commit and PR discipline

Subjects and titles judged against `reference/commits.md`, the version model against
`reference/versioning.md`.

### Step 6: Cached facts still true

Re-derive any row in the cached-facts table (`reference/freshness.md`) captured more than
~3 months ago, using the command in its *Re-derive with* column. Report each as
still-current or stale-with-the-new-value, and update every consumer listed on that row in
one pass.

### Step 7: Run what CI runs

Run the *Lint & quality check* commands in `SKILL.md` against the repository under audit,
and read the result, before reporting the audit clean. The command block in
ha-integration-ci's README is that repository's own; a consumer reaches those scripts
through `quality-audit.yml` instead.

### Step 8: Report

Per item: pass/fail with `file:line` evidence · what the mechanical gate caught · remaining
manual work. Fix findings before claiming the tier.
