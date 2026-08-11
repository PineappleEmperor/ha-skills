# 03 — test prerequisites · WITH skill · PASS

Date: 2026-08-11. Skill @ 6.0.3.

## Result: PASS on every criterion

- `conftest.py` at the REPO ROOT, copied byte-for-byte from the template, with
  `import custom_components` as its first statement — and correctly explained the
  binding race with p-h-c-c's bundled package. This is the criterion that
  distinguishes a pass from the plausible-looking failure.
- `asyncio_mode = "auto"` added to pyproject.toml.
- Correctly concluded no `pythonpath` was needed (the root conftest puts the repo
  on sys.path) — the guidance says this and the agent applied it rather than
  cargo-culting.
- Real setup-entry test: `MockConfigEntry` -> `hass.config_entries.async_setup`
  -> `assert entry.state is ConfigEntryState.LOADED`, explicitly rejecting the
  `async_setup_component` form the skill calls near-worthless. Plus an unload test.
- Verified by RUNNING pytest (4 passed), not by reading.

None of the documented failure modes occurred: conftest was not placed in
`tests/`, neither prerequisite was skipped, and it did not chase
"Integration not found" into the integration.

## Findings it produced — both real, both fixture defects of ours

1. Domain `demo` collides with an HA core integration. We knew (it is documented
   in the scenario's own notes) and shipped the fixture with it anyway.
2. `quality_scale.yaml` is a stub using non-canonical rule names.

It also added `.gitignore` unprompted, because the pytest run left `__pycache__`
that a `git add -A` would commit — arriving independently at the same defect a
human reviewer had raised hours earlier.
