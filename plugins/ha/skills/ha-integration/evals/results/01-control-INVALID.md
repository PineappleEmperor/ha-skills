# 01 — control arm · INVALID (contaminated)

The "no-guidance" control loaded the ha-integration skill anyway: the skill is
registered in this environment, so putting the skill-repo checkout out of bounds
did not withhold the guidance. The agent found the rule, quoted it verbatim, and
refused — the same behaviour as the treatment arm, for the same reason.

That makes it a second treatment arm, not a control. Scenario 01's with-skill
PASS therefore demonstrates compliance-when-present and says nothing about
whether the guidance changes behaviour versus baseline.

## Fix applied to the method

A control must withhold the guidance EXPLICITLY ("do not invoke, read, load or
search for the skill; it is unavailable"), not merely make one copy of it
unreachable. Path restrictions do not remove a registered skill.

This belongs in evals/README.md as a rule: an environment where the skill
auto-loads cannot produce a control by hiding files.
