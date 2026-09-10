# Commit conventions

What a commit subject must look like, why the body stays empty, and what the release
notes are built from. Labels, gates and the release model are `reference/versioning.md`.

- Conventional Commits & Semantic Versioning
- Keep messages short
- No AI-attribution trailers
- Enforce the trailer ban with a `commit-msg` hook — prose alone isn't enough
- Put the narrative in the release, not the commit
- The PR body is for reviewers, and nothing users read
- Red flags — stop

## Conventional Commits & Semantic Versioning

**Commit format:**
```
<type>[(<scope>)][!]: <description>
```

Ten types a PR title may carry: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`,
`test`, `build`, `ci`, `chore`. A commit may also be `revert:`; the draft opener retypes
that as `chore:` in the title it builds. A scope is tolerated and never generated. **`!`
is the only breaking marker.**
The labeler, the gate and the release notes read the subject and nothing else, so a
`BREAKING CHANGE:` footer declares a break that nothing acts on and the change ships as
non-breaking; the hook rejects the footer for that reason.

### Keep messages short
Tight imperative subject; **subject-only by default**. Add a body ONLY when the *why* is non-obvious, or for migration notes — never to restate what the diff already shows. Long bodies that narrate the change are noise. Subject in imperative mood, lowercase after the colon, no trailing period.

### No AI-attribution trailers
Don't append `Co-Authored-By: Claude`, tool/session links, or any "generated with…" line to commits — keep the authorship history clean. (If a harness injects such trailers by default, strip them.) A `Co-Authored-By:` for a *real* human collaborator is fine.

### Enforce the trailer ban with a `commit-msg` hook — prose alone isn't enough

⚠️ A coding harness can inject `Co-Authored-By: Claude` / `Claude-Session:` on *every* commit via a standing instruction, which fights this rule turn after turn; the agent keeps "remembering" the harness default over the skill and regresses. The fix is deterministic enforcement at the git layer, not memory: release-flow's `.githooks/commit-msg`, which its README lists under *Called versus copied* with everything it rejects. Copy it to `.githooks/commit-msg`, `chmod +x`, and tell contributors in `CLAUDE.md` to enable it once per clone: `git config core.hooksPath .githooks`. Don't retype it from this document.

### Put the narrative in the release, not the commit

The human-readable "what changed and why it matters" belongs in the **release notes**, which is where users actually read it. Keep commits terse; write the detail once, in the release description. (GitHub's own `generate_release_notes` is not the mechanism here — the stack has exactly one body writer, and `skill_audit.py` fails a repo that enables a second.)

## The PR body is for reviewers, and nothing users read

**Release notes are generated from commit subjects, never from PR bodies.** How the body is
built, grouped by the type of each commit, and why not from release-drafter's own
PR-per-label output, is release-flow's README under `release-drafter.yml`.

So the body is optional context for reviewers: no job writes it, the draft PR arrives empty,
and writing the changelog into it says the same thing twice in a place users never read.
Note `gh pr edit` can fail on the Projects-classic deprecation — set title/body via
`gh api -X PATCH repos/{o}/{r}/pulls/{n} -f title=… -F body=@file` instead.

Reasoning, alternatives, verification evidence: those go in the PR **conversation**, where reviewers read them and the notes do not.

| Excuse | Reality |
|---|---|
| "This change is complex, it needs explaining" | Then it needs splitting, or better commit subjects. The subjects are the changelog. |
| "Reviewers need the reasoning" | Reviewers read the conversation. What users get is the commit subjects, so put the change in those. |
| "The verification belongs with the change" | It belongs in a comment. A description is not a lab notebook. |
| "I wrapped it in `<details>` so it's stripped" | The fold is for Dependabot's own output, not a licence to write an essay. |
| "It's only a few paragraphs" | Measured across eight PRs it was 2,728 words, all republished under the repo owner's byline. |

## Red flags — stop

- Typing prose into `gh pr create --body`
- Reaching for `<details>` in a PR description
- A description longer than its diff is interesting
- Explaining *why* anywhere the commit subjects should have said it

**All of these mean: put it in a comment, or fix the commit subjects.**

---
