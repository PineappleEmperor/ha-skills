#!/usr/bin/env bash
# Build a throwaway fixture repo for an ha-integration eval scenario.
# Usage: ./make_fixture.sh <01|02|03> [dest]   — prints the fixture path.
set -euo pipefail

SCENARIO="${1:?usage: make_fixture.sh <01|02|03> [dest]}"
SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${2:-$(mktemp -d "${TMPDIR:-/tmp}/ha-eval-${SCENARIO}-XXXXXX")}"
DOMAIN=acmedev   # NOT a core domain: a custom `demo` is shadowed by core's

mkdir -p "$DEST/custom_components/$DOMAIN"
cd "$DEST"

cat > "custom_components/$DOMAIN/manifest.json" <<JSON
{
  "domain": "$DOMAIN",
  "name": "Demo",
  "codeowners": ["@someone"],
  "config_flow": true,
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
printf '{"name": "Demo", "zip_release": true, "content_in_root": false, "filename": "demo.zip"}\n' > hacs.json
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
    # Audit-time: a full CI stack that LOOKS right and passes skill_audit.sh,
    # but whose workflows were written from the prose rather than copied.
    mkdir -p .github/workflows scripts tests
    cp "$SKILL/templates/scripts/skill_audit.sh" scripts/
    cp "$SKILL/templates/scripts/manifest_gate.py" scripts/
    cp "$SKILL/templates/tests/test_manifest_gate.py" tests/
    cp "$SKILL/templates/conftest.py" .
    cat > pyproject.toml <<'TOML'
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
TOML
    # The premise is a repo that passes the mechanical gate, so the test wiring
    # has to be complete — the scenario is about paraphrase, not missing files.
    cp "$SKILL/templates/requirements.test.txt" .
    cp "$SKILL/templates/.github/dependabot.yml" "$SKILL/templates/.github/release-drafter.yml" .github/
    for w in "$SKILL"/templates/.github/workflows/*.yml; do
      cp "$w" ".github/workflows/$(basename "$w")"
    done
    sed -i "s|<domain>|$DOMAIN|g" .github/workflows/release.yml
    # The drift: lint_pr rewritten from the description. Drops
    # pull_request_target, the permissions block and the token env — all
    # invisible to a checklist that only asks "does the file exist".
    cat > .github/workflows/lint_pr.yml <<'YML'
name: Lint PR Title

on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  main:
    runs-on: ubuntu-latest
    steps:
      - uses: amannn/action-semantic-pull-request@v6
YML
    ;;
  03)
    # First-test-time: integration + CI present, no tests/ and no pytest config.
    mkdir -p .github/workflows
    cp "$SKILL/templates/.github/workflows/python_validate.yml" .github/workflows/
    cp "$SKILL/templates/requirements.test.txt" .
    printf '[tool.ruff]\ntarget-version = "py314"\n' > pyproject.toml
    ;;
  *) echo "unknown scenario: $SCENARIO" >&2; exit 2 ;;
esac

git add -A && git -c user.email=e@x -c user.name=n commit -qm "chore: scenario $SCENARIO" >/dev/null 2>&1 || true
echo "$DEST"
