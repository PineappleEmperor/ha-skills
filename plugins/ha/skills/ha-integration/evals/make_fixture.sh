#!/usr/bin/env bash
# Build a throwaway fixture repo for an ha-integration eval scenario.
# Usage: ./make_fixture.sh <01|02|03> [dest]   — prints the fixture path.
set -euo pipefail

SCENARIO="${1:?usage: make_fixture.sh <01|02|03> [dest]}"
SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${2:-$(mktemp -d "${TMPDIR:-/tmp}/ha-eval-${SCENARIO}-XXXXXX")}"
DOMAIN=acmedev   # NOT a core domain: a custom `demo` is shadowed by core's

# The pins a fixture is built with. They are deliberately literal: a scenario tests
# whether an agent compares what it wrote against the source, not whether the pin is
# today's, and resolving them live would make the fixture need the network. Refresh
# them from each README's two `gh api` commands whenever a scenario needs a current one.
RF=8b41d48fc9bd3e7aea1d2ffdde98ca6205fdd16a   # release-flow v1.0.1
RF_TAG=v1.0.1
CI=c8b557e9f094cd855c5aecebf2edee8934d23fc4   # ha-integration-ci v1.0.0
CI_TAG=v1.0.0

# The seven caller workflows a scaffold carries, as their READMEs give them. A scenario
# that wants one drifted overwrites it afterwards.
write_callers() {
  mkdir -p .github/workflows
  cat > .github/workflows/pr-checks.yml <<YML
name: PR Checks

on:
  pull_request_target:
    types: [opened, reopened, synchronize, edited]

permissions:
  contents: read
  pull-requests: write

concurrency:
  group: pr-checks-\${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  pr:
    uses: PineappleEmperor/release-flow/.github/workflows/pr-checks.yml@$RF # $RF_TAG
YML
  cat > .github/workflows/lint-pr.yml <<YML
name: Lint PR

on:
  pull_request_target:
    types: [opened, edited, synchronize, reopened]

permissions: {}

jobs:
  lint:
    permissions:
      pull-requests: read
    uses: PineappleEmperor/release-flow/.github/workflows/lint-pr.yml@$RF # $RF_TAG
YML
  cat > .github/workflows/auto-draft-pr.yml <<YML
name: Draft PR

on:
  push:
    branches-ignore: [main]

permissions:
  contents: read

jobs:
  draft:
    uses: PineappleEmperor/release-flow/.github/workflows/auto-draft-pr.yml@$RF # $RF_TAG
    secrets:
      release-token: \${{ secrets.RELEASE_TOKEN }}
YML
  cat > .github/workflows/release-drafter.yml <<YML
name: Release Drafter

on:
  push:
    branches: [main]
  release:
    types: [published]

permissions:
  contents: write
  pull-requests: write

jobs:
  release:
    uses: PineappleEmperor/release-flow/.github/workflows/release-drafter.yml@$RF # $RF_TAG
YML
  cat > .github/workflows/python-validate.yml <<YML
name: Python Validate

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  validate:
    uses: PineappleEmperor/ha-integration-ci/.github/workflows/python-validate.yml@$CI # $CI_TAG
YML
  cat > .github/workflows/quality-audit.yml <<YML
name: Quality Audit

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  audit:
    uses: PineappleEmperor/ha-integration-ci/.github/workflows/quality-audit.yml@$CI # $CI_TAG
YML
  cat > .github/workflows/release.yml <<YML
name: Release

on:
  release:
    types: [published]

permissions:
  contents: write

jobs:
  release:
    uses: PineappleEmperor/ha-integration-ci/.github/workflows/release.yml@$CI # $CI_TAG
YML
}

mkdir -p "$DEST/custom_components/$DOMAIN"
cd "$DEST"

cat > "custom_components/$DOMAIN/manifest.json" <<JSON
{
  "domain": "$DOMAIN",
  "name": "Demo",
  "codeowners": ["@someone"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/someone/demo",
  "integration_type": "device",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/someone/demo/issues",
  "requirements": [],
  "version": "0.1.0"
}
JSON
printf '"""The Demo integration."""\n\nfrom __future__ import annotations\n' \
  > "custom_components/$DOMAIN/__init__.py"
printf 'rules:\n  config_flow: done\n' > "custom_components/$DOMAIN/quality_scale.yaml"
# filename MUST track $DOMAIN — release.yml attaches <domain>.zip and HACS
# downloads exactly this name. A stale literal here was caught by an eval run.
cat > hacs.json <<JSON
{"name": "Acme Dev", "zip_release": true, "content_in_root": false, "filename": "$DOMAIN.zip"}
JSON
# Output must stay clean: the caller does `F=$(make_fixture.sh …)`, so any git
# chatter on stdout (e.g. "nothing to commit" when a scenario adds no files)
# ends up in the captured path.
git init -q . >/dev/null 2>&1
git add -A && git -c user.email=e@x -c user.name=n commit -qm "chore: fixture" >/dev/null 2>&1

case "$SCENARIO" in
  01)
    # Scaffold-time: no CI at all, and the agent must not be able to reach
    # templates/. Isolation is the scenario's job (see the scenario file) —
    # this only guarantees nothing is pre-seeded here.
    ;;
  02)
    # Audit-time: a repo that passes the mechanical gate clean, with two planted
    # divergences that only a per-file comparison finds. The premise is the green
    # gate, so the base has to be a genuinely conforming repo — building one by hand
    # means enumerating 52 quality-scale rules and a brand icon, and re-enumerating
    # them every time the audit grows a check. The testbed IS that repo, so the
    # fixture takes it and plants the drift. History is stripped: the scenario is
    # about diffing against the templates and the READMEs, and a fixture that still
    # had its own `origin/main` would give the answer away with `git diff`.
    if ! git clone -q --depth 1 https://github.com/PineappleEmperor/ha-ci-testing .tb 2>/dev/null; then
      echo "scenario 02 needs to clone PineappleEmperor/ha-ci-testing" >&2
      exit 3
    fi
    rm -rf .tb/.git
    cp -R .tb/. . && rm -rf .tb
    rm -rf "custom_components/$DOMAIN"
    # Drift 1, in a file that is still copied byte-for-byte: hacs-validate rewritten
    # from its one-line description. It drops the daily schedule and the `category`
    # input, so the check runs on nothing and reports green.
    cat > .github/workflows/hacs-validate.yml <<'YML'
name: HACS Validation

on:
  pull_request:

permissions:
  contents: read

jobs:
  hacs:
    name: HACS validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: hacs/action@main
YML
    # Drift 2, the caller-model shape of the same mistake: the `uses:` is right, so
    # check_callers and check_action_pins both pass, but the trigger and permissions
    # were written from memory. Under `pull_request` a fork PR gets a read-only token,
    # so the labelling the called workflow does silently stops working on forks.
    cat > .github/workflows/pr-checks.yml <<'YML'
name: PR Checks

on:
  pull_request:
    types: [opened, reopened, synchronize, edited]

permissions:
  contents: read

jobs:
  pr:
    uses: PineappleEmperor/release-flow/.github/workflows/pr-checks.yml@8b41d48fc9bd3e7aea1d2ffdde98ca6205fdd16a # v1.0.1
YML
    ;;
  03)
    # First-test-time: integration + CI present, no tests/ and no pytest config.
    mkdir -p .github/workflows
    write_callers
    cp "$SKILL/templates/requirements.test.txt" .
    printf '[tool.ruff]\ntarget-version = "py314"\n' > pyproject.toml
    ;;
  *) echo "unknown scenario: $SCENARIO" >&2; exit 2 ;;
esac

git add -A && git -c user.email=e@x -c user.name=n commit -qm "chore: scenario $SCENARIO" >/dev/null 2>&1 || true
echo "$DEST"
