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

### Step 1: Callers, not bodies; copies, not paraphrases

The invariant in `SKILL.md`, checked per file. Each workflow the scaffold carries is either
a caller matching its README block with the tokens resolved, or a copy matching this skill's
`templates/` (located per *Where `templates/` lives* in `reference/github-actions.md`), and
every difference is in that file's sanctioned-adaptations table. What the mechanical audit
does check is *What the audit checks now* in ha-integration-ci's README; it compares neither
a caller nor a copy against its source. Scan `.github/` and `scripts/` for extras the
template does not have.

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| `cmp` a template directory against the repo's | `cmp` file against file | a tree still being assembled reads as identical when individual files differ | *Where `templates/` lives* in `reference/github-actions.md` |

> **Note:** if `templates/` cannot be located, report this item as **not checked**; do not
> mark it passed.

### Step 2: Patterns applied

Judged against `reference/patterns.md`, section by section: the `__init__.py` wiring list,
*Entity platform files*, *Notify platform (modern pattern — HA 2023.8+)*, *Typed
`ConfigEntry`*. Cite the section beside each finding.

### Step 3: `quality_scale.yaml` honest

Judged against `reference/quality-scale.md`: the structural rules under *Scaffold
`quality_scale.yaml` from the start*, plus the one thing no check sees — an optimistic
`exempt` masking a gap (e.g. `stale-devices` exempt while a device *is* created).

### Step 4: Tests mock the boundary

Judged against `reference/testing.md`: *Mock only at the external boundary* and *Minimum
coverage before claiming a tier*.

### Step 5: Commit and PR discipline

Subjects and titles follow `reference/commits.md`, which points at the types a title may
carry. The version model is `reference/versioning.md` — check the repo against that, not
against memory.

### Step 6: Cached facts still true

Re-derive any row in the cached-facts table (`reference/freshness.md`) captured more than
~3 months ago, using the command in its *Re-derive with* column. Report each as
still-current or stale-with-the-new-value, and update every consumer listed on that row in
one pass.

### Step 7: Run what CI runs

Run the commands ha-integration-ci's README lists before reporting an audit clean.

### Step 8: Report

Per item: pass/fail with `file:line` evidence · what the mechanical gate caught · remaining
manual work. Fix findings before claiming the tier.
