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
# Split by what actually needs an integration. Run whole against a repo that has no
# custom_components/ and the integration-only rows fire as false positives; a report
# that is mostly noise gets waved away, which is how a real pull_request_target
# finding sat unread in this very output.
for w in pr-checks release_drafter semantic_release lint_pr \
         python_validate quality_audit; do
  [ -f ".github/workflows/$w.yml" ] || FAIL "missing .github/workflows/$w.yml"
done
if [ -n "$CC" ]; then
  for w in hacs_validate hassfest_validate release; do
    [ -f ".github/workflows/$w.yml" ] || FAIL "missing .github/workflows/$w.yml"
  done
else
  echo "ℹ️  no custom_components/ — skipping integration-only checks (HACS, hassfest, zip release, HA test harness)"
fi
[ -f .github/release-drafter.yml ] || FAIL "missing .github/release-drafter.yml"
[ -f .github/dependabot.yml ]      || FAIL "missing .github/dependabot.yml"
[ -f .gitignore ]                  || FAIL "missing .gitignore (copy templates/.gitignore)"

# Build artefacts must never be tracked. A committed .pyc under templates/ is
# copied verbatim into every scaffolded repo — a stale compiled conftest, tagged
# for one Python/pytest version. This has happened: `git add -A` after a local
# pytest run committed three of them.
if git rev-parse --git-dir >/dev/null 2>&1; then
  tracked_pyc=$(git ls-files | grep -E '__pycache__|\.py[cod]$' || true)
  [ -n "$tracked_pyc" ] && { echo "$tracked_pyc"; FAIL "compiled Python artefacts are tracked (git rm --cached, and add them to .gitignore)"; }
fi

# --- Canonical scripts present (pr-checks.yml's version-gate job shells out to
# the gate; a missing script fails that job at runtime on every PR) ---
[ -f scripts/manifest_gate.py ]      || FAIL "missing scripts/manifest_gate.py (pr-checks.yml's version-gate shells out to it)"
[ -f tests/test_manifest_gate.py ]   || FAIL "missing tests/test_manifest_gate.py (the gate's logic must stay unit-tested)"
[ -f scripts/commit_summary.py ]     || FAIL "missing scripts/commit_summary.py (pr-checks.yml's commit-summary shells out to it)"
# The release description is the artefact users read. Nothing checked it until a
# malformed block shipped in several releases while every other gate stayed green.
[ -f scripts/release_notes.py ]      || FAIL "missing scripts/release_notes.py (release notes would be grouped by PR label, filing fixes under Features)"
[ -f scripts/check_release_notes.py ] || FAIL "missing scripts/check_release_notes.py (nothing would verify the release description renders)"

# Both scripts shipped, both sat unused: release_drafter.yml ran the drafter and
# stopped, so every release used $CHANGES while the audit passed on file presence.
# Presence is not wiring.
# Every script this skill SHIPS must be invoked by some workflow. Presence was
# checked one script at a time, by hand, and each grep was added only after that
# script had already shipped unwired: release_notes.py generated nothing for three
# releases and manifest_gate.py sat unreferenced in the skill's own repo.
#
# Match `run:` bodies only. A plain grep over the workflow files counts a mention in
# a COMMENT as an invocation, which is the same mistake one level up: checking for a
# string rather than for the thing actually running.
#
# A repo's own developer utilities are a normal category and must not trip this, so
# they opt out with a marker. The marker is ignored for the scripts this skill ships
# — otherwise it would switch off the very wiring check it exists to enforce.
if [ -d scripts ] && [ -d .github/workflows ]; then
  python3 - <<'PYWIRE' || fail=1
import pathlib, sys, yaml

SHIPPED = {"manifest_gate.py", "commit_summary.py", "release_notes.py",
           "check_release_notes.py", "skill_audit.sh"}

runs = []
for wf in pathlib.Path(".github/workflows").glob("*.y*ml"):
    try:
        doc = yaml.safe_load(wf.read_text()) or {}
    except yaml.YAMLError:
        continue
    for job in (doc.get("jobs") or {}).values():
        for step in (job or {}).get("steps", []) or []:
            runs.append(str((step or {}).get("run", "")))

# Shell comments live INSIDE run: bodies, and pr-checks.yml explains manifest_gate.py
# in one. Matching the raw body counts that explanation as an invocation, so drop
# comment lines first. A trailing inline comment is not stripped; that would need a
# shell parser, and a name appearing only there is not a realistic false pass.
body = "\n".join(
    line for r in runs for line in r.splitlines()
    if not line.lstrip().startswith("#"))

bad = False
for s in sorted(pathlib.Path("scripts").glob("*")):
    if s.suffix not in (".py", ".sh") or not s.is_file():
        continue
    if s.name in body:
        continue
    if s.name in SHIPPED:
        print(f"❌ FAIL: scripts/{s.name} ships with this skill but no workflow step "
              f"runs it (the check it performs never runs)")
        bad = True
        continue
    marked = any(line.lstrip().startswith("#") and "skill-audit: local-tool" in line
                 for line in s.read_text(errors="replace").splitlines())
    if not marked:
        print(f"❌ FAIL: scripts/{s.name} is not run by any workflow step. If it is a "
              f"developer utility rather than a CI check, add a comment line "
              f"'# skill-audit: local-tool' anywhere in it")
        bad = True
sys.exit(1 if bad else 0)
PYWIRE
fi

# Exactly one thing may write the release body. Two did, and on a tagged release they
# raced: the published notes carried GitHub's `What's Changed` beneath the grouped
# sections. check_release_notes.py cannot catch that — it runs inside the workflow
# that writes first, so it validates a body that is still correct at the time.
# Counts every writer: `gh release edit --notes*`, `generate_release_notes: true`, and
# an explicit `body:` on a release action. The generate-notes API only renders a body,
# so it is not a writer.
if [ -d .github/workflows ]; then
  python3 - <<'PYBODY' || fail=1
import pathlib, re, sys, yaml

writers = []
for wf in pathlib.Path(".github/workflows").glob("*.y*ml"):
    try:
        doc = yaml.safe_load(wf.read_text()) or {}
    except yaml.YAMLError:
        continue
    for jn, job in (doc.get("jobs") or {}).items():
        for step in (job or {}).get("steps", []) or []:
            step = step or {}
            run = str(step.get("run", ""))
            live = "\n".join(l for l in run.splitlines() if not l.lstrip().startswith("#"))
            if re.search(r"gh release (edit|create)[^\n]*--notes", live):
                writers.append(f"{wf.name}:{jn} (gh release --notes)")
            with_ = step.get("with") or {}
            if str(with_.get("generate_release_notes", "")).lower() == "true":
                writers.append(f"{wf.name}:{jn} (generate_release_notes)")
            if "body" in with_ or "body_path" in with_:
                writers.append(f"{wf.name}:{jn} (body)")

if len(writers) > 1:
    print("❌ FAIL: more than one workflow step writes the release body; they race and "
          "the published notes end up containing both:")
    for w in writers:
        print(f"    {w}")
    sys.exit(1)
sys.exit(0)
PYBODY
fi

# The previous tag must exclude the release being written. `gh release list --limit 1`
# is correct for the version gate, which runs while the current version is unreleased,
# and wrong here: on `release: published` it returns the tag being published, so the
# range is empty and the body renders `_No user-facing changes._`. v7.2.0 shipped that
# way — the draft written on push was right, the publish overwrote it. Two halves that
# must agree, moved apart: the trigger changed, the tag lookup did not.
if [ -f .github/workflows/release_drafter.yml ]; then
  python3 - <<'PYPREV' || fail=1
import pathlib, re, sys, yaml

wf = pathlib.Path(".github/workflows/release_drafter.yml")
text = wf.read_text()
doc = yaml.safe_load(text) or {}
on = doc.get(True) or doc.get("on") or {}
if "release" not in on:
    sys.exit(0)
for step in (s for j in (doc.get("jobs") or {}).values() for s in (j or {}).get("steps", []) or []):
    run = str((step or {}).get("run", ""))
    if "release_notes.py" not in run:
        continue
    prev = next((l for l in run.splitlines() if re.match(r"\s*PREV=", l)), "")
    if "--limit 1 " in prev or prev.rstrip().endswith("--limit 1"):
        print("❌ FAIL: release_drafter.yml resolves the previous tag with `--limit 1` while "
              "triggering on `release: published`; that returns the release being written and "
              "the notes come out empty. Exclude the current tag.")
        sys.exit(1)
sys.exit(0)
PYPREV
fi

# A zip_release repo must patch the manifest version from the tag. HACS installs the
# asset, so an unpatched zip ships whatever version the last PR happened to commit —
# users then see the old version after updating, and nothing in CI notices because
# hassfest only reads the repo copy. frenck/spook patches from `release: published`.
if [ -f hacs.json ] && [ -f .github/workflows/release.yml ]; then
  if grep -q '"zip_release"[[:space:]]*:[[:space:]]*true' hacs.json; then
    grep -q 'manifest.json' .github/workflows/release.yml \
      || FAIL "release.yml builds a zip_release asset without setting the manifest version from the tag (see templates/.github/workflows/release.yml)"
  fi
fi

# `labeled`/`unlabeled` plus `cancel-in-progress` is a merge deadlock. Our autolabeler
# cannot fire those events (the default token suppresses them), but Dependabot can:
# it applies several labels at once, each starting a run, and the concurrency group
# cancels all but the last. CANCELLED check-runs make the rollup FAILURE even though
# nothing failed, and a required-checks ruleset then refuses the merge. Verified on
# ha-lego #22: mergeable MERGEABLE, rollup FAILURE, three cancelled contexts.
# Re-running one cancelled run flipped the rollup to SUCCESS with no other change,
# which is what proves it was the cancellations and not the skipped jobs.
#
# A SKIPPED job is fine and does satisfy a required check — do not "fix" that.
if [ -f .github/workflows/pr-checks.yml ]; then
  python3 - <<'PYCANCEL' || fail=1
import pathlib, sys, yaml

doc = yaml.safe_load(pathlib.Path(".github/workflows/pr-checks.yml").read_text()) or {}
on = doc.get(True) or doc.get("on") or {}
types = set((on.get("pull_request_target") or on.get("pull_request") or {}).get("types", []))
cancels = bool((doc.get("concurrency") or {}).get("cancel-in-progress"))
hazard = types & {"labeled", "unlabeled"}
if hazard and cancels:
    print(f"❌ FAIL: pr-checks.yml triggers on {sorted(hazard)} with "
          f"cancel-in-progress. A bot applying several labels starts a run per label; "
          f"the cancelled ones make the status rollup FAILURE and the PR unmergeable. "
          f"Drop those types — the in-workflow autolabeler cannot fire them anyway.")
    sys.exit(1)
sys.exit(0)
PYCANCEL
fi

RD=.github/workflows/release_drafter.yml
if [ -f "$RD" ]; then
  grep -q 'scripts/release_notes.py' "$RD" \
    || FAIL "$RD never runs scripts/release_notes.py (notes fall back to release-drafter's \$CHANGES, grouped by PR label)"
  grep -q 'scripts/check_release_notes.py' "$RD" \
    || FAIL "$RD never runs scripts/check_release_notes.py (a malformed release description would ship unnoticed)"
  # release_notes.py resolves a tag..HEAD range; checkout is depth 1 by default and
  # the range dies with "unknown revision".
  grep -q 'fetch-depth: 0' "$RD" \
    || FAIL "$RD checks out at depth 1; release_notes.py cannot resolve its commit range without fetch-depth: 0"
fi
[ -f tests/test_commit_summary.py ]  || FAIL "missing tests/test_commit_summary.py (the classifier must stay unit-tested)"
# Classifier logic must NOT be inlined back into the workflow: an inline heredoc
# cannot be unit-tested, and a wrong classifier corrupts release notes silently
# rather than failing a build. That is how the semver-bump regression shipped.
grep -q 'MAINT = ' .github/workflows/pr-checks.yml 2>/dev/null \
  && FAIL "pr-checks.yml inlines the commit classifier (call scripts/commit_summary.py instead)"

# NOTE: this loop proves each workflow EXISTS, never that it MATCHES the skill's
# template — a consuming repo has no copy of templates/ to diff against. Content
# fidelity is the first item of the Mode 4 judgement checklist, run by an agent
# that does have the skill on disk. Green here is not evidence of a faithful copy.

# --- Evidence must match the claim ---
# SKILL.md: "every rule you mark `done` must have a test that exercises it... If a
# rule is genuinely untestable it should be `exempt` with a comment, not an
# unproven `done`." Gate on the CLAIM, not on the presence of tests:
#   no `done` rules  -> nothing is claimed, nothing to prove, stay silent
#   any `done` rule  -> tests must exist, or the claim is unproven -> FAIL
# The previous rule was backwards: it warned at a fresh scaffold (claiming nothing,
# doing nothing wrong) and stayed quiet on a repo marking everything `done` with no
# tests at all — exactly the false claim the skill forbids.
DONE_RULES=0
QS_DONE_TESTCOV=no
if [ -n "$CC" ] && [ -f "${CC}quality_scale.yaml" ]; then
  DONE_RULES=$(python3 -c "
import sys, yaml
rules = (yaml.safe_load(open(sys.argv[1])) or {}).get('rules') or {}
def status(v): return v if isinstance(v, str) else (v or {}).get('status')
print(sum(1 for v in rules.values() if status(v) == 'done'))" "${CC}quality_scale.yaml" 2>/dev/null || echo 0)
  QS_DONE_TESTCOV=$(python3 -c "
import sys, yaml
rules = (yaml.safe_load(open(sys.argv[1])) or {}).get('rules') or {}
v = rules.get('test-coverage')
print('yes' if (v if isinstance(v, str) else (v or {}).get('status')) == 'done' else 'no')" "${CC}quality_scale.yaml" 2>/dev/null || echo no)
fi

# A panel's presentation logic is part of test-coverage: nothing else can reach it.
# Claiming test-coverage done while the panel is untested is the same unproven claim.
if [ "$QS_DONE_TESTCOV" = yes ] && [ -d frontend ]; then
  [ -n "$(find frontend/src frontend/test -name '*.test.ts' -o -name '*.spec.ts' 2>/dev/null)" ] \
    || FAIL "quality_scale marks test-coverage done, but the panel has no frontend tests (its presentation logic is reachable from nothing else — see the panel section of SKILL.md)"
fi

# --- CI actually runs the tests ---
if [ -d tests ] && [ -n "$CC" ]; then
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
elif [ "$DONE_RULES" -gt 0 ]; then
  FAIL "quality_scale marks $DONE_RULES rule(s) done but there is no tests/ directory — a done without a test is a claim, not evidence (mark them todo, or exempt with a comment)"
fi
if [ -f requirements.test.txt ] && [ -n "$CC" ]; then
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
  # actions/checkout CLEARS the workspace, so a job that checks out after writing
  # a file there loses it. That shipped: the commit-summary job fetched subjects
  # into subjects.txt, then checked out, then read a file that no longer existed.
  python3 - "$P" <<'PYCO' || FAIL "pr-checks.yml: actions/checkout must be the FIRST step of its job (it clears the workspace)"
import sys, yaml
w = yaml.safe_load(open(sys.argv[1]))
bad = [j for j, jd in w["jobs"].items()
       if any("actions/checkout" in str(s.get("uses", "")) for s in jd["steps"])
       and "actions/checkout" not in str(jd["steps"][0].get("uses", ""))]
for j in bad:
    print(f"    job '{j}' checks out after another step has run")
sys.exit(1 if bad else 0)
PYCO
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

# --- No HACS/hassfest check may be ignored ---
# `ignore:` disqualifies the repo from the HACS default store; it exists for
# debugging only. Empirically load-bearing: in eval scenario 01, BOTH control
# runs (skill withheld) reached for `ignore: brands` to make a failing check pass
# on day one, each rationalising it as temporary. Neither would have shipped to
# the default store. The rule was documented from the start and ungated until now.
for w in ${CC:+hacs_validate hassfest_validate}; do
  f=".github/workflows/$w.yml"
  [ -f "$f" ] || continue
  grep -nE '^[[:space:]]*ignore:' "$f" \
    && FAIL "$w.yml sets ignore: — ignoring any check disqualifies the repo from the HACS default store"
done

# --- The checks must actually be able to block a merge ---
# Every workflow here is ADVISORY until the default branch requires it. A repo can
# have the whole gate stack green-or-red and still merge either way, which makes the
# architecture decorative. Needs a token that can read rulesets, so it degrades to a
# WARN when unavailable rather than failing a local run.
if command -v gh >/dev/null 2>&1; then
  REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null || echo "")}"
  branch=""
  [ -n "$REPO" ] && branch=$(gh api "repos/$REPO" --jq .default_branch 2>/dev/null || echo "")
  if [ -n "$branch" ]; then
    rules=$(gh api "repos/$REPO/rules/branches/$branch" --jq '[.[].type]' 2>/dev/null || echo "")
    if [ -z "$rules" ]; then
      WARN "could not read branch rules for $branch (token lacks permission?) — verify required status checks by hand"
    else
      printf '%s' "$rules" | grep -q required_status_checks \
        || FAIL "no required status checks on $branch — every workflow in this stack is advisory and a red PR can be merged (see 'Make the checks REQUIRED' in SKILL.md)"
      printf '%s' "$rules" | grep -q non_fast_forward \
        || WARN "force-pushes to $branch are not blocked"
      # An admin bypass of `always` means a required check stops nobody who holds admin.
      gh api "repos/$REPO/rulesets" --jq '.[].id' 2>/dev/null | while read -r rid; do
        gh api "repos/$REPO/rulesets/$rid" --jq '.bypass_actors[]? | select(.bypass_mode=="always") | .actor_type' 2>/dev/null
      done | grep -q . \
        && WARN "a ruleset grants bypass_mode: always — required checks do not constrain anyone holding that role"
    fi
  fi
fi

# --- Exactly ONE labeler ---
# pr-checks.yml's `label` job is it. A second labeler (classically a
# release-drafter autolabeler job on pull_request) makes labels flap AND breaks
# pr-checks' `needs: label` ordering: title-check waits for the first labeler
# while the second is still applying labels. This drifted into the skill's own
# repo and went unnoticed until a manual template diff.
if [ -f .github/workflows/release_drafter.yml ]; then
  python3 - .github/workflows/release_drafter.yml <<'PYRD' || FAIL "release_drafter.yml must be push-only with no autolabeler job (pr-checks.yml is the sole labeler)"
import sys, yaml
w = yaml.safe_load(open(sys.argv[1]))
triggers = set((w.get(True) or w.get("on") or {}))
bad = []
# `release` is expected: a push maintains the draft, and `release: published` is the
# last writer for both the draft-published and tag-pushed paths, so the body is
# written once. Anything else here would be a second writer racing it.
if triggers - {"push", "workflow_dispatch", "release"}:
    bad.append(f"triggers {sorted(triggers)} (expected push and release only)")
for name, jd in w.get("jobs", {}).items():
    if "label" in name.lower():
        bad.append(f"job '{name}' looks like a second labeler")
for b in bad:
    print(f"    {b}")
sys.exit(1 if bad else 0)
PYRD
fi

# Only two workflows may open PRs, and only in the shapes below. create-dev-pr.yml is
# the superseded auto-opener: it overwrote human PR titles and opened with the default
# token, so no checks ran and the PR could never merge.
#
# Permitted: auto_draft_pr.yml (draft only, gated on the actor being the repo owner, so
# a PR opened with RELEASE_TOKEN cannot appear to be written by someone else) and
# update_manifest_floors.yml (nothing else can open a PR for a scheduled floor bump).
# Neither can serve fork contributions — push never fires on a fork and a fork's token
# is read-only — so fork contributors still open their own.
[ -f .github/workflows/create-dev-pr.yml ] \
  && FAIL "create-dev-pr.yml is superseded (use auto_draft_pr.yml, which is draft-only and actor-gated)"
for wf in $(grep -rln 'gh pr create' .github/workflows/ 2>/dev/null); do
  case "$(basename "$wf")" in
    auto_draft_pr.yml|update_manifest_floors.yml) ;;
    *) FAIL "$wf opens PRs with 'gh pr create' (only auto_draft_pr.yml and update_manifest_floors.yml may)" ;;
  esac
done
if [ -f .github/workflows/auto_draft_pr.yml ]; then
  grep -q 'github.actor == github.repository_owner' .github/workflows/auto_draft_pr.yml \
    || FAIL "auto_draft_pr.yml must gate on the actor being the repo owner, or it opens PRs that impersonate the token owner"
  grep -q -- '--draft' .github/workflows/auto_draft_pr.yml \
    || FAIL "auto_draft_pr.yml must open the PR as a draft"
fi

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
  if [ -f "${CC}quality_scale.yaml" ]; then
    # Existence proved nothing: a file containing one rule passed a real audit
    # while ~51 canonical rules were absent and that one rule was an unproven
    # `done`. Snapshot of the canonical set — keep in lockstep with the rule
    # lists in SKILL.md (see its Freshness table).
    python3 - "${CC}quality_scale.yaml" <<'PYQS' || FAIL "quality_scale.yaml does not enumerate the canonical rule set"
import sys, yaml
CANON = {
 "action-setup","appropriate-polling","brands","common-modules","config-flow-test-coverage",
 "config-flow","dependency-transparency","docs-actions","docs-high-level-description",
 "docs-installation-instructions","docs-removal-instructions","entity-event-setup",
 "entity-unique-id","has-entity-name","runtime-data","test-before-configure",
 "test-before-setup","unique-config-entry","config-entry-unloading","log-when-unavailable",
 "entity-unavailable","action-exceptions","reauthentication-flow","parallel-updates",
 "test-coverage","integration-owner","docs-installation-parameters",
 "docs-configuration-parameters","entity-translations","entity-device-class","devices",
 "entity-category","entity-disabled-by-default","discovery","stale-devices","diagnostics",
 "exception-translations","icon-translations","reconfiguration-flow","dynamic-devices",
 "discovery-update-info","repair-issues","docs-use-cases","docs-supported-devices",
 "docs-supported-functions","docs-data-update","docs-known-limitations","docs-troubleshooting",
 "docs-examples","async-dependency","inject-websession","strict-typing",
}
rules = (yaml.safe_load(open(sys.argv[1])) or {}).get("rules") or {}
missing = sorted(CANON - set(rules))
if missing:
    print(f"    {len(missing)} canonical rules absent, e.g. {missing[:6]}")
sys.exit(1 if missing else 0)
PYQS
  else
    FAIL "missing quality_scale.yaml"
  fi
  M="${CC}manifest.json"
  grep -q '"integration_type"' "$M" 2>/dev/null || FAIL "manifest.json missing integration_type"
  grep -q '"issue_tracker"'    "$M" 2>/dev/null || FAIL "manifest.json missing issue_tracker (HACS requires it)"
  # A manifest that claims config_flow without the module fails setup at runtime.
  if grep -q '"config_flow"[[:space:]]*:[[:space:]]*true' "$M" 2>/dev/null; then
    [ -f "${CC}config_flow.py" ] || FAIL "manifest declares config_flow: true but ${CC}config_flow.py is missing"
  fi
  # A panel integration declares `frontend` in dependencies; the frontend component's
  # pip requirement is NOT pulled in by `pip install homeassistant`, so without an
  # explicit pin every setup test fails in CI with "No module named 'hass_frontend'"
  # while usually passing locally (the package is already there from another install).
  # A panel's presentation logic is reachable from nothing else: tsc proves a helper
  # returns a string, not that it returns the right one, and the Python suite cannot
  # see it. WARN rather than FAIL — a hard failure pushes people to a trivially
  # passing test, which is the vacuous check this gate exists to remove.
  if [ -d frontend ] && [ -f frontend/package.json ]; then
    grep -qE '"test"[[:space:]]*:' frontend/package.json \
      || WARN "frontend/package.json has no test script; the panel's presentation logic is unproven (see the panel section of SKILL.md for what to export)"
  fi

  if grep -qE '"(frontend|panel_custom)"' "$M" 2>/dev/null; then
    grep -qE '^[[:space:]]*home-assistant-frontend==' requirements.test.txt 2>/dev/null \
      || FAIL "manifest depends on frontend/panel_custom but requirements.test.txt has no home-assistant-frontend pin (every setup test will fail in CI with: No module named 'hass_frontend')"
  fi
  [ -f CLAUDE.md ]         || FAIL "missing CLAUDE.md (the skill's per-repo enforcement — without it no future session is told to re-invoke)"
  [ -f README.md ]         || FAIL "missing README.md (HACS 'information' and 'images' checks both need it)"
  [ -f pyrightconfig.json ] || WARN "missing pyrightconfig.json"
fi

# --- Coverage gaps closed 2026-08-11 -----------------------------------------
# Every check above was added reactively, one per bug. A cross-reference of the
# skill's stated rules against this script found five that were documented and
# never enforced; three had already been violated in the skill's own repo. These
# are those five.

# 1. Autolabeler rules must be TITLE-only. A `branch:` rule flaps whenever the
#    branch name disagrees with the commits (branch `chore/…`, commits `feat:`).
if [ -f .github/release-drafter.yml ]; then
  python3 - .github/release-drafter.yml <<'PYAL' || FAIL "release-drafter.yml autolabeler has non-title rules (title-only, or labels flap)"
import sys, yaml
cfg = yaml.safe_load(open(sys.argv[1])) or {}
bad = [r.get("label") for r in cfg.get("autolabeler", []) if set(r) - {"label", "title"}]
for b in bad:
    print(f"    rule '{b}' matches on something other than the title")
sys.exit(1 if bad else 0)
PYAL
fi

# 2. Docstrings are ONE line for functions and classes. MODULE docstrings are
#    exempt: SKILL.md's Code style constrains "public functions and classes", and a
#    file-level explanation of a load-bearing constraint is better placed in a module
#    docstring than demoted to a comment. Reported from the field — the rule was
#    stricter than the prose it enforced.
if [ -n "$CC" ]; then
  python3 - "$CC" <<'PYDS' || FAIL "multi-line docstring on a function or class in custom_components/ (single-line required; module docstrings are exempt)"
import ast, pathlib, sys
bad = []
for f in pathlib.Path(sys.argv[1]).rglob("*.py"):
    try:
        tree = ast.parse(f.read_text(encoding="utf-8"))
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        doc = ast.get_docstring(node, clean=False)
        if doc and "\n" in doc.strip():
            name = getattr(node, "name", "<module>")
            print(f"    {f}:{getattr(node, 'lineno', 1)} {name}")
            bad.append(name)
sys.exit(1 if bad else 0)
PYDS
fi

# 3. The commit-msg hook must be present AND enabled. Shipping it is not enough:
#    a harness can inject AI-attribution trailers on every commit, and prose
#    alone loses that fight (which is why the hook exists).
if [ -f .githooks/commit-msg ]; then
  [ -x .githooks/commit-msg ] || FAIL ".githooks/commit-msg is not executable (chmod +x)"
  if git rev-parse --git-dir >/dev/null 2>&1; then
    [ "$(git config core.hooksPath 2>/dev/null)" = ".githooks" ] \
      || WARN "core.hooksPath is not .githooks — run: git config core.hooksPath .githooks"
  fi
else
  WARN "no .githooks/commit-msg (terse-subject + AI-trailer rejection)"
fi

# 4. Brand assets: exact square sizes, and the @2x variants. A present icon.png
#    with no icon@2x.png is the classic "icon shows only sometimes" bug — a
#    HiDPI client requests @2x, 404s, and falls back inconsistently.
if [ -n "$CC" ]; then
  [ -d "${CC}brand" ] || FAIL "missing ${CC}brand/ (HACS check-brands fails without icon.png)"
  python3 - "${CC}brand" <<'PYBR' || FAIL "brand assets missing or wrongly sized"
import pathlib, struct, sys

def size(p):
    b = p.read_bytes()
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", b[16:24])

brand = pathlib.Path(sys.argv[1])
want = {"icon.png": (256, 256), "icon@2x.png": (512, 512)}
bad = False
for name, exp in want.items():
    f = brand / name
    if not f.exists():
        print(f"    missing {f}"); bad = True; continue
    got = size(f)
    if got != exp:
        print(f"    {f} is {got}, expected {exp}"); bad = True
for name in ("logo.png", "logo@2x.png"):
    if not (brand / name).exists():
        print(f"    missing {brand / name}"); bad = True
sys.exit(1 if bad else 0)
PYBR
fi

# 5. Self-diff, when this IS the skill repo. A consuming repo has no templates/
#    to compare against, but the skill repo carries them — and a second labeler
#    drifted into its own .github/ and survived months of prose review because
#    nothing ever ran this diff.
TMPL=$(ls -d plugins/*/skills/*/templates 2>/dev/null | head -1)
if [ -n "$TMPL" ] && [ -d "$TMPL/.github" ]; then
  # SEMANTIC comparison, not `diff`: block-vs-flow YAML sequences and quoted keys
  # are not drift, and a check that cries wolf over formatting gets ignored. Parsed
  # structures must match; comments are reported separately as a warning, because a
  # stale comment is how the corrected autolabeler vocabulary failed to propagate.
  python3 - "$TMPL/.github" .github <<'PYSD' || FAIL "this repo's .github/ diverges from its own templates/ (see Mode 4 sanctioned adaptations)"
import pathlib, sys, yaml

tmpl, repo = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
# Files this repo legitimately adapts; every other difference is drift.
SANCTIONED = {"release_drafter.yml",   # reads a plugin manifest, not an HA one
              "pr-checks.yml",         # gather step reads plugin.json + marketplace.json
              "python_validate.yml"}   # non-HA suite, runs on pull_request
bad = False
for tf in sorted(tmpl.rglob("*.yml")):
    rel = tf.relative_to(tmpl)
    if rel.name in SANCTIONED:
        continue
    rf = repo / rel
    if not rf.exists():
        # Presence is the canonical-workflows list's job, and that list knows which
        # rows are integration-only. Enforcing it here too made the two disagree:
        # a non-integration repo passed the list and failed this with the same file.
        continue
    if yaml.safe_load(tf.read_text()) != yaml.safe_load(rf.read_text()):
        print(f"    diverges: .github/{rel}"); bad = True
sys.exit(1 if bad else 0)
PYSD
fi

# A repo that ships auto_draft_pr.yml needs the RELEASE_TOKEN secret it runs on. A PR
# opened with GITHUB_TOKEN fires no `pull_request_target` event, so no checks run and
# the required ones never report — the PR is permanently unmergeable.
# Secret listing needs admin, so this checks when it can and says so when it cannot,
# rather than passing silently.
if [ -f .github/workflows/auto_draft_pr.yml ]; then
  if SECRETS=$(gh secret list --json name --jq '.[].name' 2>/dev/null); then
    printf '%s\n' "$SECRETS" | grep -qx RELEASE_TOKEN \
      || FAIL "auto_draft_pr.yml is present but the RELEASE_TOKEN secret is not set (see SKILL.md, RELEASE_TOKEN)"
  else
    echo "ℹ️  cannot list secrets here — verify RELEASE_TOKEN exists, or draft PRs will not open"
  fi
fi

# release-drafter v7 matches a category through `when:`. A top-level `labels:` is the
# v6 shape: it parses, the drafter runs green, and NO category ever matches — so
# `$RESOLVED_VERSION` silently falls back to a patch bump. Invisible here because the
# body is overwritten by release_notes.py, so the only symptom is a version that is
# quietly wrong. A `feature`-labelled PR resolved 0.0.1 instead of 0.1.0 on ha-ci-testing.
if [ -f .github/release-drafter.yml ]; then
  python3 - <<'PYDRAFTER' || fail=1
import pathlib, sys, yaml

doc = yaml.safe_load(pathlib.Path(".github/release-drafter.yml").read_text()) or {}
bad = [c.get("title") or c.get("type") for c in (doc.get("categories") or [])
       if "labels" in c or "label" in c]
if bad:
    print("❌ FAIL: release-drafter categories use the v6 top-level `labels:`; v7 matches "
          "under `when:` and these never match, so the version resolves to a patch bump:")
    for b in bad:
        print(f"    {b}")
    sys.exit(1)
sys.exit(0)
PYDRAFTER
fi

[ "$fail" = 0 ] && { echo "✅ skill audit passed"; exit 0; } || { echo "skill audit FAILED"; exit 1; }
