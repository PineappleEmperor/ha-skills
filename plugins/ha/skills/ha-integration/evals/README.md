# ha-integration evals

Regression scenarios for **the skill itself**. Not copied into a scaffolded
integration — `templates/` is what ships; this directory is maintenance.

## Why

Every defect in `TODO.md` was found the expensive way: a real build (`ha-lego`)
went wrong, or a manual sweep found it months later. Nothing catches the next
drift until it ships. `superpowers:writing-skills` treats skill authoring as
TDD — write the failing scenario, watch an agent fail it, write the guidance,
watch it pass. These are the failing scenarios, kept so a future edit can be
checked against the failures that motivated it.

## How to run one

Each scenario is a markdown file under `scenarios/`. It gives you a fixture, a
prompt, and the pass/fail criteria.

```bash
./make_fixture.sh <scenario-dir>     # builds a throwaway repo, prints its path
```

Then dispatch a **fresh** subagent — a new context, no skill preloaded beyond
what the scenario says to give it — with the scenario's *Prompt* verbatim, its
working directory set to the fixture. Read the transcript against *Pass* /
*Fail*.

**Grading is by reading, not by exit code.** These test judgement under
pressure, and the failure mode is an agent that produces plausible, confident,
wrong work. An automated assertion would mostly measure whether the agent used
the expected words. Read what it actually did.

**Always run the baseline arm too** — the same prompt with the guidance removed
(or against an older revision of the skill). If the baseline already passes, the
scenario is not testing anything and the guidance it justifies should be cut.
One sample per arm lies; run 3–5.

## Scenarios

| # | Scenario | Guards |
|---|---|---|
| 01 | `templates/` unreachable during scaffold | The `ha-lego` failure: agent authors CI from the prose, calls it done |
| 02 | Audit a repo whose workflows were paraphrased | The audit passing 15 hand-written files clean |
| 03 | Write the first test for a scaffolded integration | The pytest prerequisites (`conftest.py`, `asyncio_mode`) |

## Adding one

Add a scenario when a real failure gets past the skill — not for hypotheticals.
Record the *verbatim* rationalisation the agent used; that phrasing is the thing
the next revision has to close, and paraphrasing it loses the loophole.
