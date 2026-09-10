# Audit — the judgement checklist

The audit items a grep cannot decide. ha-integration-ci's `skill_audit.py --list` covers the mechanical ones.

## Judgement checklist (read the code — a grep can't decide these)

- **Callers, not bodies; copies, not paraphrases.** Each workflow the scaffold carries is
  either a caller matching its README block with the tokens resolved, or one of the copied
  files in `reference/github-actions.md`'s table matching this skill's `templates/`
  (locate it per *Where `templates/` lives* there). Every difference must appear in the
  sanctioned-adaptations table in that file. The mechanical checks (`check_callers`,
  `check_action_pins`) hold a caller to the right repository, path and pin shape; what they
  cannot see is a copied config or plain workflow rewritten by hand, so compare those
  **per file** with `cmp`, never per directory, and scan `.github/` and `scripts/` for
  extras the template does not have. If `templates/` cannot be located, report the item
  as **not checked**; do not mark it passed.
- **Patterns applied** — judged against `reference/patterns.md`: `runtime_data` (not `hass.data[DOMAIN][entry_id]`) for entry state; coordinator `async_shutdown()` on unload; `async_remove_config_entry_device` present if the integration creates a device; `DeviceInfo` TypedDict; `_attr_has_entity_name = True`; typed `ConfigEntry` alias; modern `NotifyEntity` (or a directly-registered service for custom `data`).
- **`quality_scale.yaml` honest** — the rule list and tier requirements are `reference/quality-scale.md`: every canonical rule listed; every `exempt` carries a real `comment`; no optimistic `exempt` masking a gap (e.g. `stale-devices` exempt while a device *is* created); the `manifest.json` tier claimed only when every rule at/below it is `done`/`exempt`.
- **Tests mock the boundary** — the rules are `reference/testing.md`: a real setup-entry `LOADED` test exists (not just `async_setup_component`); the transport is mocked, not the integration's own functions; a two-entry parallel `LOADED` test exists if multiple devices are allowed; parsers have unit tests.
- **Commit/PR discipline:** subjects and titles follow `reference/commits.md`, which names the types a title may carry. The version model is `reference/versioning.md` — check the repo against that, not against memory.
- **Cached facts still true.** Re-derive any row in the cached-facts table (`reference/freshness.md`) captured more than ~3 months ago, using the command in its *Re-derive with* column. Report each as still-current or stale-with-the-new-value, and update every consumer listed on that row in one pass.

**A green gate is not a green suite.** What `skill_audit.py` checks is *What the audit
checks now* in ha-integration-ci's README; the per-file comparison above is a human item
because nothing mechanical does it, and the audit never runs the repo's tests. Run what CI
runs — `ruff`, `pyright`, `pytest`, `version_sync.py` — before reporting an audit clean.

**Report:** per-item pass/fail with `file:line` evidence · what the mechanical gate caught · remaining manual work. Fix findings before claiming the tier.
