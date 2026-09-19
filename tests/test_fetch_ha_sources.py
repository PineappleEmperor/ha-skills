"""Tests for the release-source fetch, and for the artefact the gate holds the repo to.

Every fetch is injected, so none of these touch the network, and `main` is given a tmp root
because the real one empties and rewrites `docs/ha-release/`.

The last test is not a unit test at all: it reads the committed index and fails when it is
missing or names a release other than the one `freshness.md` does. That is what stops the
gate's source check being defeated by deleting the index — the gate fails open without one,
by design, so CI has to be what notices.
"""

import datetime as dt
import importlib.util
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import check_ha_release as chr_

_SPEC = importlib.util.spec_from_file_location(
    "fetch_ha_sources",
    Path(__file__).resolve().parents[1] / "scripts" / "fetch_ha_sources.py",
)
fhs = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(fhs)

REPO = Path(__file__).resolve().parents[1]

RELEASE_FEED = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>2026.9: There's room on this bus</title>
    <link href="https://www.home-assistant.io/blog/2026/09/02/release-20269/"/>
    <updated>2026-09-02T00:00:00+00:00</updated>
    <content type="html">&lt;p&gt;Notes body&lt;/p&gt;</content>
  </entry>
  <entry>
    <title>2026.8: Approachable by design</title>
    <link href="https://www.home-assistant.io/blog/2026/08/05/release-20268/"/>
    <updated>2026-08-05T00:00:00+00:00</updated>
    <content type="html">&lt;p&gt;Older notes&lt;/p&gt;</content>
  </entry>
  <entry>
    <title>FireAvert joins Works with Home Assistant</title>
    <link href="https://www.home-assistant.io/blog/2026/07/28/fireavert/"/>
    <updated>2026-07-28T00:00:00+00:00</updated>
    <content type="html">&lt;p&gt;Not a release&lt;/p&gt;</content>
  </entry>
</feed>
"""

DEV_FEED = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel>
  <item>
    <title>In the window</title>
    <link>https://developers.home-assistant.io/blog/2026/08/24/device-registry</link>
    <pubDate>Mon, 24 Aug 2026 00:00:00 GMT</pubDate>
  </item>
  <item>
    <title>On the release day itself</title>
    <link>https://developers.home-assistant.io/blog/2026/09/02/modbus</link>
    <pubDate>Wed, 02 Sep 2026 00:00:00 GMT</pubDate>
  </item>
  <item>
    <title>On the previous release day, so the previous window's</title>
    <link>https://developers.home-assistant.io/blog/2026/08/05/older</link>
    <pubDate>Wed, 05 Aug 2026 00:00:00 GMT</pubDate>
  </item>
  <item>
    <title>After the window</title>
    <link>https://developers.home-assistant.io/blog/2026/09/17/later</link>
    <pubDate>Thu, 17 Sep 2026 00:00:00 GMT</pubDate>
  </item>
</channel></rss>
"""

PAGE = (
    "<html><head><style>p{}</style></head><body><nav>menu</nav>"
    "<article><h1>Title</h1><p>First para.</p><script>x=1</script>"
    "<p>Second para.</p></article><footer>foot</footer></body></html>"
)


def _get(url: str) -> str:
    """Stand in for the network: the two feeds, and any post page."""
    if url == fhs.RELEASE_FEED:
        return RELEASE_FEED
    if url == fhs.DEV_FEED:
        return DEV_FEED
    return PAGE


# ------------------------------------------------------------------ extraction


def test_text_extraction_keeps_the_words_and_drops_the_furniture() -> None:
    """Script, style, nav and footer are muted; the article's paragraphs survive."""
    text = fhs.to_text(fhs.article_of(PAGE))
    assert "First para." in text
    assert "Second para." in text
    for dropped in ("x=1", "menu", "foot", "p{}"):
        assert dropped not in text
    assert "\n\n\n" not in text


def test_a_page_without_an_article_is_taken_whole() -> None:
    """Better a noisy source than a silently empty one, so the fallback is the page."""
    assert fhs.article_of("<html><body>bare</body></html>").endswith("</html>")


# ---------------------------------------------------------------------- feeds


def test_only_release_notes_entries_are_taken_from_the_release_feed() -> None:
    """The feed carries partnership and event posts too; a title decides."""
    found = fhs.release_posts(RELEASE_FEED)
    assert set(found) == {(2026, 9), (2026, 8)}
    assert found[(2026, 9)]["date"] == "2026-09-02"
    assert "Notes body" in found[(2026, 9)]["html"]


def test_the_post_window_excludes_the_previous_release_day() -> None:
    """A post dated the previous release day belongs to that window, not this one."""
    titles = {
        post["title"]
        for post in fhs.dev_posts(DEV_FEED, dt.date(2026, 8, 5), dt.date(2026, 9, 2))
    }
    assert titles == {"In the window", "On the release day itself"}


def test_the_window_runs_from_the_previous_release_to_this_one() -> None:
    """The anchor is the previous release's own date, not a fixed span."""
    releases = fhs.release_posts(RELEASE_FEED)
    assert fhs.window((2026, 9), releases) == (dt.date(2026, 8, 5), dt.date(2026, 9, 2))


def test_the_oldest_release_in_the_feed_falls_back_to_a_fixed_span() -> None:
    """With nothing earlier to anchor to, the window opens a fixed distance back."""
    releases = fhs.release_posts(RELEASE_FEED)
    start, end = fhs.window((2026, 8), releases)
    assert end == dt.date(2026, 8, 5)
    assert start == end - fhs._FALLBACK_WINDOW


def test_a_release_the_feed_does_not_carry_is_refused_not_guessed() -> None:
    """Off the end of the feed is a stop, because a silent empty window reads as done."""
    with pytest.raises(SystemExit):
        fhs.window((2025, 1), fhs.release_posts(RELEASE_FEED))


def test_the_slug_is_the_last_url_segment() -> None:
    """Filenames come from the post's own URL, so a refetch is idempotent."""
    assert (
        fhs.slug_of("https://example.com/blog/2026/09/02/Modbus_Get-Hub/")
        == "modbus-get-hub"
    )


# ----------------------------------------------------------------- end to end


def test_a_run_writes_every_source_and_an_index_that_names_them_all(tmp_path) -> None:
    """The index is the gate's input, so every file written must appear in it."""
    assert fhs.main(["--release", "2026.9"], get=_get, root=tmp_path) == 0
    out = tmp_path / "docs/ha-release"
    written = sorted(p.name for p in (out / "2026.9").iterdir())
    assert written == [
        "blog-2026-08-24-device-registry.md",
        "blog-2026-09-02-modbus.md",
        "release-notes.md",
    ]
    index = (out / "index.md").read_text(encoding="utf-8")
    for name in written:
        assert f"`docs/ha-release/2026.9/{name}`" in index
    assert "Notes body" in (out / "2026.9/release-notes.md").read_text(encoding="utf-8")
    assert "First para." in (out / "2026.9/blog-2026-09-02-modbus.md").read_text(
        encoding="utf-8"
    )


def test_a_second_run_replaces_the_window_rather_than_accumulating(tmp_path) -> None:
    """A stale release left behind would be demanded forever by the gate."""
    fhs.main(["--release", "2026.8"], get=_get, root=tmp_path)
    fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)
    out = tmp_path / "docs/ha-release"
    assert sorted(p.name for p in out.iterdir() if p.is_dir()) == ["2026.9"]


def test_since_widens_the_window_to_several_releases(tmp_path) -> None:
    """A backfill pass covers every release between the two, as 2026.6-2026.9 did."""
    fhs.main(["--since", "2026.8", "--release", "2026.9"], get=_get, root=tmp_path)
    out = tmp_path / "docs/ha-release"
    assert sorted(p.name for p in out.iterdir() if p.is_dir()) == ["2026.8", "2026.9"]


# ------------------------------------------------------- the committed artefact


def test_the_committed_index_covers_the_release_the_skill_claims() -> None:
    """The gate fails open without an index, so this is what makes deleting it visible.

    It is also the check that keeps a pass honest: fetching moves the index, writing the
    rows moves the release row, and only when both have happened is the suite green.
    """
    index = REPO / "docs/ha-release/index.md"
    assert index.exists(), "run scripts/fetch_ha_sources.py"
    text = index.read_text(encoding="utf-8")
    year, minor = chr_.captured_minor(
        (REPO / chr_.DEFAULT_FILE).read_text(encoding="utf-8")
    )
    assert f"docs/ha-release/{year}.{minor}/release-notes.md" in text
    named = [
        line.split("`")[1]
        for line in text.splitlines()
        if line.startswith("| `docs/ha-release/")
    ]
    assert named, "the index names no sources"
    for rel in named:
        assert (REPO / rel).exists(), f"{rel} is named by the index but absent"
