#!/usr/bin/env bash
# Skill-conformance audit: verifies the ha-integration skill was actually followed —
# canonical workflows present, action pins current, antipatterns absent, quality_scale
# present. Mechanical subset of Mode 4. Exit 1 on any FAIL. Runs locally and in CI.
set -uo pipefail

CC=$(ls -d custom_components/*/ 2>/dev/null | head -1)
fail=0
FAIL() { echo "❌ FAIL: $*"; fail=1; }
WARN() { echo "⚠️  WARN: $*"; }

# --- Canonical workflows present ---
# release.yml: absent -> HACS install fails with "Could not download" on a
# zip_release repo. quality_audit.yml: absent -> THIS script never runs in CI,
# and that is the one absence it can never report on a PR.
for w in pr-checks release_drafter semantic_release lint_pr \
         hacs_validate hassfest_validate python_validate \
         release quality_audit; do
  [ -f ".github/workflows/$w.yml" ] || FAIL "missing .github/workflows/$w.yml"
done
[ -f .github/release-drafter.yml ] || FAIL "missing .github/release-drafter.yml"
[ -f .github/dependabot.yml ]      || FAIL "missing .github/dependabot.yml"

# --- Canonical scripts present (pr-checks.yml's version-gate job shells out to
# the gate; a missing script fails that job at runtime on every PR) ---
[ -f scripts/manifest_gate.py ]      || FAIL "missing scripts/manifest_gate.py (pr-checks.yml's version-gate shells out to it)"
[ -f tests/test_manifest_gate.py ]   || FAIL "missing tests/test_manifest_gate.py (the gate's logic must stay unit-tested)"

# NOTE: this loop proves each workflow EXISTS, never that it MATCHES the skill's
# template — a consuming repo has no copy of templates/ to diff against. Content
# fidelity is the first item of the Mode 4 judgement checklist, run by an agent
# that does have the skill on disk. Green here is not evidence of a faithful copy.

# --- CI actually runs the tests ---
if [ -d tests ]; then
  [ -f requirements.test.txt ] \
    || FAIL "tests/ exists but requirements.test.txt is missing (pytest step cannot install the suite)"
  # Root conftest, not tests/conftest: it must import `custom_components` before
  # p-h-c-c binds that name to its own bundled package, or HA can't find the
  # integration and every setup test fails with "Integration not found".
  if [ -f conftest.py ]; then
    grep -q '^import custom_components' conftest.py \
      || FAIL "conftest.py does not import custom_components (HA will not discover the integration)"
    grep -q 'enable_custom_integrations' conftest.py \
      || FAIL "conftest.py does not pull in enable_custom_integrations"
  else
    FAIL "missing root conftest.py (must be at the repo root, not tests/conftest.py)"
  fi
  grep -qE 'asyncio_mode[[:space:]]*=[[:space:]]*"auto"' pyproject.toml 2>/dev/null \
    || FAIL "pyproject.toml missing asyncio_mode = \"auto\" (async tests never run)"
  grep -q 'pytest' .github/workflows/python_validate.yml 2>/dev/null \
    || FAIL "python_validate.yml has no pytest step (quality_scale 'done' rules would go unproven)"
else
  WARN "no tests/ directory — every quality_scale rule marked 'done' is unproven"
fi
if [ -f requirements.test.txt ]; then
  grep -qE 'pytest-homeassistant-custom-component[[:space:]]*==' requirements.test.txt \
    || WARN "pytest-homeassistant-custom-component is unpinned (it hard-pins the HA version the suite tests against)"
fi

# --- Action pins current (stale majors Dependabot would immediately bump) ---
# ⚠️ These majors are a snapshot, verified 2026-08-07. They rot silently: a rule
# written for "flag v1-v5" keeps passing a v6 pin long after v7 ships, so the
# check meant to catch staleness goes stale in the same place. Re-derive with:
#   for r in actions/checkout actions/setup-python softprops/action-gh-release \
#            amannn/action-semantic-pull-request release-drafter/release-drafter; do
#     echo "$r $(gh api repos/$r/releases/latest --jq .tag_name)"; done
# and update BOTH the pattern here and the pin in the templates. See the
# Freshness table in SKILL.md.
grep -rnE 'actions/checkout@v[1-6]\b'                    .github/workflows/ && FAIL "stale actions/checkout (use v7)"
grep -rnE 'actions/setup-python@v[1-6]\b'                .github/workflows/ && FAIL "stale actions/setup-python (use v7)"
grep -rnE 'softprops/action-gh-release@v[12]\b'          .github/workflows/ && FAIL "stale action-gh-release (use v3)"
grep -rnE 'amannn/action-semantic-pull-request@v[1-5]\b' .github/workflows/ && FAIL "stale semantic-pull-request (use v6)"
grep -rnE 'release-drafter/release-drafter(/autolabeler)?@v[1-6]\b' .github/workflows/ && FAIL "stale release-drafter (use v7)"

# --- Workflow correctness ---
grep -q "Remove superseded" .github/workflows/pr-checks.yml 2>/dev/null \
  || FAIL "pr-checks.yml missing the removal-only superseded-label step"
grep -q "dependabot\[bot\]" .github/workflows/pr-checks.yml 2>/dev/null \
  || WARN "pr-checks.yml may not exempt dependabot[bot] from the version gate"
grep -q "gh release list" .github/workflows/pr-checks.yml 2>/dev/null \
  || WARN "pr-checks.yml may not compare against the last published release"

# --- pr-checks.yml: ordering and pull_request_target safety ---
# Jobs that read labels must declare `needs: label`. Separate workflows cannot be
# sequenced at all (the autolabeler's `labeled` event is suppressed by the
# GITHUB_TOKEN anti-recursion rule), which is why these live in one workflow.
if [ -f .github/workflows/pr-checks.yml ]; then
  P=.github/workflows/pr-checks.yml
  grep -q 'pull_request_target' "$P" \
    || FAIL "pr-checks.yml must use pull_request_target (fork PRs get a read-only token otherwise)"
  [ "$(grep -c 'needs: label' "$P")" -ge 2 ] \
    || FAIL "pr-checks.yml: label-reading jobs must declare 'needs: label' (else they race the autolabeler)"
  grep -q "user.type != 'Bot'" "$P" \
    || FAIL "pr-checks.yml does not skip bot-authored PRs"
  # Any checkout under pull_request_target must pin the BASE, never the PR head:
  # the token is writable, so PR-authored code must never run.
  if grep -q 'actions/checkout' "$P"; then
    grep -q 'ref: ${{ github.event.pull_request.base.sha }}' "$P" \
      || FAIL "pr-checks.yml checks out without pinning base.sha (never run PR code under pull_request_target)"
    grep -q 'head.sha' "$P" && grep -A2 'actions/checkout' "$P" | grep -q 'head.sha' \
      && FAIL "pr-checks.yml checks out the PR head under pull_request_target"
  fi
  # Untrusted strings (PR title, the PR's own manifest version) must reach run: via
  # env, never `${{ }}` interpolation.
  python3 - "$P" <<'PYCHK' || FAIL "pr-checks.yml interpolates \${{ }} inside a run: block (use env:)"
import sys, re, yaml
w = yaml.safe_load(open(sys.argv[1]))
bad = [(j, s.get("name"), m)
       for j, jd in w["jobs"].items() for s in jd["steps"]
       for m in re.findall(r"\$\{\{\s*([^}]+?)\s*\}\}", s.get("run", ""))]
for b in bad:
    print(f"    {b}")
sys.exit(1 if bad else 0)
PYCHK
fi

# No workflow may open PRs. create-dev-pr.yml is the superseded auto-opener: it cannot
# serve fork contributions (push never fires on a fork; a fork's pull_request token is
# read-only) and it overwrote human PR titles. PRs are opened by humans.
[ -f .github/workflows/create-dev-pr.yml ] \
  && FAIL "create-dev-pr.yml is superseded (PRs are opened manually; use pr-checks.yml)"
grep -rln 'gh pr create' .github/workflows/ 2>/dev/null \
  && FAIL "a workflow opens PRs with 'gh pr create' (PRs are opened manually)"

# --- Antipatterns in integration code (high-confidence) ---
if [ -n "$CC" ]; then
  ap() { grep -rnE "$1" "$CC" 2>/dev/null && FAIL "$2"; }
  ap 'discovery\.async_load_platform' "deprecated discovery.async_load_platform (use NotifyEntity / platform forward)"
  ap 'BaseNotificationService'         "deprecated BaseNotificationService (use NotifyEntity)"
  ap 'update_before_add=True'          "update_before_add=True (populate via property or _handle_coordinator_update)"
  ap 'OptionsFlowHandler'              "deprecated OptionsFlowHandler name (use OptionsFlow)"
  ap 'PlatformNotReady'                "PlatformNotReady in a config-entry integration (use ConfigEntryNotReady)"
  ap '_LOGGER\.[a-z]+\([[:space:]]*f"' "f-string in a logging call (use lazy % args — ruff G004)"
  ti=$(grep -rn '# type: ignore' "$CC" 2>/dev/null | grep -v 'import-untyped')
  [ -n "$ti" ] && { echo "$ti"; FAIL "bare # type: ignore (Platinum: only [import-untyped] with a reason)"; }
  grep -rq 'from __future__ import annotations' "$CC"__init__.py 2>/dev/null \
    || WARN "no 'from __future__ import annotations' in __init__.py"

  # --- quality_scale + manifest honesty ---
  [ -f "${CC}quality_scale.yaml" ] || FAIL "missing quality_scale.yaml"
  M="${CC}manifest.json"
  grep -q '"integration_type"' "$M" 2>/dev/null || FAIL "manifest.json missing integration_type"
  grep -q '"issue_tracker"'    "$M" 2>/dev/null || FAIL "manifest.json missing issue_tracker (HACS requires it)"
fi

[ "$fail" = 0 ] && { echo "✅ skill audit passed"; exit 0; } || { echo "skill audit FAILED"; exit 1; }
