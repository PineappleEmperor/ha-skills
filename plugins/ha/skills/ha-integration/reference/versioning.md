# Versioning, labels & CI gating

Reference for `ha-integration`. Loaded on demand.

- One labeler, title-only — don't hand-roll a second one
- Stale superseded labels — NOT rare in a squash + rc-cycle repo
- Type-vocab gap (narrower than it looks — verify against the config, not from memory)
- Prerelease (rc) cycle
- ⚠️ A `pull_request_target` workflow cannot validate a fix to itself
- PR events fire normally — the `GITHUB_TOKEN` suppression no longer applies
- How the current opener avoids this
- The suppression is not only about PR creation
- This no longer bites, because of how the opener is built





Commit and PR-title conventions, and what the release notes are built from, are
`reference/commits.md`.

### One labeler, title-only — don't hand-roll a second one

⚠️ The autolabeler can only match title/body/branch/files (never commit subjects). Label off the **title** and keep it the *only* labeler. Pitfalls: (a) a second label step in any workflow **fights** the autolabeler → labels flap (add/remove every push); (b) `branch:` rules flap when the branch name disagrees with the commits (e.g. branch `chore/…`, commits `feat:`) — so use **title-only** rules. Resist re-adding custom bash to "label from commit subjects"; the title already encodes the winning type.

### Stale superseded labels — NOT rare in a squash + rc-cycle repo

⚠️ The autolabeler only *adds*, never removes. When a PR's title flips type mid-life (`fix:` → `feat:` as scope grows — routine on a long-lived `feat/rcN` branch), the **old type label lingers alongside the new one**. release-drafter is PR-granular and lists a PR under **every** matching label's category, so a double-labelled PR shows up under *two* headings (e.g. both `## 🚀 Features` and `## 🔧 Fixes`) with the same change listed under two release sections. The `version-resolver` still picks the highest for the bump, but the **release notes are wrong**. This is common — not "rare since a PR is usually one type"; rc-cycle PRs routinely accrue mixed types and a flipping title. Fix with a **removal-only** step after the autolabeler (removal-only can't flap — it only ever subtracts the non-winning labels, keyed on the same title the autolabeler reads):
```yaml
# pr-checks.yml `label` job, step AFTER autolabeler@v7
- name: Remove superseded type labels
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GH_REPO: ${{ github.repository }}  # job has no checkout — gh would else fail "not a git repository"
    TITLE: ${{ github.event.pull_request.title }}
    PR: ${{ github.event.pull_request.number }}
  run: |
    if   printf '%s' "$TITLE" | grep -qiE '^[a-z]+(\([^)]*\))?!:';        then WIN=xfeat
    elif printf '%s' "$TITLE" | grep -qiE '^(chore|docs)(\([^)]*\))?:';   then WIN=chore
    elif printf '%s' "$TITLE" | grep -qiE '^fix(\([^)]*\))?:';            then WIN=fix
    elif printf '%s' "$TITLE" | grep -qiE '^(feat|feature)(\([^)]*\))?:'; then WIN=feature
    else exit 0  # title maps to no managed label; leave labels untouched
    fi
    CURRENT=$(gh pr view "$PR" --json labels --jq '.labels[].name')
    for L in xfeat feature fix chore; do
      [ "$L" = "$WIN" ] && continue
      # `if` (not `grep && gh`): a no-match grep as the step's last command
      # returns 1 under `bash -e`, failing the step even when nothing's wrong.
      if printf '%s\n' "$CURRENT" | grep -qx "$L"; then
        gh pr edit "$PR" --remove-label "$L"
      fi
    done
```
The `!`-breaking branch must come first (else `feat!` matches the `feat` arm). This is still **one source of truth** — the title — and removal-only, so it can't fight the autolabeler the way a second *adding* step does. Needs `pull-requests: write`. **Note this only fixes the *labels* (one PR → one category).** Within a single squash PR whose body lists mixed-type commits, the commits stay together under that PR's one category — that no longer arises: the notes are built from commit subjects and each commit is classified on its own, so a mixed-type PR contributes to whichever sections its commits belong in.

### Type-vocab gap (narrower than it looks — verify against the config, not from memory)

⚠️ The autolabeler maps `feat`/`feature` → **feature**, `fix` → **fix**, `chore`/`docs`/`refactor`/`perf`/`test`/`build`/`ci`/`style` → **chore**, and any `type!:` → **xfeat**. So `ci:`, `refactor:`, `perf:`, `build:`, `style:` and `test:` **are** labelled (as `chore` → 🧰 Maintenance → patch). The real gap is **`revert:`**, which `lint_pr` accepts and the autolabeler maps to nothing → no label → no release-drafter category. **This matters more now a human types the title.** A `revert:` PR — or any non-Conventional title — passes `lint_pr` and still ends up unlabelled, hence uncategorised and invisible to the version gate. The `title-check` job in `pr-checks.yml` catches it: it reads the PR's **actual labels** (ground truth, so it can't drift from this config), and `needs: label` guarantees the autolabeler has already run and comments with a suggested title type derived from the commits. It does not edit the title; that's the author's call. Don't hand-patch the label either — the autolabeler rewrites it on the next `synchronize`.

### Prerelease (rc) cycle
release candidates are published via the GitHub **prerelease flag** + a `v…-rcN` tag; the manifest carries a matching **PEP440 prerelease** (`2.0.0rc1`) which `AwesomeVersion`/hassfest/HACS accept (`2.0.0 > 2.0.0rc1`). Two rules:
- **rc numbers track *published* candidates, not PRs.** You only increment `rc1`→`rc2` when you actually cut a new published rc; you do **not** invent `rc2`/`rc3` per-PR to satisfy the gate. The version stays frozen across iteration: in a tag-driven repo nothing in the branch carries it at all — the rc number lives only in the tag you publish.
- **A prerelease deliberately changes gate behaviour:** a prerelease version only needs to *differ from base* — so the gate must **skip** the label-derived "incorrect version" suggestion when the PR version matches `(rc|alpha|beta|a|b|dev)[0-9]*$` (otherwise a `feature`-labelled `2.0.0rc1` PR fails, demanding `v2.1.0`). Also de-anchor the base parse (`^([0-9]+)\.([0-9]+)\.([0-9]+)` without `$`) so a base that already carries `rcN` still parses. This is the *only* prerelease gate change needed — do **not** add per-PR rc-increment logic or relax the "differ from base" rule.
- **Graduating off rc to the same-number final is a legitimate bump the gate must allow.** Coming off the rc line (`2.0.0rc19` → **`2.0.0`** final) is the natural cycle close, but the de-anchored parse makes `2.0.0rc19` and `2.0.0` both `(2,0,0)`, so a naive `pr == base` check (and a `feature` label demanding `v2.1.0`) **wrongly rejects the graduation** — even though `AwesomeVersion` knows `2.0.0 > 2.0.0rc19`. The gate special-cases it: when the PR version is final, equals the base tuple, **and** the last release was a prerelease, pass it ("final graduates its own prerelease"); a `pr == base` where the last release was already *final* still fails (real unchanged version). Covered by `test_final_graduates_prerelease`.

**Nothing is ever bumped by hand.** `release.yml` writes `manifest.json` from the release
tag at publish, so no PR carries a bump, `version-gate` skips itself, and the advisory step
says what the labels imply. The committed value is a placeholder between releases. Dependabot's exemption from it is `reference/github-setup.md`.

### ⚠️ A `pull_request_target` workflow cannot validate a fix to itself

`pull_request_target` loads the workflow from the **base branch**, so a PR that fixes a
broken job is still checked by the broken copy on `main`. The job cannot pass until the fix
is merged, and it cannot be merged while the job is red — the rule for that single case is `reference/discipline.md`.

This is the **only** sanctioned exception, per `reference/discipline.md`; it applies to one job on
one PR, and it requires proof by diff. The full rule, the rationalisation table and the red
flags are *Merge discipline* in `reference/discipline.md` — read it there rather than
acting on this summary.

### PR events fire normally — the `GITHUB_TOKEN` suppression no longer applies

### How the current opener avoids this
`auto_draft_pr.yml` opens with `RELEASE_TOKEN`, so the events fire and every check runs on first open. The alternatives were worse: opening with the default token and pushing an empty commit to force `synchronize` litters history and races the checks, and a `workflow_dispatch` re-run needs a human, which defeats the point.

**Historical note, kept because the symptom is memorable and the old advice is still circulating.** GitHub suppresses workflow runs for events caused by the default `secrets.GITHUB_TOKEN` (an anti-recursion rule). While this skill shipped `create-dev-pr.yml`, that bot opened the PR, so the `pull_request: opened` event was swallowed and `lint_pr`, the autolabeler and the version gate **did not run on first open**. It bit exactly once per branch — a later human push fired `synchronize` with the human as `triggering_actor`, and everything ran — so the footgun only really hurt a branch pushed once and merged untouched.

### The suppression is not only about PR creation

⚠️ It fires for *any* event caused by the default token, so **a workflow that expects to be woken by another workflow's action is relying on an event that will not arrive.** Concretely: the autolabeler applies a label with `GITHUB_TOKEN`, so the resulting `labeled` event is swallowed and nothing keyed on it runs. **This is why every PR-time job that reads or writes labels lives in one workflow, `pr-checks.yml`, ordered with `needs:`.** Jobs within a workflow sequence deterministically; workflows never do. `title-check` learned this the hard way — as a separate workflow it raced the autolabeler, then polled for the label as a workaround, and only `needs: label` actually fixed it. If you find yourself polling for another workflow's side effect, put the work in the same workflow instead.

### This no longer bites, because of how the opener is built
a human-opened PR is not a token-caused event and every `pull_request` workflow runs on `opened`. `auto_draft_pr.yml` opens with `RELEASE_TOKEN` precisely so the events fire; a PR opened with the default token would be permanently unmergeable.

The old advice also suggested a `push:` trigger on the version gate so it ran on branch pushes too. **Dropped:** the label-derived expected bump needs PR context, so the push path could only ever check the parts that don't depend on a label — and in practice the template's push trigger was a no-op, because every step was gated on `github.event_name == 'pull_request'`. The gate is a PR-time job now, which is the only context in which it can do its whole job.

---

Dependabot's setup, grouping and floor management live in `reference/dependabot.md`.
