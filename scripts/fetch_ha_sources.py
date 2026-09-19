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
  * the release-notes post for each release in the window, whole, from home-assistant.io's
    Atom feed, which unlike the developer feed carries the entire body.

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

# What each host says about reuse, carried into every file taken from it. This is the
# licence's own condition rather than politeness: CC BY-NC-SA 4.0 section 3(a) asks that a
# copy retain the copyright notice, a notice referring to the licence, a link to the
# material, and an indication that it was modified. Section 2(a)(4) settles the other half —
# a format change "never produces Adapted Material", so converting HTML to text leaves these
# verbatim copies rather than adaptations, and ShareAlike is not triggered.
LICENCES = {
    "www.home-assistant.io": (
        "Copyright (c) Home Assistant contributors. Licensed CC BY-NC-SA 4.0 "
        "(https://creativecommons.org/licenses/by-nc-sa/4.0/), per LICENSE.md of "
        "home-assistant/home-assistant.io."
    ),
    "developers.home-assistant.io": (
        "Copyright (c) Home Assistant contributors. The developer documentation repository "
        "publishes no licence; this copy is kept for reference and attribution only."
    ),
}
_MODIFIED = (
    "Modified only in format: converted from HTML to plain text by "
    "`scripts/fetch_ha_sources.py`. The wording is the author's, unaltered."
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
    because the run only warns at zero. The notes are the other half of the net: they link the
    posts that mattered enough to announce, whatever the feed has dropped.
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
    """A post entry built from its own URL, for one the feed no longer carries."""
    parts = urllib.parse.urlsplit(url).path.strip("/").split("/")
    if len(parts) < 5 or parts[0] != "blog":
        return None
    year, month, day = parts[1:4]
    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        return None
    return {
        "title": title or parts[4].replace("-", " "),
        "url": url,
        "date": f"{year}-{month}-{day}",
    }


def provenance(url: str) -> str:
    """The attribution block every fetched file carries, per its host's terms."""
    host = urllib.parse.urlsplit(url).netloc
    licence = LICENCES.get(host, "Copyright (c) its authors; no licence is stated.")
    return f"Fetched from {url}\n{licence}\n{_MODIFIED}"


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
    source read.
    """
    fetched = [
        (
            f"blog-{post['date']}-{slug_of(post['url'])}.md",
            f"# {post['title']}\n\n{provenance(post['url'])}\n\n"
            f"{to_text(article_of(get(post['url'])))}",
        )
        for post in sorted(posts, key=lambda p: p["date"])
    ]
    folder = out / f"{release[0]}.{release[1]}"
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    (folder / "release-notes.md").write_text(
        f"# {notes['title']}\n\n{provenance(notes['url'])}\n\n{to_text(notes['html'])}",
        encoding="utf-8",
    )
    for name, body in fetched:
        (folder / name).write_text(body, encoding="utf-8")
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
    for folder in sorted(
        (p for p in out.iterdir() if p.is_dir()), key=lambda p: _minor(p.name)
    ):
        for path in sorted(
            (f for f in folder.iterdir() if f.is_file()),
            key=lambda f: (f.name != "release-notes.md", f.name),
        ):
            title, url = _header(path)
            rows.append(
                (f"{OUT_DIR}/{folder.name}/{path.name}", title, url, digest(path))
            )
    return rows


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
        "The governance gate refuses a patch to a file under",
        "`plugins/ha/skills/ha-integration/reference/` that names one of the releases below",
        "until it has served that release's own files. Any release with no non-empty folder",
        "here is not demanded, because nothing here could settle it — one older than the",
        "oldest fetched, a gap inside the span, or a removal release a year out. The single",
        "exception is the minor immediately after the newest below: that is the one a pass is",
        "about to write about, so an absent folder there means the fetch was skipped, and the",
        'gate says so. This list is what "open every source" means in practice; re-run the',
        "script to add a release.",
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
            if recovered:
                posts.append(recovered)
                linked += 1
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


if __name__ == "__main__":
    sys.exit(main())
