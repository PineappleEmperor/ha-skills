# Media sources can now be searched

Fetched from https://developers.home-assistant.io/blog/2026/07/03/media-source-search
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified only in format: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. The wording is the author's, unaltered.

Media sources can now be searched

July 3, 2026 · One min read

Josef Zweck

Media sources can now implement search. By adding an async_search_media method to your MediaSource, users can search through your media directly from the media browser.

from homeassistant.components.media_player import SearchMedia, SearchMediaQuery

async def async_search_media(

self, item: MediaSourceItem, query: SearchMediaQuery

) -> SearchMedia:

"""Search media."""

results = [...]  # list of BrowseMediaSource items

return SearchMedia(result=results)

To tell the media browser which items can be searched, set the can_search flag to True on the BrowseMediaSource items you return while browsing (typically directories). Other integrations can trigger a search through the new media_source.async_search_media helper.

For more info, see the updated documentation.
