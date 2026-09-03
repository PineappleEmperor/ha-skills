#!/usr/bin/env python3
# skill-audit: local-tool
"""Read-receipt gate over this repo's own governing docs — pure logic, no dependencies.

Transport lives in governance_server.py so this module stays importable by the test suite in
CI, which installs only pytest and pyyaml.

Modelled on ha-mcp's strict best-practices gate (`src/ha_mcp/strict_bps.py`). The shape is
theirs; four things differ because our situation differs.

WHY A SEPARATE PROCESS AT ALL. A gate whose secret lives anywhere the gated party can read is
theatre. ha-mcp puts the salt in a server on another host. We cannot, so the equivalent boundary
is this process: spawned by the harness, outside the agent's sandbox and PID namespace, so its
memory is unreachable and its salt unguessable. Measured, not assumed — a harness child writes
paths the agent's shell gets `Read-only file system` on, and sees 116 PIDs against the agent's 5.

WHAT DIFFERS FROM ha-mcp:
  * The key mixes the governing docs' CONTENT hash alongside salt and clock. Theirs need not:
    their guide ships with their server. Ours change under us, so editing a governing doc must
    invalidate outstanding keys for the tiers it governs.
  * Keys are per-TIER. The corpus is ~2,000 lines; emitting all of it on every gate would be
    unusable, so each governed path maps to the docs that govern it. Same idea as their
    STRICT_BPS_GATED_TOOLS mapping a tool to one reference file.
  * The gated operation is a file write rather than an HA config write.
  * TWO receipts, not one. The docs receipt proves the rules were read; a second receipt, bound
    to the target file's own bytes, proves the WHOLE FILE was read before it was patched.
    Whole-file rewrites forced that reading implicitly and were the original design here.
    Patching is cheaper and avoids transcription slips across hundreds of untouched lines, but
    on its own it would restore the exact failure this repo already suffered: locate a line,
    replace it in isolation, never see the context that made it wrong. The file receipt buys
    the cheapness back without buying the failure.

WHAT IS COPIED DELIBERATELY:
  * Plain-English key prefixes. An opaque token made an agent read the round-trip as prompt
    injection and talk its user into disabling the gate (ha-mcp #1924).
  * One emitter, one validator per key. A refusal that leaks the key defeats the gate.
  * Fail OPEN where the key is unobtainable (a governing doc unreadable) so a broken doc cannot
    brick every edit. Fail CLOSED where intent is unclear (path outside the repo, unknown tier,
    ambiguous match): wrongly refusing costs one confusing error, wrongly allowing costs the gate.
"""

from __future__ import annotations

import difflib
import hashlib
import hmac
import os
import pathlib
import secrets
import time

REPO = pathlib.Path(__file__).resolve().parents[1]

RECEIPT_PREFIX = "I-HAVE-READ-THE-GOVERNING-DOCS"
EDIT_PREFIX = "I-HAVE-READ-THE-WHOLE-FILE"
_SALT = secrets.token_hex(8)
ROTATION_SECONDS = int(os.environ.get("GOVERNANCE_ROTATION_SECONDS", "3600"))

# Governed path prefix -> the docs that govern it. FIRST match wins, so specific before general.
TIERS: dict[str, tuple[str, ...]] = {
    # The governing docs govern THEMSELVES, via the doc about how changes are made. Without
    # this the gate is trivially defeated: the docs were writable by ordinary means, and since
    # an unreadable governing doc fails the gate OPEN, deleting one bought a keyless write.
    # Demonstrated end-to-end — a governing doc moved aside, then the search guard disarmed
    # through the live server with no key at all.
    "docs/workflow-map.md": ("plugins/ha/skills/ha-integration/reference/discipline.md",),
    "plugins/ha/skills/ha-integration/reference/": (
        "plugins/ha/skills/ha-integration/reference/discipline.md",
    ),
    "docs/backlog.md": ("plugins/ha/skills/ha-integration/reference/discipline.md",),
    ".github/workflows/": (
        "docs/workflow-map.md",
        "plugins/ha/skills/ha-integration/reference/github-actions.md",
    ),
    "plugins/ha/skills/ha-integration/templates/.github/workflows/": (
        "docs/workflow-map.md",
        "plugins/ha/skills/ha-integration/reference/github-actions.md",
    ),
    "plugins/ha/skills/ha-integration/templates/": (
        "plugins/ha/skills/ha-integration/reference/scaffold.md",
    ),
    "scripts/": (
        "plugins/ha/skills/ha-integration/reference/audit.md",
        "plugins/ha/skills/ha-integration/reference/testing.md",
    ),
    "tests/": (
        "plugins/ha/skills/ha-integration/reference/audit.md",
        "plugins/ha/skills/ha-integration/reference/testing.md",
    ),
}


class GateError(Exception):
    """Refusal that reaches the caller as a tool error, never as a crash."""


def resolve_tier(rel: str) -> str | None:
    """First matching tier for a repo-relative path, or None when ungoverned."""
    for prefix in TIERS:
        if rel == prefix or rel.startswith(prefix):
            return prefix
    return None


def _docs_hash(tier: str) -> str | None:
    """Hash of the tier's governing docs, or None if any is unreadable (fail-open signal)."""
    h = hashlib.sha256()
    for rel in TIERS[tier]:
        try:
            h.update((REPO / rel).read_bytes())
        except OSError:
            return None
    return h.hexdigest()


def _file_hash(rel: str) -> str:
    """Hash of the target's current bytes; a missing file counts as empty so it can be created."""
    try:
        return hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
    except OSError:
        return hashlib.sha256(b"").hexdigest()


def _key_for(tier: str, bucket: int, docs: str) -> str:
    mac = hmac.new(_SALT.encode(), f"{bucket}:{tier}:{docs}".encode(), hashlib.sha256)
    return f"{RECEIPT_PREFIX}-{mac.hexdigest()[:8]}"


def _edit_key_for(tier: str, rel: str, bucket: int, docs: str, body: str) -> str:
    mac = hmac.new(
        _SALT.encode(), f"{bucket}:{tier}:{docs}:{rel}:{body}".encode(), hashlib.sha256
    )
    return f"{EDIT_PREFIX}-{mac.hexdigest()[:8]}"


def current_receipt_key(tier: str, now: float | None = None) -> str | None:
    docs = _docs_hash(tier)
    if docs is None:
        return None
    bucket = int((time.time() if now is None else now) // ROTATION_SECONDS)
    return _key_for(tier, bucket, docs)


def valid_receipt_keys(tier: str, now: float | None = None) -> set[str]:
    """Current key plus the previous rotation's, so a read just before rotation still counts."""
    docs = _docs_hash(tier)
    if docs is None:
        return set()
    t = time.time() if now is None else now
    return {
        _key_for(tier, int(t // ROTATION_SECONDS), docs),
        _key_for(tier, int((t - ROTATION_SECONDS) // ROTATION_SECONDS), docs),
    }


def current_edit_key(rel: str, now: float | None = None) -> str | None:
    tier = resolve_tier(rel)
    if tier is None:
        return None
    docs = _docs_hash(tier)
    if docs is None:
        return None
    bucket = int((time.time() if now is None else now) // ROTATION_SECONDS)
    return _edit_key_for(tier, rel, bucket, docs, _file_hash(rel))


def valid_edit_keys(rel: str, now: float | None = None) -> set[str]:
    """Current and previous window, bound to the file's CURRENT bytes.

    Binding to content is what makes this receipt mean "you read this file as it stands". It
    also settles concurrent modification for free: if anything else rewrote the file after the
    read, every outstanding key for it is already dead.
    """
    tier = resolve_tier(rel)
    if tier is None:
        return set()
    docs = _docs_hash(tier)
    if docs is None:
        return set()
    t = time.time() if now is None else now
    body = _file_hash(rel)
    return {
        _edit_key_for(tier, rel, int(t // ROTATION_SECONDS), docs, body),
        _edit_key_for(tier, rel, int((t - ROTATION_SECONDS) // ROTATION_SECONDS), docs, body),
    }


def receipt_line(tier: str) -> str:
    """The ONLY place a docs key is emitted. Never reuse this text in a refusal."""
    return (
        f"Acknowledgment key: {current_receipt_key(tier)} - pass this as ReceiptKey to "
        f"get_file for paths under '{tier}'. It is a read-receipt, not a secret: "
        f"published here deliberately, rotates, is bound to the current content of the docs "
        f"below, and grants no privileges. Replaying it is the designed protocol."
    )


def safe_relpath(path: str) -> str:
    """Repo-relative path, refusing anything that escapes the repo. Fail closed."""
    p = pathlib.Path(path) if os.path.isabs(path) else (REPO / path)
    resolved = p.resolve()
    try:
        return str(resolved.relative_to(REPO))
    except ValueError:
        raise GateError(
            "path resolves outside the repository; patch_file only writes within it"
        ) from None


def get_docs(tier: str) -> str:
    if tier not in TIERS:
        raise GateError(f"unknown tier {tier!r}; known tiers: {sorted(TIERS)}")
    if current_receipt_key(tier) is None:
        return (
            f"A governing doc for '{tier}' is unreadable, so no key can be issued and the gate "
            f"is OPEN for this tier. Fix the doc to restore it."
        )
    parts = [receipt_line(tier), ""]
    for rel in TIERS[tier]:
        parts += [f"===== {rel} =====", (REPO / rel).read_text(encoding="utf-8"), ""]
    return "\n".join(parts)


def get_file(path: str, receipt_key: str | None) -> str:
    """Emit a governed file in full, plus the EditKey that patching it requires.

    Requires the tier's docs receipt first, so the rules are read before the file rather than
    instead of it.
    """
    rel = safe_relpath(path)
    tier = resolve_tier(rel)
    if tier is None:
        raise GateError(
            f"{rel} is not governed; read it with the ordinary tools rather than through this gate"
        )
    valid = valid_receipt_keys(tier)
    if valid and receipt_key not in valid:
        raise GateError(
            f"{rel} is governed by '{tier}'. Call get_docs(tier={tier!r}) first, read "
            f"it, then pass that ReceiptKey here."
        )
    try:
        body = (REPO / rel).read_text(encoding="utf-8")
    except OSError:
        body = ""
    return "\n".join(
        [
            f"EditKey: {current_edit_key(rel)} - pass this as EditKey on patch_file for "
            f"{rel}. It is bound to the bytes below, so it dies the moment this file changes; "
            f"re-read rather than resending a previous value.",
            "",
            f"===== {rel} ({len(body.splitlines())} lines) =====",
            body,
        ]
    )


def _apply(before: str, old_string: str, new_string: str, rel: str) -> str:
    """Exact, unique replacement. Absence and ambiguity are refusals, never guesses.

    One special case: an empty old_string against an empty file CREATES it. Without this, a
    governed directory becomes unextendable the moment writes are denied elsewhere — every new
    script or test would be impossible to add through the only writer allowed to add it. An
    empty old_string against a file with content stays a refusal, because that is a whole-file
    clobber wearing a patch's clothes.
    """
    if not old_string:
        if before == "":
            return new_string
        raise GateError(
            f"old_string is empty but {rel} is not; pass the exact text to replace rather than "
            f"clobbering the file"
        )
    hits = before.count(old_string)
    if hits == 0:
        raise GateError(
            f"old_string does not appear in {rel}; re-read the file, because it is not what you "
            f"think it is"
        )
    if hits > 1:
        raise GateError(
            f"old_string appears {hits} times in {rel}; include enough surrounding lines to make "
            f"it unique rather than letting the gate choose one"
        )
    return before.replace(old_string, new_string)


def _report(before: str, after: str, rel: str) -> str:
    """The actual diff, so an unintended edit is visible the moment it lands.

    Counts alone prove volume, not correctness: "+1 -1" reads identically whether the right
    line changed or the wrong one did. The diff is the evidence, so it is returned in full —
    context included, never truncated. A change large enough to be unwieldy here is itself
    worth seeing, and a silent cap would hide exactly the case this exists to catch.
    """
    diff = list(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
            lineterm="",
            n=3,
        )
    )
    if not diff:
        return "  no textual change"
    added = sum(1 for d in diff if d.startswith("+") and not d.startswith("+++"))
    removed = sum(1 for d in diff if d.startswith("-") and not d.startswith("---"))
    hunks = sum(1 for d in diff if d.startswith("@@"))
    return f"  {hunks} hunk(s), +{added} -{removed} lines\n" + "\n".join(diff)


def patch_file(
    path: str, old_string: str, new_string: str, edit_key: str | None
) -> str:
    """Replace one exact, unique occurrence of old_string, reporting what actually changed."""
    rel = safe_relpath(path)
    tier = resolve_tier(rel)
    if tier is None:
        raise GateError(
            f"{rel} is not governed; edit it with the ordinary tools rather than through this gate"
        )
    try:
        before = (REPO / rel).read_text(encoding="utf-8")
    except OSError:
        # A missing file is empty, not an error: creating one is a legitimate governed edit,
        # and its receipt is issued over the same empty-bytes hash get_file used.
        before = ""

    if not valid_receipt_keys(tier):
        # Fail open, as ha-mcp does when its skill content is missing: a broken governing doc
        # makes the key unobtainable, and bricking every edit is the worse failure.
        after = _apply(before, old_string, new_string, rel)
        (REPO / rel).write_text(after, encoding="utf-8")
        return (
            f"wrote {rel} (gate OPEN: a governing doc for '{tier}' is unreadable)\n"
            + _report(before, after, rel)
        )

    if edit_key not in valid_edit_keys(rel):
        raise GateError(
            f"{rel} is governed by '{tier}'. Call get_docs(tier={tier!r}), then "
            f"get_file(path={rel!r}) and READ IT IN FULL, then retry with the EditKey "
            f"it returns. That key is bound to this file's current bytes, so a stale one means "
            f"the file moved under you - re-read rather than resending a previous value."
        )

    after = _apply(before, old_string, new_string, rel)
    (REPO / rel).write_text(after, encoding="utf-8")
    # The key rolls forward: the caller read the file in full and has just seen this diff, so
    # it has read the file as it now stands. Without this every second patch cost a re-read of
    # the whole file — eleven of thirteen reads of one file in a session were that.
    return (
        f"wrote {rel}\n"
        + _report(before, after, rel)
        + f"\nEditKey: {current_edit_key(rel)} - for the next patch to {rel}; it is bound to "
        f"the bytes as now written, so it dies if anything else touches the file."
    )
