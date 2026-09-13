#!/usr/bin/env bash
# UserPromptSubmit: per-turn anchors. Independent, each marker-gated.
# Install: a `command` hook under `hooks.UserPromptSubmit` in ~/.claude/settings.json
# whose command is `bash /path/to/ha-resources-reminder.sh`.

# HA-integration repos: skill + quality anchors.
if ls custom_components/*/manifest.json >/dev/null 2>&1; then
  echo "[ha-integration] ha-integration skill active before integration edits · keep quality_scale.yaml honest · verify HA APIs at developers.home-assistant.io."
fi

# Any repo on this workflow stack (the skill repo AND scaffolded integrations): the
# commit/PR conventions that drift down-context mid-session. reference/commits.md owns
# them; this repeats only the ones that get broken.
if [ -f .github/workflows/pr-checks.yml ]; then
  echo "[ci-conventions] commit & PR subject = ONE tight imperative (lowercase after the colon, no trailing period, no comma-joined dual subject). auto-draft-pr.yml opens the draft PR with a title built from the commits; no job writes the PR body. PR TITLE must use a type release-flow's lint-pr.yml accepts (the list is in that workflow); type! for breaking; revert: is not accepted. Branch off main; the release tag sets the version, so no PR carries a manifest bump."
fi
