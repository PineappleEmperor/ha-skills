# Commit, PR and merge discipline

Two behavioural rules with no artefact of their own: what to do when a check is red, and
what to do before naming a root cause. Commit and PR-body format is `reference/commits.md`.

- Merge discipline — never merge a red check
- One exception, and it is narrow
- Red flags — stop
- All of these mean: stop, read the log, fix or explain in writing first
- The exception gets misapplied
- Debugging discipline
- About to run `gh pr merge` while any check is red
- Diagnosing a failure **after** merging rather than before
- Reusing a previous exception without re-deriving why it applies
- Reaching for `--admin`, `--force`, or a `bypass_actors` entry to get a merge through
- Telling yourself the failure is "unrelated" without having read the log
- **Trace before naming a cause** — grep the path (publish → subscribe → handler), confirm in code; a pre-trace hunch is a guess, not the diagnosis.
- **Multi-entry service fan-out:** a `hass.services.async_call(DOMAIN, svc, …)` with no target loops **all** config entries. An entity action that should hit only its own device must pass its own `entry_id`/`device_id` and the handler must filter — default to "all" only for a deliberate bulk call.

---
