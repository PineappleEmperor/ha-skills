# Handover — workflow set review

Written 2026-08-31 at the end of a long session. Delete this file once the work it describes
has landed; it is session state, not repo documentation.

## Where things stand

- Branch `feat/reference-link-check`, [PR #65](https://github.com/PineappleEmperor/pineapple-claude-hacs/pull/65), remote and local both at `abd23a2` (verified by fetch, not by trusting push output).
- `python3 scripts/skill_audit.py` — passes.
- `python3 scripts/skill_meta_audit.py` — passes.
- `python3 -m pytest -q -p no:homeassistant` — 126 pass. **The flag is required locally**: this machine has pytest 9.0.3 alongside `pytest-homeassistant-custom-component` 0.13.355, whose autouse async fixture errors under pytest 9. CI is unaffected — `python_validate.yml` installs only `pytest pyyaml`.
- Everything below is already committed and pushed. Nothing is in flight.

## What this session decided, so it does not get relitigated

**The label is the only input to the released version.** Title → autolabeler → label →
release-drafter resolves the highest semver-increment → draft tag → publish → `release.yml`
writes it into `manifest.json`. Nothing downstream re-derives it.

**`CC label validation` is the gate.** It now compares the label the PR carries against the
one its *commits* entitle it to (`commit_summary.py --mode label`) and exits 1 on a mismatch.
Before, it only asked whether *a* label existed, warned, and exited 0 — so a `fix:`-titled PR
carrying a `feat!:` commit released a breaking change as a patch, and the required context
reported success.

**All three label contexts stay required.** They are a chain, not duplication:
`CC title validation` (type not in the allowlist), `CC labelling` (labelling machinery
failed), `CC label validation` (label present but wrong). An earlier recommendation to drop
two of them was wrong and has been reversed in the docs.

**`version-gate` is deleted.** Its comparisons were skipped in a tag-driven repo, its
breaking-marker rule moved into the label gate, and its "next release will be X" line was a
second implementation of what release-drafter already resolves. That line now lives in
`title-check`. **The Dependabot exemption went with it** — it existed only to keep that job
off bot PRs, and `title-check` already skips bots.

**Panel bundle rebuilds at release, not at merge.** `release.yml` rebuilds before packing the
zip, so users always install a fresh build. It cannot live in its own workflow: two workflows
on one `release: published` event cannot be ordered, so a separate rebuild could finish after
the zip was packed. `panel_bundle.yml` keeps the PR-time type-check, tests, and a
**non-blocking** staleness warning. Consequence: "the committed bundle must be fresh" is no
longer a merge gate.

**Renames:** `stale.yml` → `issue_stale.yml`, `frontend_build.yml` → `panel_bundle.yml`.
`issue_stale.yml` is kept — repo hygiene counts as an intent.

**`dependency_review` is canonical.** Its context is required by `ruleset.json`, so a repo
missing the workflow left the ruleset waiting forever.

## The defect worth remembering

`scripts/` and `templates/scripts/` are *different files*. The first is what this repo runs
and what the tests import; the second is what integrations receive. They drifted, and two
fixes — the GitHub App token pair and `dependency_review` becoming canonical — landed only in
the copy nobody ships, while the docs asserted they were fixed.

`check_template_scripts_match` now compares every `.py` under `templates/scripts/` and
`templates/tests/` against its counterpart byte-for-byte. It caught two further drifts while
the rest of this work was being done.

## Open, with the next step spelled out

1. **Trim `manifest_gate.py` to `--suggest`.** `evaluate()` is dead in the shipped stack and
   carries a comment saying so. Removing it also means removing much of
   `test_manifest_gate.py`. Approved in principle; deliberately not started late in a session.
   Decide first whether it stays for repos that genuinely gate a committed version.
2. **History squash and purge.** Agreed a while back, held until content settled. Tags moving
   is acceptable; the user does not care about tag positions in this repo. Do it after PR #65
   merges, or the branch gets rewritten too.
3. **Testbed `ha-ci-testing`.** `ruleset.json` is committed at its root (done this session).
   The ruleset itself is **not applied** — that needs `Administration: write`, which the user
   has declined to grant to the token. The `PLATFORMS`-without-module trap fires correctly
   there, which is the deliberate defect in that repo.
4. **Re-run scenario 06 arms A and C.** The router KAT passed 5/5, but A and C were answered
   from a line since removed ("work from this file alone"), and the oracle for E was edited
   before the run. See `evals/results/06-post-fix-pass.md` — the caveat is recorded there.
5. **Assess the HA MCP server's best-practice guides** — deferred, tracked in memory as
   `ha-mcp-best-practice-guides`. Unrelated to this repo's CI.

## How to work on this repo

Learned the hard way this session; ignoring these cost hours.

- **Read files, do not grep them.** Absence of a grep match is not evidence a thing is fixed.
  A `grep -c ""` "check" for blank runs counted lines and could never have found anything, and
  a grep that found only a job name led to reporting a still-live defect as resolved.
- **Never bulk-transform prose with a script.** A single bad transform gutted `discipline.md`
  from 663 words to 212. Read and edit by hand.
- **Audit and fix are separate passes.** Findings go in `docs/backlog.md` first; fixes come
  after, one issue per commit.
- **Verify by fetching back, not by asserting.** Both audits and the tests before every
  commit; `git fetch` to confirm a push rather than trusting its output.
- **A check you have not seen fail is not a check.** Each new check here was watched failing
  before being trusted.

## Environment gotchas

- `~/.gitconfig` was on the sandbox read deny-list for part of the session, which makes
  *every* git command abort with `fatal: unknown error occurred while reading the
  configuration files`. It has been allowed; if it recurs, `GIT_CONFIG_GLOBAL=/dev/null`
  works but drops `user.name`/`user.email`, so commits then need them passed per-invocation.
- Credential-storage lock warnings on push (`Read-only file system`) are noise; the ref still
  updates. Check with `git fetch`.
- The GitHub MCP server has no git-data endpoints, so it cannot push local commits. The git
  MCP server (`mcp-server-git`) has no push at all. Neither is a route around a git problem.
