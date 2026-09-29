#!/usr/bin/env python3
# skill-audit: local-tool
"""PreToolUse hook: refuse a build dispatch whose brief is missing, malformed or unreviewed.

docs/brief.md owns the shape; this checks it. An Agent call is a build unless its
subagent_type is one of the read-only agents, and a build's prompt must carry
`Brief: <path>`. A Workflow script is held to every brief path it names, and must name one
unless it says `brief-gate: read-only`. Every problem is reported in one refusal, so a
brief is not repaired one round-trip at a time.
"""

import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

READ_ONLY = {
    "reviewer",
    "Explore",
    "Plan",
    "claude-code-guide",
    "caveman:cavecrew-investigator",
    "caveman:cavecrew-reviewer",
    "feature-dev:code-explorer",
    "feature-dev:code-architect",
}

SECTIONS = (
    "Goal",
    "Repository",
    "Sources read",
    "Defect class",
    "Facts",
    "Rules applied",
    "Cases",
    "Files",
    "Out of scope",
    "Commits",
    "Checks",
    "Stop and report if",
)
KINDS = ("reported", "sibling", "guard")
CASE_COLUMNS = ["#", "Kind", "Situation", "Facts", "Expected", "Proof", "Seen"]
FACT_COLUMNS = ["ID", "Fact", "Owner", "Pointers"]
RULE_COLUMNS = ["Rule", "Applies", "How the plan meets it"]
REVIEW = ROOT / "docs" / "review.md"
INVARIANTS_HEADING = "## Invariants every kind checks"
READ_LOG = ROOT / ".tmp" / "reads.jsonl"
SKILL = ROOT / "plugins" / "ha" / "skills" / "ha-integration"
SKILL_EXCLUDED = ("evals/results/", "__pycache__/")
GOVERNING_DOCS = ("brief.md", "review.md", "skill-schema.md", "skill-file-hierarchy.md")
CI_READMES = tuple(
    ROOT.parent / repo / "README.md"
    for repo in ("ha-integration-ci", "ha-panel-ci", "release-flow")
)

_BRIEF = re.compile(r"Brief:\s*(\S+?\.md)\b")
# Home Assistant core, not docs/skill-schema.md's "core rule" (a file's bold line).
_CORE = re.compile(r"\bcore\b(?! rules?\b)", re.IGNORECASE)
_TAG = re.compile(r"\b20\d\d\.\d{1,2}\.\d+\b")
_INVARIANT = re.compile(r"^(\d+)\. \*\*")
_DOC = re.compile(r"`([\w./-]+\.md)`")
# One or two digits, so a fact ID never collides with a ruff code such as F401.
_FACT_ID = re.compile(r"\bF\d{1,2}\b")


def _invariant_texts() -> dict[int, str]:
    """Each invariant docs/review.md lists, with the text of its whole item."""
    body = REVIEW.read_text().split(INVARIANTS_HEADING, 1)[1].split("\n## ", 1)[0]
    items: dict[int, list[str]] = {}
    current = None
    for line in body.splitlines():
        if m := _INVARIANT.match(line):
            current = int(m[1])
            items[current] = []
        if current is not None:
            items[current].append(line)
    return {n: "\n".join(lines) for n, lines in items.items()}


def invariants() -> list[int]:
    """The invariant numbers docs/review.md lists, which every brief answers in advance."""
    return list(_invariant_texts())


def invariant_sources() -> dict[int, list[str]]:
    """The documents each invariant names; answering it `yes` means having read them."""
    return {n: _DOC.findall(text) for n, text in _invariant_texts().items()}


def _sections(text: str) -> list[tuple[str, str]]:
    """The `##` headings in order, each with the text beneath it."""
    out: list[tuple[str, list[str]]] = []
    for line in text.splitlines():
        if line.startswith("## "):
            out.append((line[3:].strip(), []))
        elif out:
            out[-1][1].append(line)
    return [(name, "\n".join(body).strip()) for name, body in out]


def _table(body: str) -> tuple[list[str], list[list[str]]] | None:
    """The first markdown table in a section: its header and its data rows."""
    rows = [line.strip() for line in body.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        return None
    cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
    return cells[0], cells[2:]


def _check_sources(body: str, text_outside: str) -> list[str]:
    bullets = [
        line.strip() for line in body.splitlines() if line.strip().startswith("- ")
    ]
    problems = [
        f"Sources read: `{b}` does not end `(in full)`"
        for b in bullets
        if not b.endswith("(in full)")
    ]
    if _CORE.search(text_outside) and not any(
        "core" in b and _TAG.search(b) for b in bullets
    ):
        problems.append(
            "Sources read: the brief mentions core but names no core file at a tag"
        )
    return problems


def _check_cases(body: str) -> list[str]:
    table = _table(body)
    if table is None or table[0] != CASE_COLUMNS:
        return [f"Cases: needs a table with columns {' | '.join(CASE_COLUMNS)}"]
    rows = table[1]
    problems = []
    if len(rows) < 3:
        problems.append("Cases: fewer than three rows")
    kinds = [row[1] if len(row) > 1 else "" for row in rows]
    problems += [f"Cases: unknown kind `{k}`" for k in kinds if k not in KINDS]
    problems += [f"Cases: no `{k}` case" for k in KINDS if k not in kinds]
    problems += [
        f"Cases: case {row[0]} records nothing under Seen; run its Proof while planning"
        for row in rows
        if len(row) < 7 or not row[6]
    ]
    problems += [
        f"Cases: case {row[0]} cites no fact; every case proves a row of Facts"
        for row in rows
        if len(row) < 4 or not _FACT_ID.search(row[3])
    ]
    return problems


def _files(files_body: str) -> list[tuple[str, bool]]:
    """Each path a brief's Files section names, and whether the change creates it."""
    entries = [
        line.strip()[2:].split()
        for line in files_body.splitlines()
        if line.strip().startswith("- ") and len(line.strip()) > 2
    ]
    return [(words[0], "(new)" in words[1:]) for words in entries]


def _shipped(files_body: str) -> list[str]:
    """The skill documents a brief's Files section names, each of which carries rules."""
    return [
        p
        for p, _ in _files(files_body)
        if p.startswith("plugins/") and p.endswith(".md")
    ]


def _unread_files(files_body: str, sources_body: str) -> list[str]:
    """A file the change edits that the brief's author never read."""
    return [
        f"Files: `{path}` is changed but not under Sources read"
        for path, new in _files(files_body)
        if not new and path not in sources_body
    ]


def _unread_sources(rows: dict[str, list[str]], sources_body: str) -> list[str]:
    """An invariant answered `yes` whose named documents are not under Sources read."""
    return [
        f"Rules applied: `Invariant {n}` answered yes without reading `{doc}`"
        for n, docs in invariant_sources().items()
        if (row := rows.get(f"Invariant {n}")) and len(row) > 1 and row[1] == "yes"
        for doc in docs
        if doc not in sources_body
    ]


def _check_rules(body: str, files_body: str, sources_body: str) -> list[str]:
    table = _table(body)
    if table is None or table[0] != RULE_COLUMNS:
        return [f"Rules applied: needs a table with columns {' | '.join(RULE_COLUMNS)}"]
    rows = {row[0]: row for row in table[1] if row}
    problems = []
    for rule, row in rows.items():
        applies = row[1] if len(row) > 1 else ""
        if applies not in ("yes", "no"):
            problems.append(
                f"Rules applied: `{rule}` applies `{applies}`, not yes or no"
            )
        if len(row) < 3 or not row[2]:
            problems.append(
                f"Rules applied: `{rule}` does not say how the plan meets it"
            )
    required = [f"Invariant {n}" for n in invariants()]
    required += [f"Anti-patterns: {path}" for path in _shipped(files_body)]
    problems += [
        f"Rules applied: no `{rule}` row; docs/brief.md says what each answers"
        for rule in required
        if rule not in rows
    ]
    return problems + _unread_sources(rows, sources_body)


def _check_facts(body: str, cases_body: str, text: str) -> list[str]:
    """Each fact stated once, owned, proved by a case, and every citation resolving."""
    table = _table(body)
    if table is None or table[0] != FACT_COLUMNS or not table[1]:
        return [f"Facts: needs a table with columns {' | '.join(FACT_COLUMNS)}"]
    rows = [row + [""] * (len(FACT_COLUMNS) - len(row)) for row in table[1]]
    ids = [row[0] for row in rows]
    problems = [
        f"Facts: `{i}` is not an ID of the form F1 to F99"
        for i in ids
        if not _FACT_ID.fullmatch(i)
    ]
    problems += [
        f"Facts: {i} is used for more than one row"
        for i in dict.fromkeys(ids)
        if ids.count(i) > 1
    ]
    claims: dict[str, str] = {}
    for fid, claim, owner, _ in rows:
        key = " ".join(claim.lower().split())
        if key in claims:
            problems.append(f"Facts: {fid} makes the same claim as {claims[key]}")
        claims.setdefault(key, fid)
        if not owner:
            problems.append(f"Facts: {fid} has no owner")
    defined = set(ids)
    cases = _table(cases_body)
    cited = {
        fid
        for row in (cases[1] if cases else [])
        if len(row) > 3
        for fid in _FACT_ID.findall(row[3])
    }
    problems += [
        f"Facts: {fid} is proved by no case" for fid in ids if fid not in cited
    ]
    problems += [
        f"Facts: {fid} is cited but not defined"
        for fid in sorted(set(_FACT_ID.findall(text)) - defined)
    ]
    return problems


def _is_text(path: pathlib.Path) -> bool:
    try:
        path.read_text()
    except UnicodeDecodeError:
        return False
    return True


def corpus() -> list[pathlib.Path]:
    """Every file a brief's author reads first: the whole skill and what governs it.

    Not a search: every shipped text file under the skill, the evals except their result
    records, the governing docs, and the CI READMEs the skill points into.
    """
    skill = [
        path
        for path in sorted(SKILL.rglob("*"))
        if path.is_file()
        and not any(
            part in path.relative_to(SKILL).as_posix() for part in SKILL_EXCLUDED
        )
        and _is_text(path)
    ]
    docs = [ROOT / "docs" / name for name in GOVERNING_DOCS]
    return skill + docs + [readme for readme in CI_READMES if readme.is_file()]


def required_reads(bodies: dict[str, str]) -> list[pathlib.Path]:
    """The corpus, then every local file the brief cites under Sources read."""
    repo_match = re.search(r"(?:^|\s)(/\S+)", bodies.get("Repository", ""))
    repo = pathlib.Path(repo_match[1]) if repo_match else ROOT
    cited = []
    for line in bodies.get("Sources read", "").splitlines():
        if not line.strip().startswith("- "):
            continue
        word = line.strip()[2:].split()[0].strip("`,")
        if "://" in word:
            continue
        path = pathlib.Path(word)
        path = path if path.is_absolute() else repo / path
        if path.is_file():
            cited.append(path)
    required = corpus()
    return required + [path for path in cited if path not in required]


def _whole_reads(session: str | None) -> dict[str, set[str]]:
    """Path to the hashes it was read whole at, in this session."""
    reads: dict[str, set[str]] = {}
    if not READ_LOG.is_file():
        return reads
    for line in READ_LOG.read_text().splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("session") == session and entry.get("full"):
            reads.setdefault(entry["path"], set()).add(entry["sha256"])
    return reads


def _check_reads(bodies: dict[str, str], session: str | None) -> list[str]:
    """Every required file read whole, in this session, at its current content."""
    reads = _whole_reads(session)
    problems = []
    for path in required_reads(bodies):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest not in reads.get(str(path.resolve()), set()):
            problems.append(f"not read in full at its current content: {path}")
    return problems


def _check_review(path: pathlib.Path, text: str) -> list[str]:
    review = path.with_suffix(".review")
    if not review.is_file():
        return [f"no case review: {review} does not exist"]
    lines = review.read_text().splitlines()
    digest = hashlib.sha256(text.encode()).hexdigest()
    if not lines or lines[0].strip() != digest:
        return [
            "case review is of an earlier version: its sha256 does not match the brief"
        ]
    verdict = lines[1].strip() if len(lines) > 1 else ""
    if verdict != "VERDICT: complete":
        return [
            f"case review did not pass: `{verdict or 'no verdict'}` — the review lists what is missing"
        ]
    return []


def validate(path: pathlib.Path, session: str | None = None) -> list[str]:
    """Every way the brief at path falls short of docs/brief.md."""
    if not path.is_file():
        return [f"{path} does not exist"]
    text = path.read_text()
    found = _sections(text)
    names = [name for name, _ in found]
    bodies = dict(found)
    problems = [f"missing section `## {s}`" for s in SECTIONS if s not in bodies]
    present = [n for n in names if n in SECTIONS]
    if present != [s for s in SECTIONS if s in bodies]:
        problems.append("sections are out of order; docs/brief.md gives the order")
    problems += [
        f"section `## {n}` is empty" for n, b in found if n in SECTIONS and not b
    ]
    if bodies.get("Repository") and not re.search(r"(^|\s)/\S", bodies["Repository"]):
        problems.append("Repository: no absolute path")
    if "Sources read" in bodies:
        outside = "\n".join(b for n, b in found if n != "Sources read")
        problems += _check_sources(bodies["Sources read"], outside)
    if bodies.get("Rules applied"):
        problems += _check_rules(
            bodies["Rules applied"],
            bodies.get("Files", ""),
            bodies.get("Sources read", ""),
        )
    if bodies.get("Files"):
        problems += _unread_files(bodies["Files"], bodies.get("Sources read", ""))
    if bodies.get("Cases"):
        problems += _check_cases(bodies["Cases"])
    if bodies.get("Facts"):
        problems += _check_facts(bodies["Facts"], bodies.get("Cases", ""), text)
    if bodies.get("Checks") and "```" not in bodies["Checks"]:
        problems.append("Checks: the commands are not in a fenced block")
    return problems + _check_reads(bodies, session) + _check_review(path, text)


def _resolve(raw: str) -> pathlib.Path:
    path = pathlib.Path(raw)
    return path if path.is_absolute() else ROOT / path


def _refusal(problems: dict[str, list[str]]) -> str:
    lines = [
        "[brief-gate] A build is dispatched only with a brief in the shape docs/brief.md gives."
    ]
    for name, found in problems.items():
        lines.append(f"{name}:")
        lines += [f"  - {p}" for p in found]
    return "\n".join(lines)


def decide(payload: dict) -> str | None:
    """The refusal for this tool call, or None to allow it."""
    tool = payload.get("tool_name")
    args = payload.get("tool_input") or {}
    if tool == "Agent":
        if args.get("subagent_type", "general-purpose") in READ_ONLY:
            return None
        paths = _BRIEF.findall(args.get("prompt", ""))
        if not paths:
            return _refusal(
                {"prompt": ["no `Brief: <path>` line; write the brief first"]}
            )
    elif tool == "Workflow":
        script = args.get("script") or ""
        if not script and args.get("scriptPath"):
            script_path = _resolve(args["scriptPath"])
            script = script_path.read_text() if script_path.is_file() else ""
        paths = _BRIEF.findall(script)
        if not paths:
            if "brief-gate: read-only" in script:
                return None
            return _refusal(
                {"script": ["names no brief, and does not say `brief-gate: read-only`"]}
            )
    else:
        return None
    session = payload.get("session_id")
    problems = {
        raw: found
        for raw in dict.fromkeys(paths)
        if (found := validate(_resolve(raw), session))
    }
    return _refusal(problems) if problems else None


def main() -> int:
    """Read the hook payload on stdin and deny the call when its brief falls short."""
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0  # Unparseable input is the harness's problem, not grounds to block.
    reason = decide(payload)
    if reason is None:
        return 0
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
