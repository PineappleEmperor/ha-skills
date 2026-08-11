#!/usr/bin/env bash
# UserPromptSubmit: per-turn anchors. Independent, each marker-gated.

# HA-integration repos: skill + quality anchors.
if ls custom_components/*/manifest.json >/dev/null 2>&1; then
  msg="[ha-integration] ha-integration skill active before integration edits · keep quality_scale.yaml honest · verify HA APIs at developers.home-assistant.io"
  [ -d firmware ] && msg="$msg · run scripts/sync_render.py after firmware/ edits"
  echo "$msg."
fi

# Any repo on this workflow stack (the skill repo AND scaffolded integrations):
# the commit/PR conventions that drift down-context mid-session.
if [ -f .github/workflows/pr-checks.yml ]; then
  echo "[ci-conventions] commit & PR subject = ONE tight imperative (lowercase after the colon, no trailing period, no comma-joined dual subject). YOU open the PR (gh pr create) — no workflow opens one; pr-checks.yml only maintains the commit-list block in the body, so don't hand-edit inside the <!-- commit-summary --> markers. PR TITLE must use a labellable type: feat|feature, fix, or chore|docs|refactor|perf|test|build|ci|style (all label as chore), or type! for breaking. revert: passes lint_pr but maps to NO label and NO release category. Branch off main; bump the manifest/plugin version once, as the last commit before merge."
fi
