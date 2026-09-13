# Dependabot for a HA custom integration

What Dependabot can bump, what it cannot reach, and why its PRs need no special handling.
Set up alongside `reference/github-setup.md`.

- Ecosystems worth enabling
- Dependabot needs no exemption
- Pins in your repo versus pins in the templates

### Ecosystems worth enabling

`.github/dependabot.yml` with `commit-message.prefix: "chore"` on each ecosystem, so titles read `chore: bump …` and the autolabeler files them (the mapping is release-flow's drafter config). Know what it actually buys you:

- **`github-actions`** — the real value. Bumps every `uses:` pin under `.github/workflows/`: the action pins in the four plain workflows and, more importantly, the callers' pins, which is how a release of a CI repository reaches you (the version model in ha-integration-ci's README).
- **`pip`** — points at `requirements.test.txt` / `pyproject`. Real value now that the template ships `requirements.test.txt` **pinned** (`pytest-homeassistant-custom-component==…`); it stays near-useless in a repo that leaves test deps unpinned, since no version specifier means nothing to bump. ⚠️ A bump here moves the **HA version the suite tests against** (`reference/testing.md` says why), so review these PRs rather than auto-merging: a bump can drag the Python floor with it, and your ruff `target-version` and `pyrightconfig.json` must then match the floor the CI declares — the audit compares them (ha-integration-ci's README) — and a floor move is a CI release first.
- **`manifest.json` `requirements` are invisible to Dependabot** — it can't parse the manifest, and the entries are open `>=` ranges (HA installs the latest matching anyway), so there's nothing to *routinely* bump. Raising a `>=` floor is a deliberate safety/feature act, done by hand in a PR of its own. Nothing in the stack automates it, and if something ever does it is a reusable workflow in ha-integration-ci — never a script and a PR opener written into one repo, which is the copied-body model the CI repositories replaced.

---

### Dependabot needs no exemption

Nothing compares a committed version, and the label gate skips bot-authored PRs. Dependabot
PRs carry a `chore` label from their `chore:` title, fold into the next release, and need no
special case anywhere.

---

### Pins in your repo versus pins in the templates

The callers carry no stored pin anywhere but your repo, so there is nothing to regress. The
four plain workflows have a template, so re-copying one can move its pin *backwards*; diff
before overwriting and keep the newer pin, the listed adaptation in
`reference/github-actions.md`.
