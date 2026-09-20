#!/usr/bin/env python3
# skill-audit: local-tool
"""Pull a release window's own sources into `docs/ha-release/`, so the gate can demand them.

*When the release row goes red* in `reference/freshness.md` says to open every developer-blog
post in the window and the release notes beside them before writing a word of the refresh.
Nothing made that true. The 2026.9 pass wrote rows from memory, got eight facts wrong, and
the rule it broke was its own — row 220. A rule with no artefact is a note to a future
reader, so this turns the sources into files: the gate then refuses a patch to `reference/`
that names a release until every one of those files has been served whole.

WHAT IT FETCHES, and why both. Neither source contains the other, which *When the release row
goes red* records from the 2026.9 pair: the release notes linked three of that window's posts,
and carried nine backward-incompatible changes that had no post at all.
  * every developer-blog post published in the window THAT THE FEED STILL CARRIES, each
    post's own page fetched because the feed carries only an excerpt. The feed holds a fixed
    number of entries, so a backfill reaching further back than it does collects what is
    left rather than what was published, and the run says so when a window comes up empty;
  * the *Backward-incompatible changes* section of the release-notes post for each release
    in the window, taken from the post's own markdown in `home-assistant/home-assistant.io`
    rather than from the rendered page. Nine tenths of such a post is feature prose and
    patch-release dependency bumps; the section that is kept is the part that can break a
    custom integration, and the part the developer blog does not carry. The Atom feed is
    still read, for each release's title, date and link, and for the post body `dev_links`
    recovers aged-out posts from.

WHAT IT IS NOT. A fetched post is a secondary source, and saving one here does not make it
primary: the same section of `freshness.md` says core at the tag is the source of record. This
makes the reading enforceable, not the claims true.

The window ends at the release named on the command line, defaulting to the one
`freshness.md` names, and starts after the previous release — so a post published the week
after a release belongs to the *next* window, which is where it describes a change landing.
"""

from collections.abc import Callable
import datetime as dt
from email.utils import parsedate_to_datetime
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.check_ha_release import captured_minor

DEV_FEED = "https://developers.home-assistant.io/blog/rss.xml"
RELEASE_FEED = "https://www.home-assistant.io/atom.xml"
FRESHNESS = "plugins/ha/skills/ha-integration/reference/freshness.md"
OUT_DIR = "docs/ha-release"
INDEX = "index.md"
ATOM = {"a": "http://www.w3.org/2005/Atom"}
USER_AGENT = "ha-skills-source-fetch (+https://github.com/PineappleEmperor/ha-skills)"

# A release-notes post titles itself with the release: "2026.9: There's room on this bus".
_RELEASE_TITLE = re.compile(r"^(\d{4})\.(\d{1,2}):")
# How far back to look for posts when the previous release's own post is not in the feed.
_FALLBACK_WINDOW = dt.timedelta(days=40)

_BLOCK = {
    "p",
    "div",
    "br",
    "li",
    "tr",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "pre",
    "section",
    "article",
    "ul",
    "ol",
    "table",
    "blockquote",
}
_SKIP = {"script", "style", "nav", "footer", "svg", "button", "form"}

# What each host says about reuse, carried into every file taken from it. CC BY-NC-SA 4.0
# section 3(a) asks a copy to retain the creator credit, the copyright notice, a notice
# referring to the licence and its disclaimer, a link to the material, and an indication of
# modification. The credit and the link are the "Copyright (c)" and "Fetched from" lines
# below; the licence notice and its disclaimer are what the licence URI carries, which is
# what section 3(a)(2) allows.
# ShareAlike, section 3(b), binds only an Adapter's Licence over Adapted Material, so it
# would attach to these files and never to the repository around them either way. Whether
# stripping navigation, scripts and link targets is a "technical modification necessary"
# under section 2(a)(4), and so leaves these verbatim copies, is a reading rather than a
# certainty — which is why the note below says what was dropped instead of asserting it.
# Keyed by URL PREFIX, longest match first, because one host is not one set of terms:
# raw.githubusercontent.com serves home-assistant.io under CC BY-NC-SA and core under
# Apache-2.0, and a host key would have stamped the first onto the second.
_HA_IO = (
    "Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 "
    "(https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of "
    "home-assistant/home-assistant.io."
)
LICENCES = {
    "https://www.home-assistant.io/": _HA_IO,
    "https://raw.githubusercontent.com/home-assistant/home-assistant.io/": _HA_IO,
    "https://developers.home-assistant.io/": (
        "Copyright (c) Home Assistant contributors. The developer documentation repository "
        "publishes no licence; this copy is kept for reference and attribution only."
    ),
}
_MODIFIED_HTML = (
    "Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps "
    "the article body and loses everything the markup carried — navigation and chrome, link "
    "targets, image alt text, table and list structure, and code formatting. No wording has "
    "been changed, added or reordered."
)
_MODIFIED_SLICE = (
    "Modified: this is the *Backward-incompatible changes* section of the post's own source "
    "markdown, cut at the surrounding `##` headings by `scripts/fetch_ha_sources.py`. "
    "Nothing inside it has been changed, added or reordered; the rest of the post — the "
    "feature write-ups and the patch-release changelogs — is not kept."
)


class _Text(HTMLParser):
    """Readable text out of an HTML fragment. Structure is lost; the words are not."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._muted = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP:
            self._muted += 1
        elif tag in _BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP and self._muted:
            self._muted -= 1
        elif tag in _BLOCK:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._muted:
            self.parts.append(data)

    def text(self) -> str:
        """The collected words, with runs of blank lines collapsed to one."""
        joined = "".join(self.parts)
        lines = [line.strip() for line in joined.splitlines()]
        out: list[str] = []
        for line in lines:
            if line or (out and out[-1]):
                out.append(line)
        return "\n".join(out).strip() + "\n"


class _Links(HTMLParser):
    """Every `href` in a fragment, with the words that linked to it."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            self.found.append((self._href, "".join(self._text).strip()))
            self._href = None


def dev_links(html: str) -> list[tuple[str, str]]:
    """Developer-blog posts a release-notes body links to, as (url, link text).

    The feed window is a net with a hole: the developer feed holds a fixed number of entries,
    so a backfill reaching past it collects what is left. Measured on the first run — 2026.6's
    notes name nine posts for that window and the feed still carried one, and nothing said so,
    because the run only warns at zero. The notes are the other half of the net.

    They are not a free pass: a release's notes also link posts from earlier windows, and
    filing those here produced a byte-identical copy of 2026.8's modbus post under 2026.9. So
    the caller holds a recovered post to the same dates as the feed half, and says on stderr
    when it drops one, because a post the notes name and the window rejects is either a post
    for another release or a window whose start is the fallback span rather than a real one.
    """
    parser = _Links()
    parser.feed(html)
    seen: dict[str, str] = {}
    for href, text in parser.found:
        url = href.split("#")[0].split("?")[0].rstrip("/")
        if url.startswith("https://developers.home-assistant.io/blog/"):
            seen.setdefault(url, text)
    return sorted(seen.items())


def post_from_url(url: str, title: str) -> dict[str, str] | None:
    """A post entry built from its own URL, for one the feed no longer carries.

    The date is built through `datetime.date`, not by joining three path segments: that
    accepted `/blog/2026/7/5/x` and produced `2026-7-5`, which becomes the filename and the
    sort key. And the link text is only a title when it reads like one — a release note that
    links a post as "here" would otherwise file it under `# here`, so anything shorter than a
    phrase falls back to the slug.
    """
    parts = urllib.parse.urlsplit(url).path.strip("/").split("/")
    if len(parts) < 5 or parts[0] != "blog":
        return None
    try:
        when = dt.date(int(parts[1]), int(parts[2]), int(parts[3]))
    except ValueError:
        return None
    return {
        "title": title if len(title) >= 15 else parts[4].replace("-", " "),
        "url": url,
        "date": when.isoformat(),
    }


def provenance(url: str, modification: str = _MODIFIED_HTML) -> str:
    """The attribution block every fetched file carries, per that URL's terms."""
    match = max((p for p in LICENCES if url.startswith(p)), key=len, default="")
    licence = LICENCES.get(match, "Copyright (c) its authors; no licence is stated.")
    return f"Fetched from {url}\n{licence}\n{modification}"


def notes_markdown_url(post_url: str) -> str:
    """The release-notes post's source markdown in `home-assistant/home-assistant.io`.

    The rendered page has to be flattened to text, and that drops exactly what this section
    is read for: the backticks around an API name and the PR link behind each entry — the
    two things *A post is not the source of record* sends a reader to core with. The
    repository's own markdown keeps both, and its `##` headings make the cut below exact
    rather than a match on a phrase that also appears in the page's table of contents.
    """
    parts = urllib.parse.urlsplit(post_url).path.strip("/").split("/")
    if len(parts) != 5 or parts[0] != "blog":
        raise SystemExit(f"{post_url} is not a post URL this can find the markdown for")
    year, month, day, slug = parts[1:]
    return (
        "https://raw.githubusercontent.com/home-assistant/home-assistant.io/master/"
        f"source/_posts/{year}-{month}-{day}-{slug}.markdown"
    )


def breaking_changes(markdown: str, release: str) -> str:
    """The *Backward-incompatible changes* section of a release-notes post, and only it.

    Measured over 2026.6-2026.9: the four posts run to 215 KB and this section to 25 KB of
    it, the remainder being feature write-ups and three patch-release changelogs of
    dependency bumps, none of which a custom integration can act on. The section ends with
    the post's own list of the release's notable developer-blog posts, which is the one
    place the two sources cross-reference each other.

    An absent heading stops the run rather than falling back to the whole post or to
    nothing: a silently empty source is what the gate would then certify as read.
    """
    heading = "## Backward-incompatible changes"
    start = markdown.find(f"\n{heading}\n")
    if start == -1:
        raise SystemExit(
            f"{release}'s release-notes markdown carries no {heading!r} heading; the post's "
            "shape has changed, and slicing it here would write an empty source"
        )
    body = markdown[start + 1 :]
    end = body.find("\n## ", len(heading))
    return (body if end == -1 else body[:end]).strip() + "\n"


def to_text(html: str) -> str:
    """Strip an HTML fragment to text, keeping only what a reader would read."""
    parser = _Text()
    parser.feed(html)
    return parser.text()


def article_of(page: str) -> str:
    """The <article> of a developer-blog page, or the whole page when it has none."""
    start = page.find("<article")
    end = page.find("</article>")
    if start == -1 or end == -1 or end < start:
        return page
    return page[start:end]


def fetch(url: str) -> str:
    """Read a URL as text; the injection point, so no test touches the network.

    The User-Agent is not decoration: home-assistant.io's CDN answers `urllib`'s default with
    403, and the failure looks like an outage rather than a rejected client.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def _parse(feed: str) -> ET.Element:
    """Parse a feed. Two HTTPS endpoints of home-assistant.io, not untrusted input.

    `defusedxml` would be the answer to a hostile feed, and it is not a dependency: CI
    installs pytest and pyyaml, and this script is deliberately stdlib-only. The exposure is
    an entity-expansion bomb served by home-assistant.io itself, at which point the sources
    the whole procedure rests on are compromised anyway.
    """
    return ET.fromstring(feed)  # noqa: S314 - the project's own feeds, reasoned above


def release_posts(feed: str) -> dict[tuple[int, int], dict[str, str]]:
    """Every release-notes entry the Atom feed carries, keyed by (year, minor)."""
    found: dict[tuple[int, int], dict[str, str]] = {}
    for entry in _parse(feed).findall("a:entry", ATOM):
        title = entry.findtext("a:title", default="", namespaces=ATOM)
        match = _RELEASE_TITLE.match(title)
        if not match:
            continue
        content = entry.find("a:content", ATOM)
        link = entry.find("a:link", ATOM)
        date = entry.findtext("a:updated", default="", namespaces=ATOM)[:10]
        # A release entry missing its link or its date is not something to write a folder
        # from: an absent link used to raise AttributeError and an absent date a ValueError,
        # both of them after the folder had already been emptied.
        if link is None or len(date) != 10:
            raise SystemExit(f"the feed entry for {title!r} carries no link or no date")
        found[(int(match.group(1)), int(match.group(2)))] = {
            "title": title,
            "url": link.get("href", ""),
            "date": date,
            "html": "".join(content.itertext()) if content is not None else "",
        }
    return found


def dev_posts(feed: str, after: dt.date, until: dt.date) -> list[dict[str, str]]:
    """Developer-blog entries published in (after, until], newest first."""
    found: list[dict[str, str]] = []
    for item in _parse(feed).findall(".//item"):
        raw = item.findtext("pubDate")
        if not raw:
            continue
        when = parsedate_to_datetime(raw).date()
        if after < when <= until:
            found.append(
                {
                    "title": item.findtext("title") or "",
                    "url": item.findtext("link") or "",
                    "date": when.isoformat(),
                }
            )
    return found


def slug_of(url: str) -> str:
    """The last path segment of a post URL, lowercased, as the filename stem."""
    return re.sub(r"[^a-z0-9-]+", "-", url.rstrip("/").rsplit("/", 1)[-1].lower())


def window(
    release: tuple[int, int], releases: dict[tuple[int, int], dict[str, str]]
) -> tuple[dt.date, dt.date]:
    """The dates a release's posts fall between: after the previous release, up to this one.

    A post published the week after a release describes a change landing in the next one, so
    the window is exclusive at its start. When the previous release is off the end of the
    feed there is nothing to anchor to, and the window opens a fixed span earlier instead.
    """
    if release not in releases:
        raise SystemExit(
            f"the feed carries no release notes for {release[0]}.{release[1]}; it reaches back "
            f"to {min(releases)[0]}.{min(releases)[1]}"
        )
    end = dt.date.fromisoformat(releases[release]["date"])
    earlier = [d for d in releases if d < release]
    if not earlier:
        return end - _FALLBACK_WINDOW, end
    return dt.date.fromisoformat(releases[max(earlier)]["date"]), end


def write_release(
    out: Path,
    release: tuple[int, int],
    notes: dict[str, str],
    posts: list[dict[str, str]],
    get: Callable[[str], str],
) -> int:
    """Replace one release's folder, returning how many posts it now holds.

    Every page is fetched before anything is written. A fetch that fails halfway — one 403,
    one timeout, and there is no retry — would otherwise leave the folder emptied and
    half-filled, and a half-filled folder is what the gate would then certify as every
    source read. The notes are sliced here too, before the first write, so a post whose
    shape has changed stops the run instead of replacing a folder with an empty source.
    """
    name = f"{release[0]}.{release[1]}"
    notes_url = notes_markdown_url(notes["url"])
    notes_body = breaking_changes(get(notes_url), name)
    fetched = [
        (
            f"blog-{post['date']}-{slug_of(post['url'])}.md",
            f"# {post['title']}\n\n{provenance(post['url'])}\n\n"
            f"{to_text(article_of(get(post['url'])))}",
        )
        for post in sorted(posts, key=lambda p: p["date"])
    ]
    folder = out / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    (folder / "release-notes.md").write_text(
        f"# {notes['title']} — backward-incompatible changes\n\n"
        f"{provenance(notes_url, _MODIFIED_SLICE)}\n\n{notes_body}",
        encoding="utf-8",
    )
    for filename, body in fetched:
        (folder / filename).write_text(body, encoding="utf-8")
    return len(fetched)


def _header(path: Path) -> tuple[str, str]:
    """The title and source URL a fetched file records in its own opening lines."""
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("#").strip() if lines else path.stem
    url = next(
        (
            line[len("Fetched from ") :].strip()
            for line in lines[:6]
            if line.startswith("Fetched from ")
        ),
        "",
    )
    return title, url


def digest(path: Path) -> str:
    """The first twelve hex characters of a file's SHA-256, which the index records.

    The gate can refuse to patch these files, and a demand list taken from the directory
    survives one. Neither notices a file emptied outside the gate, so the index carries a
    hash and the suite compares it: a source that has been hollowed out stops matching the
    line that says what it is.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def sources_on_disk(out: Path) -> list[tuple[str, str, str, str]]:
    """Every fetched file with its hash, oldest release first, notes before posts.

    Read from the directory rather than from what this run happened to fetch, so that a run
    for one release leaves the releases beside it listed. The gate reads the same directory,
    which is what keeps the two from disagreeing.
    """
    rows: list[tuple[str, str, str, str]] = []
    # Only folders named for a release, and named the way the gate reads them. The gate skips
    # a folder whose name does not parse; this used to sort by it and raise, so a stray
    # directory was invisible to one reader and fatal to the other.
    releases = [p for p in out.iterdir() if p.is_dir() and _is_release(p.name)]
    for folder in sorted(releases, key=lambda p: _minor(p.name)):
        for path in sorted(
            (f for f in folder.iterdir() if f.is_file()),
            key=lambda f: (f.name != "release-notes.md", f.name),
        ):
            title, url = _header(path)
            rows.append(
                (f"{OUT_DIR}/{folder.name}/{path.name}", title, url, digest(path))
            )
    return rows


def recorded_digests(out: Path) -> dict[str, str]:
    """What the index on disk says each source hashes to.

    Empty only before the first fetch. Once releases exist, a missing index is refused rather
    than treated as nothing to compare against: emptying a source and deleting the index made
    the next run re-sign it, which is the check paying for its own input. A row deleted from
    an otherwise-present index does the same thing one file at a time, and is caught in the
    diff and by `test_the_committed_index_and_the_committed_folders_agree` rather than here.
    """
    try:
        text = (out / INDEX).read_text(encoding="utf-8")
    except OSError:
        if any(p.is_dir() and _is_release(p.name) for p in out.iterdir()):
            raise SystemExit(
                f"{OUT_DIR}/{INDEX} is missing while fetched releases are present; restore it "
                f"before fetching, or the run would re-sign whatever has changed under it"
            ) from None
        return {}
    found: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith(f"| `{OUT_DIR}/"):
            cells = [cell.strip(" `") for cell in line.strip("|").split("|")]
            if len(cells) >= 2:
                found[cells[0]] = cells[1]
    return found


def verify_untouched(out: Path, refetching: set[str]) -> None:
    """Refuse to proceed when a release this run will not refetch has changed under us.

    A source emptied or edited in place is caught by comparing the hashes the index records —
    and the index is rewritten, for every release, on every run. So a fetch for one release
    re-signed whatever had been tampered with in the others and the suite went green again:
    the guard erased its own evidence. Checked BEFORE the first folder is replaced, because a
    refusal raised afterwards leaves exactly the half-written tree `write_release` goes out of
    its way to avoid.
    """
    if not out.is_dir():
        return
    known = recorded_digests(out)
    for path, _, _, sha in sources_on_disk(out):
        release = path.split("/")[2]
        if release not in refetching and path in known and known[path] != sha:
            raise SystemExit(
                f"{path} no longer matches the hash the index records, and this run would "
                f"not refetch {release}. Restore it, or refetch that release deliberately; "
                f"re-signing it here would hide whatever changed it."
            )


def write_index(out: Path, today: str) -> str:
    """Write the index over everything on disk, and return it."""
    rows = sources_on_disk(out)
    named = ", ".join(sorted({row[0].split("/")[2] for row in rows}, key=_minor))
    lines = [
        f"# The sources for Home Assistant {named}",
        "",
        "Fetched by `scripts/fetch_ha_sources.py`, last on "
        + today
        + ". Every file below",
        "is a **secondary** source: it says what changed and why, and never how an API is",
        "spelled — core at the release tag says that, and the paragraph beginning *A post is",
        "not the source of record* under *When the release row goes red* in",
        "`plugins/ha/skills/ha-integration/reference/freshness.md` says why.",
        "",
        "The governance gate reads this directory and demands these files before it will let",
        "a reference file make a claim about one of the releases below. What exactly it",
        "demands, and what it does not, is `unread_sources` in `scripts/governance_gate.py`,",
        "which is the only place that rule is stated; re-run the script to add a release.",
        "",
        "**The window is a net, not a claim.** Posts are gathered by publication date, between",
        "one release and the next, and a post published in the days before a release usually",
        "describes the release *after* it — the beta was cut a week earlier. The 2026.9 window",
        "caught a configurator-deprecation post dated two days before 2026.9 shipped, and",
        "`configurator/__init__.py` at the `2026.9.0` tag carries no deprecation at all. Which",
        "release a change is actually in is core's to answer, never the post's. The net has a",
        "hole of its own at the far end: the developer blog's feed carries a fixed number of",
        "entries, so a backfill reaching further back than the feed does collects only the",
        "posts still in it.",
        "",
        "Each file opens with its own source URL and the terms the host publishes it under,",
        "and the `sha256` below is the first twelve characters of that file's hash — the",
        "suite compares them, so a source emptied or altered in place stops matching the line",
        "that says what it is.",
        "",
        "| Source | sha256 | What it is |",
        "|---|---|---|",
    ]
    lines += [
        f"| `{path}` | `{sha}` | [{title}]({url}) |" for path, title, url, sha in rows
    ]
    text = "\n".join(lines) + "\n"
    (out / INDEX).write_text(text, encoding="utf-8")
    return text


def main(
    argv: list[str] | None = None,
    get: Callable[[str], str] = fetch,
    root: Path | None = None,
) -> int:
    """Fetch the window and write the index. 0 on success; a SystemExit message otherwise.

    `root` is injected only by the suite. Left to compute its own, this function rewrites
    the real `docs/ha-release/` — each requested release's folder replaced, the rest left
    alone — so an end-to-end test of it would rewrite the sources the gate is holding the
    repository to.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    root = root or Path(__file__).resolve().parents[1]
    releases = release_posts(get(RELEASE_FEED))

    if "--release" in args:
        end = _minor(args[args.index("--release") + 1])
    else:
        end = captured_minor((root / FRESHNESS).read_text(encoding="utf-8"))
    start = _minor(args[args.index("--since") + 1]) if "--since" in args else end
    # Both ends are checked against the feed, not just filtered by it. Filtering alone let
    # `--release 2026.10` on a feed that stops at 2026.9 exit 0 over a window it never
    # fetched, which then reads as a window nobody needs to fetch.
    for edge in {start, end}:
        window(edge, releases)
    wanted = sorted(r for r in releases if start <= r <= end)

    dev = get(DEV_FEED)
    out = root / OUT_DIR
    verify_untouched(out, {f"{year}.{minor}" for year, minor in wanted})
    out.mkdir(parents=True, exist_ok=True)
    for release in wanted:
        after, until = window(release, releases)
        notes = releases[release]
        posts = dev_posts(dev, after, until)
        # The notes are the second half of the net. A post the feed has aged out is still
        # linked from the release it shipped in, and without this a backfill quietly kept
        # one of the nine posts 2026.6's notes name.
        known = {post["url"].rstrip("/") for post in posts}
        linked = 0
        for url, text in dev_links(notes["html"]):
            if url in known:
                continue
            recovered = post_from_url(url, text)
            if not recovered:
                continue
            # Same window as the feed half, or the notes drag in whatever they happen to
            # link: 2026.9's notes link the 2026-07-05 modbus post, and the first version
            # filed a byte-identical copy of 2026.8's source under 2026.9.
            if after < dt.date.fromisoformat(recovered["date"]) <= until:
                posts.append(recovered)
                linked += 1
            else:
                print(
                    f"  {url} is linked by {release[0]}.{release[1]}'s notes but dated "
                    f"{recovered['date']}, outside ({after}, {until}]; not filed here",
                    file=sys.stderr,
                )
        count = write_release(out, release, notes, posts, get)
        found = f"{count} post(s)" + (
            f", {linked} of them from the notes" if linked else ""
        )
        print(f"{release[0]}.{release[1]}: release notes and {found}")
        if not count:
            print(
                f"  no developer-blog post is dated in ({after}, {until}] and the notes link "
                f"none; the feed may no longer reach that far back",
                file=sys.stderr,
            )
    write_index(out, dt.datetime.now(dt.UTC).date().isoformat())
    return 0


def _minor(value: str) -> tuple[int, int]:
    year, _, minor = value.strip().partition(".")
    return int(year), int(minor)


def _is_release(name: str) -> bool:
    """Whether a folder name is one the gate will read as a release. Same rule, one place."""
    year, _, minor = name.partition(".")
    return year.isdigit() and minor.isdigit()


if __name__ == "__main__":
    sys.exit(main())
