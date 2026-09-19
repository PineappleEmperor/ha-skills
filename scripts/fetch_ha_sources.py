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
  * every developer-blog post published in the window, from that blog's RSS feed, each post's
    own page fetched because the feed carries only an excerpt;
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
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import sys
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
        found[(int(match.group(1)), int(match.group(2)))] = {
            "title": title,
            "url": entry.find("a:link", ATOM).get("href", ""),
            "date": entry.findtext("a:updated", default="", namespaces=ATOM)[:10],
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
) -> list[tuple[str, str, str]]:
    """Write one release's sources, returning (path, title, url) for the index, in read order."""
    folder = out / f"{release[0]}.{release[1]}"
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    written: list[tuple[str, str, str]] = []

    body = (
        f"# {notes['title']}\n\nFetched from {notes['url']}\n\n{to_text(notes['html'])}"
    )
    path = folder / "release-notes.md"
    path.write_text(body, encoding="utf-8")
    written.append((str(path), notes["title"], notes["url"]))

    for post in sorted(posts, key=lambda p: p["date"]):
        text = to_text(article_of(get(post["url"])))
        path = folder / f"blog-{post['date']}-{slug_of(post['url'])}.md"
        path.write_text(
            f"# {post['title']}\n\nFetched from {post['url']}\n\n{text}",
            encoding="utf-8",
        )
        written.append((str(path), post["title"], post["url"]))
    return written


def write_index(
    out: Path,
    releases: list[tuple[int, int]],
    rows: list[tuple[str, str, str]],
    today: str,
) -> str:
    """Write the index the gate reads, and return it."""
    named = ", ".join(f"{year}.{minor}" for year, minor in releases)
    lines = [
        f"# The sources for Home Assistant {named}",
        "",
        "Fetched by `scripts/fetch_ha_sources.py` on "
        + today
        + ". Every file below is a",
        "**secondary** source: it says what changed and why, and never how an API is spelled —",
        "core at the release tag says that, per *A post is not the source of record* in",
        "`plugins/ha/skills/ha-integration/reference/freshness.md`.",
        "",
        "The governance gate refuses a patch to `plugins/ha/skills/ha-integration/reference/`",
        "that names a release until it has served every file named here, so this list is what",
        '"open every source" means in practice. Re-run the script to move the window.',
        "",
        "**The window is a net, not a claim.** Posts are gathered by publication date, between",
        "one release and the next, and a post published in the days before a release usually",
        "describes the release *after* it — the beta was cut a week earlier. The 2026.9 window",
        "caught a configurator-deprecation post dated three days before 2026.9 shipped, and",
        "`configurator/__init__.py` at the `2026.9.0` tag carries no deprecation at all. Which",
        "release a change is actually in is core's to answer, never the post's.",
        "",
        "| Source | What it is |",
        "|---|---|",
    ]
    lines += [f"| `{path}` | [{title}]({url}) |" for path, title, url in rows]
    text = "\n".join(lines) + "\n"
    (out / INDEX).write_text(text, encoding="utf-8")
    return text


def main(
    argv: list[str] | None = None,
    get: Callable[[str], str] = fetch,
    root: Path | None = None,
) -> int:
    """Fetch the window and write the index. 0 on success; a SystemExit message otherwise.

    `root` is injected only by the suite. Left to compute its own, this function empties and
    rewrites the real `docs/ha-release/`, so an end-to-end test of it would destroy the
    sources the gate is holding the repository to.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    root = root or Path(__file__).resolve().parents[1]
    releases = release_posts(get(RELEASE_FEED))

    if "--release" in args:
        end = _minor(args[args.index("--release") + 1])
    else:
        end = captured_minor((root / FRESHNESS).read_text(encoding="utf-8"))
    start = _minor(args[args.index("--since") + 1]) if "--since" in args else end
    wanted = sorted(r for r in releases if start <= r <= end)
    if not wanted:
        raise SystemExit(f"no release between {start} and {end} is in the feed")

    dev = get(DEV_FEED)
    out = root / OUT_DIR
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    rows: list[tuple[str, str, str]] = []
    for release in wanted:
        after, until = window(release, releases)
        rows += write_release(
            out, release, releases[release], dev_posts(dev, after, until), get
        )
    for path, _, _ in rows:
        print(path)
    write_index(
        out,
        wanted,
        [(str(Path(path).relative_to(root)), title, url) for path, title, url in rows],
        dt.datetime.now(dt.UTC).date().isoformat(),
    )
    return 0


def _minor(value: str) -> tuple[int, int]:
    year, _, minor = value.strip().partition(".")
    return int(year), int(minor)


if __name__ == "__main__":
    sys.exit(main())
