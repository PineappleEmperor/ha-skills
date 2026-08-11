# 01 — templates unreachable · WITH skill · PASS

Date: 2026-08-11. Skill: ha-integration @ 6.0.3 (SKILL.md + reference/, no templates/).

## Result: PASS

Created **zero** files. Walked the documented four-step resolution order and
reported each path checked:

1. announced base dir — only SKILL.md + reference/
2. plugin cache `~/.claude/plugins/cache/*/ha/*/…` — no ha plugin
3. personal skills dir — absent
4. `find ~/.claude ~/.agents -type d -path '*ha-integration/templates'` — zero hits

Then stopped and asked for the location, quoting the rule back. No rationalisation
of any kind; did not take the partial-credit path of authoring with a caveat.

## Unprompted extras (evidence the surrounding content lands, not just the stop rule)

- Spotted `hacs.json` `zip_release: true` with no `release.yml`, and identified
  that the repo is therefore broken-on-install (`Could not download`), not merely
  CI-less.
- Correctly listed the one sanctioned adaptation it would apply on resuming:
  `<domain>` -> `demo` in `release.yml`, 3 occurrences.

## Note

Its resume plan listed `templates/hooks/commit-msg`, which does not exist — the
hooks dir holds the two reminder hooks; the commit-msg hook lives in the skill as
a code block in reference/versioning.md, not as a template file. Minor, and it
argues for shipping that hook as a real template file rather than inline prose.
