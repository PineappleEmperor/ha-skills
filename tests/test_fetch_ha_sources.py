"""Tests for the release-source fetch, and for the artefact the gate holds the repo to.

Every fetch is injected, so none of these touch the network, and `main` is given a tmp root
because the real one rewrites the committed `docs/ha-release/`.

The last three tests are not unit tests at all. They read the committed `docs/ha-release/`
and fail when the release `freshness.md` names has no folder, when the index and the folders
disagree, or when a committed source no longer hashes to what the index records. The gate
fails open with nothing fetched and cannot notice its own absence, and it can refuse to
patch a source but not to have one emptied outside it — so CI is what notices both.
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
    """The index says where each file came from, so every file written must appear in it."""
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


def test_a_later_run_adds_a_release_and_keeps_the_ones_beside_it(tmp_path) -> None:
    """A window that moved on must not un-gate every row written about the one before it.

    The first version emptied the whole directory on each run, so fetching 2026.9 removed
    2026.8's sources and, with them, the gate's hold on every 2026.8 row.
    """
    fhs.main(["--release", "2026.8"], get=_get, root=tmp_path)
    fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)
    out = tmp_path / "docs/ha-release"
    assert sorted(p.name for p in out.iterdir() if p.is_dir()) == ["2026.8", "2026.9"]
    index = (out / "index.md").read_text(encoding="utf-8")
    assert "`docs/ha-release/2026.8/release-notes.md`" in index
    assert "`docs/ha-release/2026.9/release-notes.md`" in index


def test_the_index_and_the_directory_describe_the_same_files(tmp_path) -> None:
    """Both are read — the gate reads the directory, a person reads the index."""
    fhs.main(["--since", "2026.8", "--release", "2026.9"], get=_get, root=tmp_path)
    out = tmp_path / "docs/ha-release"
    on_disk = {row[0] for row in fhs.sources_on_disk(out)}
    named = {
        line.split("`")[1]
        for line in (out / "index.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("| `docs/ha-release/")
    }
    assert named == on_disk


def test_since_widens_the_window_to_several_releases(tmp_path) -> None:
    """A backfill pass covers every release between the two, as 2026.6-2026.9 did."""
    fhs.main(["--since", "2026.8", "--release", "2026.9"], get=_get, root=tmp_path)
    out = tmp_path / "docs/ha-release"
    assert sorted(p.name for p in out.iterdir() if p.is_dir()) == ["2026.8", "2026.9"]


def test_an_end_release_the_feed_does_not_carry_stops_the_run(tmp_path) -> None:
    """Filtering the span by the feed made a window it never fetched exit 0.

    `--release 2026.10` against a feed that stops at 2026.9 wrote 2026.8 and 2026.9, exited
    0, and titled the index for the releases it did fetch — which reads as a window nobody
    needs to fetch.
    """
    with pytest.raises(SystemExit):
        fhs.main(["--since", "2026.8", "--release", "2026.10"], get=_get, root=tmp_path)


def test_a_failed_post_fetch_leaves_the_previous_folder_intact(tmp_path) -> None:
    """Fetch every page before writing any, or a 403 halfway leaves a half-filled folder.

    A half-filled folder is what the gate would then certify as every source read. The fix
    had no test behind it and a reversion to the interleaved shape left the suite green,
    which is the finding this exists to answer.
    """
    fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)
    folder = tmp_path / "docs/ha-release/2026.9"
    before = sorted(p.name for p in folder.iterdir())

    def failing(url: str) -> str:
        # A post PAGE, not the feed: failing on the feed kills the run before it reaches
        # the folder at all, which is how the first version of this test passed against the
        # very shape it was written to forbid.
        if url.startswith("https://developers.home-assistant.io/blog/2"):
            raise OSError("403")
        return _get(url)

    with pytest.raises(OSError, match="403"):
        fhs.main(["--release", "2026.9"], get=failing, root=tmp_path)
    assert sorted(p.name for p in folder.iterdir()) == before
    assert (folder / "release-notes.md").read_text(encoding="utf-8")


def test_an_empty_window_says_so_on_stderr(tmp_path, capsys) -> None:
    """The one case the run cannot quietly pass over, and it had no test either."""
    feed = DEV_FEED.replace("2026", "2020")
    notes = RELEASE_FEED.replace(
        '<content type="html">&lt;p&gt;Notes body&lt;/p&gt;</content>',
        '<content type="html">&lt;p&gt;No links here&lt;/p&gt;</content>',
    )

    def get(url: str) -> str:
        if url == fhs.DEV_FEED:
            return feed
        if url == fhs.RELEASE_FEED:
            return notes
        return PAGE

    fhs.main(["--release", "2026.9"], get=get, root=tmp_path)
    assert "no developer-blog post is dated" in capsys.readouterr().err


def test_a_post_the_feed_has_aged_out_is_recovered_from_the_notes(tmp_path) -> None:
    """The feed is half the net; the release notes link the posts it has dropped.

    Measured on the first real run: 2026.6's notes name nine posts for that window and the
    feed still carried one, and the run said nothing, because it only warns at zero.
    """
    notes = RELEASE_FEED.replace(
        "&lt;p&gt;Notes body&lt;/p&gt;",
        "&lt;p&gt;Notes body &lt;a "
        'href="https://developers.home-assistant.io/blog/2026/08/07/aged-out"&gt;'
        "Aged out of the feed&lt;/a&gt;&lt;/p&gt;",
    )

    def get(url: str) -> str:
        return notes if url == fhs.RELEASE_FEED else _get(url)

    fhs.main(["--release", "2026.9"], get=get, root=tmp_path)
    recovered = tmp_path / "docs/ha-release/2026.9/blog-2026-08-07-aged-out.md"
    assert recovered.is_file()
    assert "Aged out of the feed" in recovered.read_text(encoding="utf-8")


def test_every_file_carries_its_source_and_the_terms_it_came_under(tmp_path) -> None:
    """CC BY-NC-SA 4.0 section 3(a) asks for the notice, the link and the modification.

    Section 2(a)(4) is why a format change leaves these verbatim copies rather than
    adaptations, so ShareAlike never bites and this repository's own licence is unaffected.
    """
    fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)
    notes = (tmp_path / "docs/ha-release/2026.9/release-notes.md").read_text(
        encoding="utf-8"
    )
    assert "creativecommons.org/licenses/by-nc-sa/4.0/" in notes
    assert "converted from HTML to plain text" in notes
    post = (tmp_path / "docs/ha-release/2026.9/blog-2026-09-02-modbus.md").read_text(
        encoding="utf-8"
    )
    assert "publishes no licence" in post
    assert "Fetched from https://developers.home-assistant.io/" in post


def test_the_index_records_a_hash_that_moves_with_the_file(tmp_path) -> None:
    """A source emptied outside the gate keeps its name and its row; the hash does not."""
    fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)
    out = tmp_path / "docs/ha-release"
    notes = out / "2026.9/release-notes.md"
    recorded = {row[0]: row[3] for row in fhs.sources_on_disk(out)}
    here = recorded["docs/ha-release/2026.9/release-notes.md"]
    assert f"`{here}`" in (out / "index.md").read_text(encoding="utf-8")
    # It has to be this file's hash, not merely a stable string: a constant in that column
    # is recorded, written to the index, and compared against itself for ever.
    assert here == fhs.digest(notes)
    notes.write_text("", encoding="utf-8")
    assert fhs.digest(notes) != here


def test_a_later_fetch_refuses_to_re_sign_a_release_it_did_not_refetch(
    tmp_path,
) -> None:
    """The hash column protected nothing while every run rewrote every row.

    Emptying a 2026.8 source failed the committed-artefact test; one fetch of 2026.9 wrote a
    fresh index over it and the suite went green again, so the guard erased its own evidence.
    """
    fhs.main(["--since", "2026.8", "--release", "2026.9"], get=_get, root=tmp_path)
    tampered = tmp_path / "docs/ha-release/2026.8/release-notes.md"
    tampered.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit, match="would not refetch 2026.8"):
        fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)
    # Nothing was written before the refusal: the tampered tree is left exactly as found,
    # rather than with 2026.9 rebuilt and no index, which is the half-written state the
    # fetch-before-write rule exists to prevent.
    assert not tampered.read_text(encoding="utf-8")
    assert (tmp_path / "docs/ha-release/index.md").is_file()

    # Refetching that release deliberately is the way through, and it has to stay the way
    # through when upstream has genuinely moved — a stub that returns the same bytes every
    # time cannot tell the exemption from its absence, and left it unprotected.
    moved = RELEASE_FEED.replace("Older notes", "Older notes, revised upstream")

    def changed(url: str) -> str:
        return moved if url == fhs.RELEASE_FEED else _get(url)

    assert fhs.main(["--release", "2026.8"], get=changed, root=tmp_path) == 0
    assert "revised upstream" in tampered.read_text(encoding="utf-8")


def test_a_missing_index_beside_fetched_releases_stops_the_run(tmp_path) -> None:
    """Deleting the index made the next run re-sign whatever had changed under it.

    The check pays for its own input, so an absent index is a refusal once releases exist —
    and still an empty comparison before the first fetch, when there is nothing to compare.
    """
    fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)
    (tmp_path / "docs/ha-release/2026.9/release-notes.md").write_text(
        "", encoding="utf-8"
    )
    (tmp_path / "docs/ha-release/index.md").unlink()
    with pytest.raises(
        SystemExit, match="is missing while fetched releases are present"
    ):
        fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)


def test_a_post_the_notes_link_from_another_window_is_not_filed_here(tmp_path) -> None:
    """The notes link posts from before their own window, and one was filed twice.

    2026.9's notes link the 2026-07-05 modbus post; the first version wrote a byte-identical
    copy of 2026.8's source into 2026.9 and counted it as a recovery.
    """
    notes = RELEASE_FEED.replace(
        "&lt;p&gt;Notes body&lt;/p&gt;",
        "&lt;p&gt;Notes body &lt;a "
        'href="https://developers.home-assistant.io/blog/2026/07/05/much-earlier"&gt;'
        "A post from a window ago&lt;/a&gt;&lt;/p&gt;",
    )

    def get(url: str) -> str:
        return notes if url == fhs.RELEASE_FEED else _get(url)

    fhs.main(["--release", "2026.9"], get=get, root=tmp_path)
    names = sorted(p.name for p in (tmp_path / "docs/ha-release/2026.9").iterdir())
    assert "blog-2026-07-05-much-earlier.md" not in names


def test_a_dropped_recovery_is_reported_rather_than_silent(tmp_path, capsys) -> None:
    """A post the notes name and the window rejects is worth a line, not a silence.

    It is either a post belonging to another release or a window whose start is the fallback
    span rather than a real previous release, and the second is a gap in the net.
    """
    notes = RELEASE_FEED.replace(
        "&lt;p&gt;Notes body&lt;/p&gt;",
        "&lt;p&gt;Notes body &lt;a "
        'href="https://developers.home-assistant.io/blog/2026/07/05/much-earlier"&gt;'
        "A post from a window ago&lt;/a&gt;&lt;/p&gt;",
    )

    def get(url: str) -> str:
        return notes if url == fhs.RELEASE_FEED else _get(url)

    fhs.main(["--release", "2026.9"], get=get, root=tmp_path)
    assert "not filed here" in capsys.readouterr().err


def test_a_recovered_post_needs_a_real_date_and_a_real_title() -> None:
    """The date built the filename and the sort key, and the link text became the heading."""
    assert (
        fhs.post_from_url("https://x/blog/2026/13/05/slug", "A full post title") is None
    )
    assert (
        fhs.post_from_url("https://x/blog/2026/07/32/slug", "A full post title") is None
    )
    assert fhs.post_from_url("https://x/blog/2026/7/5/slug", "A full post title") == {
        "title": "A full post title",
        "url": "https://x/blog/2026/7/5/slug",
        "date": "2026-07-05",
    }
    # A release note that links a post as "here" must not file it under `# here`.
    assert fhs.post_from_url("https://x/blog/2026/7/5/mqtt-changes", "here") == {
        "title": "mqtt changes",
        "url": "https://x/blog/2026/7/5/mqtt-changes",
        "date": "2026-07-05",
    }


def test_a_stray_directory_is_skipped_rather_than_fatal(tmp_path) -> None:
    """The gate skips a folder whose name is not a release; this used to sort by it and raise."""
    fhs.main(["--release", "2026.9"], get=_get, root=tmp_path)
    (tmp_path / "docs/ha-release/scratch").mkdir()
    (tmp_path / "docs/ha-release/scratch/notes.md").write_text("mine", encoding="utf-8")
    rows = fhs.sources_on_disk(tmp_path / "docs/ha-release")
    assert all("/scratch/" not in row[0] for row in rows)


@pytest.mark.parametrize(
    "missing",
    [
        '<link href="https://www.home-assistant.io/blog/2026/09/02/release-20269/"/>',
        "<updated>2026-09-02T00:00:00+00:00</updated>",
    ],
    ids=["no link", "no date"],
)
def test_nothing_is_written_when_a_release_entry_is_unusable(tmp_path, missing) -> None:
    """Both halves of the check, because only one of them had a test.

    The no-link half is also caught downstream by `window()`, so weakening the date check
    left the suite green — which is the defect class this whole row exists to answer.
    """
    broken = RELEASE_FEED.replace(missing, "")

    def get(url: str) -> str:
        return broken if url == fhs.RELEASE_FEED else _get(url)

    with pytest.raises(SystemExit):
        fhs.main(["--release", "2026.9"], get=get, root=tmp_path)
    assert not (tmp_path / "docs/ha-release").exists()


# ------------------------------------------------------- the committed artefact


def test_the_committed_sources_cover_the_release_the_skill_claims() -> None:
    """The gate fails open with nothing fetched, so this is what makes an absence visible.

    It is also the check that keeps a pass honest: fetching writes the folder, writing the
    rows moves the release row, and only when both have happened is the suite green.
    """
    out = REPO / "docs/ha-release"
    year, minor = chr_.captured_minor(
        (REPO / chr_.DEFAULT_FILE).read_text(encoding="utf-8")
    )
    folder = out / f"{year}.{minor}"
    assert folder.is_dir(), f"run scripts/fetch_ha_sources.py --release {year}.{minor}"
    assert (folder / "release-notes.md").is_file()


def test_every_committed_source_still_hashes_to_what_the_index_records() -> None:
    """The gate refuses to patch a source; nothing stops one being emptied outside it.

    Proved on review: `old_string` the whole body and `new_string` empty left five sources
    present, listed and zero bytes, with the suite green. The gate now refuses that patch,
    and this is what catches the same thing done by any other means.
    """
    out = REPO / "docs/ha-release"
    recorded = {}
    for line in (out / "index.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| `docs/ha-release/"):
            cells = [cell.strip(" `") for cell in line.strip("|").split("|")]
            recorded[cells[0]] = cells[1]
    assert recorded, "the index records no hashes"
    for rel, sha in recorded.items():
        assert fhs.digest(REPO / rel) == sha, f"{rel} no longer matches the index"


def test_the_committed_index_and_the_committed_folders_agree() -> None:
    """The gate reads the folders and a person reads the index; a drift misleads the person.

    Deriving the demand from the index let one patch to it disarm the gate. The demand now
    comes from the directory, which leaves the index able to drift instead — so the drift
    is what this checks, in both directions.
    """
    out = REPO / "docs/ha-release"
    text = (out / "index.md").read_text(encoding="utf-8")
    named = {
        line.split("`")[1]
        for line in text.splitlines()
        if line.startswith("| `docs/ha-release/")
    }
    # Release folders only, the way both the writer and the gate read this directory. Taking
    # every directory made a stray one fail CI for ever, since the writer will never list it:
    # the crash the fix removed would have come back as a permanent red.
    on_disk = {
        f"docs/ha-release/{folder.name}/{path.name}"
        for folder in out.iterdir()
        if folder.is_dir() and fhs._is_release(folder.name)
        for path in folder.iterdir()
        if path.is_file()
    }
    assert named == on_disk
