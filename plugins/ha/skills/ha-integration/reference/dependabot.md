# Dependabot for a HA custom integration

What Dependabot can bump, what it cannot reach, and the two consequences it has for the
version gate and the release notes. Set up alongside `reference/github-setup.md`.

- Keeping `>=` floors current, which Dependabot cannot do
- Exemption from the version gate
- Pins in your repo versus pins in the templates

`.github/dependabot.yml` with `commit-message.prefix: "chore"` on each ecosystem (so titles read `chore: bump …` → the autolabeler maps `chore` → patch). Know what it actually buys you:

- **`github-actions`** — the real value. Bumps `actions/checkout`, `setup-python`, action pins across all workflows.
- **`pip`** — points at `requirements.test.txt` / `pyproject`. Real value now that the template ships `requirements.test.txt` **pinned** (`pytest-homeassistant-custom-component==…`); it stays near-useless in a repo that leaves test deps unpinned, since no version specifier means nothing to bump. ⚠️ A bump here effectively bumps the **HA version the suite tests against** — `pytest-homeassistant-custom-component` hard-pins `homeassistant==<matching release>` — so review these PRs rather than auto-merging: a bump can drag the Python floor with it, and the `python_validate.yml` `python-version`, ruff `target-version` and `pyrightconfig.json` must move in lockstep.
- **`manifest.json` `requirements` are invisible to Dependabot** — it can't parse the manifest, and the entries are open `>=` ranges (HA installs the latest matching anyway), so there's nothing to *routinely* bump. Raising a `>=` floor is a deliberate safety/feature act, not automation — **unless** you want the floors kept current.

### Keeping `>=` floors current, which Dependabot cannot do

a small `scripts/update_manifest_floors.py` (parse manifest requirements, query PyPI `…/pypi/{name}/json` for the latest non-prerelease, raise the floor if newer; `--check` to dry-run) plus a scheduled `update_manifest_floors.yml` (`schedule:` + `workflow_dispatch`) that runs it and — on a change — commits to a branch, pushes, and **opens its own PR** (`gh pr create`). `auto_draft_pr.yml` is the only opener shipped, so a floor-bumper must open its own PR — mark it `# skill-audit: sanctioned-opener` with the reason, or the audit rejects it; guard with `gh pr list --head <branch> --state open` so a re-run updates rather than duplicates. Give it a title with a mapped type (`chore:`) so the autolabeler still files it. The floor-bump PR needs **no manifest version bump** under the last-release gate model in `reference/versioning.md`.

---

### Exemption from the version gate

Dependabot PRs never touch `manifest.json`, and right after a release (`main` == last release) a no-bump PR equals the released version → the gate's "unchanged" rule trips. Exempt it with a **job-level** `if:` — `github.event.pull_request.user.login != 'dependabot[bot]'`. A skipped job satisfies a required status check, which GitHub states plainly and which this repo has since confirmed, so the merge is not blocked and the check reads "Skipped" rather than a green that proves nothing. There is no second run to fall back on — `pr-checks.yml` triggers on `pull_request_target` only. With this, Dependabot PRs fold into the next release with no bump, exactly as intended.

---

### Pins in your repo versus pins in the templates

Its
`github-actions` ecosystem only scans `.github/workflows` at the repo root. Your workflows
are therefore bumped for you once `dependabot.yml` is in place; the skill's `templates/`
are maintained separately, in the skill's own repo. **Consequence for you:** re-copying
from `templates/` can move a pin *backwards* if the skill's copies are older than what
Dependabot has already given you. Diff before overwriting, and keep the newer pin.
