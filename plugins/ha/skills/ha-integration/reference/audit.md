# Audit — the judgement checklist

The audit items a grep cannot decide. ha-integration-ci's `skill_audit.py --list` covers the mechanical ones.

## Judgement checklist (read the code — a grep can't decide these)

- **Callers, not bodies; copies, not paraphrases** — the invariant in `SKILL.md`, checked
  per file. Each workflow the scaffold carries is either a caller matching its README block
  with the tokens resolved, or a copy matching this skill's `templates/` (located per
  *Where `templates/` lives* in `reference/github-actions.md`), and every difference is in
  that file's sanctioned-adaptations table. The mechanical audit compares neither against
  its source (ha-integration-ci's README, *What the audit checks now*), so compare them
  **per file** with `cmp`, never per directory — a tree still being assembled reads as
  identical when individual files differ — and scan `.github/` and `scripts/` for extras
  the template does not have. If `templates/` cannot be located, report the item as **not
  checked**; do not mark it passed.
- **Patterns applied** — judged against `reference/patterns.md`, section by section: the `__init__.py` wiring list, *Entity platform files*, *Notify platform (modern pattern — HA 2023.8+)*, *Typed `ConfigEntry`*. Cite the section beside each finding.
- **`quality_scale.yaml` honest** — judged against `reference/quality-scale.md`: the structural rules under *Scaffold `quality_scale.yaml` from the start*, plus the one thing no check sees — an optimistic `exempt` masking a gap (e.g. `stale-devices` exempt while a device *is* created).
- **Tests mock the boundary** — judged against `reference/testing.md`: *Mock only at the external boundary* and *Minimum coverage before claiming a tier*.
- **Commit/PR discipline:** subjects and titles follow `reference/commits.md`, which points at the types a title may carry. The version model is `reference/versioning.md` — check the repo against that, not against memory.
- **Cached facts still true.** Re-derive any row in the cached-facts table (`reference/freshness.md`) captured more than ~3 months ago, using the command in its *Re-derive with* column. Report each as still-current or stale-with-the-new-value, and update every consumer listed on that row in one pass.

**A green gate is not a green suite.** What `skill_audit.py` checks is *What the audit
checks now* in ha-integration-ci's README; the per-file comparison above is a human item
because nothing mechanical does it, and the audit never runs the repo's tests. Run what CI
runs — the commands ha-integration-ci's README lists — before reporting an audit clean.

**Report:** per-item pass/fail with `file:line` evidence · what the mechanical gate caught · remaining manual work. Fix findings before claiming the tier.
