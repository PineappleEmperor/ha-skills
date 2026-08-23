# Mode 4 judgement checklist

The audit items a grep cannot decide. `scripts/skill_audit.py --list` covers the mechanical ones.

## Judgement checklist (read the code — a grep can't decide these)

- **Templates copied, not paraphrased.** Diff `.github/` and `scripts/` against this skill's `templates/` (locate it per *Where `templates/` lives* in `reference/github-setup.md`). Every difference must appear in the sanctioned-adaptations table there. Files that merely *look* equivalent are not equivalent — `skill_audit.py` checks each canonical workflow **exists**, never that it **matches**, so fifteen hand-written files once passed it clean. Run:
  ```bash
  T=<skill>/templates   # from the skill's announced base directory
  diff -ru "$T/.github" .github
  diff -ru "$T/scripts" scripts
  diff -u  "$T/tests/test_manifest_gate.py" tests/test_manifest_gate.py
  ```
  Expected output is only what the sanctioned-adaptations table in `reference/github-setup.md` permits. Any other hunk is a finding — report it with the file and hunk, and restore from the template unless the diff is a deliberate, listed adaptation. If `templates/` can't be located, report the audit item as **not checked**; do not mark it passed.
- **Workflows behave, not just exist:** `pr-checks` runs on `pull_request_target`; `title-check` declares `needs: label`, and `version-gate` skips itself where the release tag sets the version; no job checks out the PR head (the version gate pins `base.sha` and reads the PR manifest over the API); no `${{ }}` appears inside any `run:`; bot authors are skipped; the only workflows opening PRs are `auto_draft_pr.yml` (draft-only, gated on `github.actor == github.repository_owner`) and any opener the repo built for itself, which must carry a `# skill-audit: sanctioned-opener` marker stating why; `release_drafter` runs on `push: main` and `release: published` — two events, one writer — with no second autolabeler; the version gate compares to the **last published release** and exempts `dependabot[bot]` with a **job-level** `if:`, and is advisory in a tag-driven repo.
- **Patterns applied:** `runtime_data` (not `hass.data[DOMAIN][entry_id]`) for entry state; coordinator `async_shutdown()` on unload; `async_remove_config_entry_device` present if the integration creates a device; `DeviceInfo` TypedDict; `_attr_has_entity_name = True`; typed `ConfigEntry` alias; modern `NotifyEntity` (or a directly-registered service for custom `data`).
- **`quality_scale.yaml` honest:** every canonical rule listed; every `exempt` carries a real `comment`; no optimistic `exempt` masking a gap (e.g. `stale-devices` exempt while a device *is* created); the `manifest.json` tier claimed only when every rule at/below it is `done`/`exempt`.
- **Tests mock the boundary:** a real setup-entry `LOADED` test exists (not just `async_setup_component`); the transport is mocked, not the integration's own functions; a two-entry parallel `LOADED` test exists if multiple devices are allowed; parsers have unit tests.
- **Commit/PR discipline:** subjects are single tight imperatives; the PR title uses a **labellable** type (`feat|fix|chore|docs`, `!` for breaking) — typed by a human, or derived from the commits by `auto_draft_pr.yml`; in an integration the release tag sets the version and no PR carries a bump, while a repo whose committed file is what consumers read bumps once, as the last commit.
- **Cached facts still true.** Re-derive any row in the **Freshness** table (`reference/freshness.md`) captured more than ~3 months ago, using the command in its *Re-derive with* column. Report each as still-current or stale-with-the-new-value, and update every consumer listed on that row in one pass. The stale-pin patterns in `skill_audit.py` are themselves a cached fact — check them against the action majors, not just the templates against the patterns.

**A green gate is not a green suite.** `skill_audit.py` checks that the canonical files
exist and inspects the content of a few (`pr-checks.yml`'s shape, the drafter wiring,
action pins). It never diffs a workflow against `templates/` — that is the byte-for-byte
item above — and it never runs the repo's tests. Eval 05 reached a passing audit while
`tests/test_version_sync.py` was still failing — from a stale template copy — and only
running `pytest` found it. Run what CI runs (`ruff`, `pyright`, `pytest`, `version_sync.py`)
before reporting an audit clean, and treat a failing test in a *copied* file as your copy
being stale, not as a skill bug to hand back.

**Verify copies per file, not per directory.** `diff -ru` on a tree still being assembled
can read as identical while individual files differ; `cmp` each copied file against its
template. Eval 05 found two additional drifted files this way after a directory diff had
already reported the copy clean.

**Report:** per-item pass/fail with `file:line` evidence · what the mechanical gate caught · remaining manual work. Fix findings before claiming the tier.

---

**Keep the gate in lockstep.** When this skill gains an antipattern or a canonical workflow, add the matching check to `scripts/skill_audit.py` in the same PR — the gate is only as current as its rules.
