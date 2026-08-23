# Dependabot for a HA custom integration

What Dependabot can bump, what it cannot reach, and the two consequences it has for the
version gate and the release notes. Set up alongside `reference/github-setup.md`.

`.github/dependabot.yml` with `commit-message.prefix: "chore"` on each ecosystem (so titles read `chore: bump …` → the autolabeler maps `chore` → patch). Know what it actually buys you:

- **`github-actions`** — the real value. Bumps `actions/checkout`, `setup-python`, action pins across all workflows.
- **`pip`** — points at `requirements.test.txt` / `pyproject`. Real value now that the template ships `requirements.test.txt` **pinned** (`pytest-homeassistant-custom-component==…`); it stays near-useless in a repo that leaves test deps unpinned, since no version specifier means nothing to bump. ⚠️ A bump here effectively bumps the **HA version the suite tests against** — `pytest-homeassistant-custom-component` hard-pins `homeassistant==<matching release>` — so review these PRs rather than auto-merging: a bump can drag the Python floor with it, and the `python_validate.yml` matrix, ruff `target-version` and `pyrightconfig.json` must move in lockstep.
- **`manifest.json` `requirements` are invisible to Dependabot** — it can't parse the manifest, and the entries are open `>=` ranges (HA installs the latest matching anyway), so there's nothing to *routinely* bump. Raising a `>=` floor is a deliberate safety/feature act, not automation — **unless** you want the floors kept current.

**Keeping `>=` floors current (custom, since Dependabot can't):** a small `scripts/update_manifest_floors.py` (parse manifest requirements, query PyPI `…/pypi/{name}/json` for the latest non-prerelease, raise the floor if newer; `--check` to dry-run) plus a scheduled `update_manifest_floors.yml` (`schedule:` + `workflow_dispatch`) that runs it and — on a change — commits to a branch, pushes, and **opens its own PR** (`gh pr create`). Since no workflow opens PRs generally, this one must do it itself — mark it `# skill-audit: sanctioned-opener` with the reason, or the audit rejects it; guard with `gh pr list --head <branch> --state open` so a re-run updates rather than duplicates. Give it a title with a mapped type (`chore:`) so the autolabeler still files it. The floor-bump PR needs **no manifest version bump** under the last-release gate model above.

**Two Dependabot consequences, both covered above:** the **version gate** must compare against the last release and **exempt `dependabot[bot]`** (see the versioning section), and Dependabot's PR body no longer reaches the notes at all, since they are built from commit subjects; its `chore: bump …` subject is classified as Maintenance like any other commit.

---
