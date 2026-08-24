# Commit conventions

What a commit subject must look like, why the body stays empty, and what the release
notes are generated from. The labels, gates and release model are
`reference/versioning.md`.

## Conventional Commits & Semantic Versioning

**Commit format:**
```
<type>[(<scope>)][!]: <description>

[optional body — one blank line after description]

[optional footers — BREAKING CHANGE: <detail>]
```

**Keep messages short.** Tight imperative subject; **subject-only by default**. Add a body ONLY when the *why* is non-obvious, or for breaking changes / migration notes — never to restate what the diff already shows. Long bodies that narrate the change are noise. Subject in imperative mood, lowercase after the colon, no trailing period.

**No AI-attribution trailers.** Don't append `Co-Authored-By: Claude`, tool/session links, or any "generated with…" line to commits — keep the authorship history clean. (If a harness injects such trailers by default, strip them.) A `Co-Authored-By:` for a *real* human collaborator is fine.

⚠️ **Enforce the trailer ban with a `commit-msg` hook — prose alone isn't enough.** A coding harness can inject `Co-Authored-By: Claude` / `Claude-Session:` on *every* commit via a standing instruction, which fights this rule turn after turn; the agent keeps "remembering" the harness default over the skill and regresses. The fix is deterministic enforcement at the git layer, not memory. Ship `.githooks/commit-msg` (Conventional Commit subject shape + terse-subject + no-narrative-body + an **editorialising-word** reject + **AI-trailer rejection**), add it to the scaffold's repo-root files, and tell contributors to enable it once per clone in `CLAUDE.md`: `git config core.hooksPath .githooks`.
Body in **`templates/hooks/commit-msg`** — copy it to `.githooks/commit-msg`, `chmod +x`. Don't retype it from this document.

**Put the narrative in the release, not the commit.** The human-readable "what changed and why it matters" belongs in the **PR description / release notes** (surfaced by release-drafter / `generate_release_notes`), which is where users actually read it. Keep commits terse; write the detail once, in the release description.

**The PR body is for reviewers and nothing else.** No job writes it — see `reference/github-actions.md` for which workflow opens a draft and how. Release notes are built from the commit subjects, so anything written here reaches reviewers only. Label the PR so it lands in the intended category (e.g. a `major`/`xfeature` label → 🚨 Breaking Change). Note release-drafter draws the PR body via the GraphQL path; `gh pr edit` can fail on the Projects-classic deprecation — set title/body via `gh api -X PATCH repos/{o}/{r}/pulls/{n} -f title=… -F body=@file` instead.

> ✅ **Release notes are generated from commit subjects, not from PR bodies.**
> `scripts/release_notes.py` walks the commits since the last published release,
> classifies each by its own Conventional Commit type, and groups them under
> Breaking / Features / Fixes / Maintenance / Other — an unmapped type such as `revert:` lands under Other, one line each, linking to the PR it
> arrived with, and ends with a full-changelog compare link.
>
> This is what surveyed HACS repos do (alexa_media_player, alandtse/tesla,
> hacs/integration, SonoffLAN, checked 2026-08-15). None of them nests commits
> under a PR entry.
>
> **Why not release-drafter's `$CHANGES`.** It categorises each *PR* by its single
> label, so a `fix:` commit inside a `feat:`-titled PR is filed under Features and a
> reader looking for what was fixed finds no Fixes section. Measured on one session,
> 3 of 8 merged PRs spanned more than one commit type, so this is the common case.
>
> release-drafter still owns the draft and the tag; `release_drafter.yml` generates
> the body over the top, then `check_release_notes.py` validates the result. The
> config keeps only `autolabeler`, `categories` (for `semver-increment`) and a
> placeholder `template` that is visible if the generator ever fails to run.
>
> **The PR body is a separate thing**: it is what a reviewer reads on the PR, it
> is written by a human or left empty, and it never reaches the notes.
