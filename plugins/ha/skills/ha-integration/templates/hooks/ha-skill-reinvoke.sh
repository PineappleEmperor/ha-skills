#!/usr/bin/env bash
# SessionStart: in an HA custom-integration repo, re-arm the ha-integration skill rule.
#
# "The skill is active" alone does not work: it has been active while the skill was
# still not followed, because the agent was following a faithful-sounding paraphrase
# of the skill instead of the artefacts it points at, and believed it was complying.
# So name the two highest-cost traps outright.
if ls custom_components/*/manifest.json >/dev/null 2>&1; then
  cat <<'MSG'
[ha-integration] This repo is a Home Assistant custom integration. Invoke the `ha-integration` skill via the Skill tool BEFORE modifying any integration code this session, and re-invoke after every /compact.

Two traps the skill being "active" does not catch:
  1. CI files are COPIED from the skill's templates/ dir, byte-for-byte. Writing a
     workflow that does what the skill's prose describes is not copying it. If you
     cannot locate templates/, stop and say so - do not author from the prose.
     Only sanctioned adaptation: <domain> substitution in release.yml.
  2. Docstrings are ONE line. Module docstring on every file; short single-line
     docstrings on public functions and classes. Single line means single line.
MSG
fi
