#!/usr/bin/env bash
# SessionStart: in an HA custom-integration repo, re-arm the ha-integration skill rule.
# Install: a `command` hook under `hooks.SessionStart` in ~/.claude/settings.json whose
# command is `bash /path/to/ha-skill-reinvoke.sh`.
#
# "The skill is active" alone does not work: it has been active while the skill was
# still not followed, because the agent was following a faithful-sounding paraphrase
# of the skill instead of the artefacts it points at, and believed it was complying.
# So name the two highest-cost traps outright.
if ls custom_components/*/manifest.json >/dev/null 2>&1; then
  cat <<'MSG'
[ha-integration] This repo is a Home Assistant custom integration. Invoke the `ha-integration` skill via the Skill tool BEFORE modifying any integration code this session, and re-invoke after every /compact.

Two traps the skill being "active" does not catch:
  1. CI files are never authored. Callers are copied from the CI repositories' READMEs,
     the rest from where reference/github-actions.md's table says, and only its listed
     adaptations are applied. A workflow that does what the prose describes is not a
     copy. If you cannot reach a README or templates/, stop and say so - do not write
     from memory.
  2. Docstrings on public functions and classes are ONE line; only the module docstring
     may run longer. Single line means single line.
MSG
fi
