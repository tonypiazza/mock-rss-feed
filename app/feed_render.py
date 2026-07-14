# app/feed_render.py
from __future__ import annotations

from app.domains.base import FeedItem
from feedgen.feed import FeedGenerator


def render_feed(
    *,
    feed_id: str,
    title: str,
    description: str,
    items: list[FeedItem],
    fmt: str,
    base_url: str,
) -> bytes:
    base = base_url.rstrip("/")
    feed_url = f"{base}/feeds/{feed_id}"

    fg = FeedGenerator()
    fg.id(feed_url)
    fg.title(title)
    fg.description(description or title)  # RSS requires a description
    fg.link(href=feed_url, rel="alternate")
    fg.link(href=feed_url, rel="self")
    fg.language("en")

    # feedgen emits items newest-first; add in chronological order.
    for it in items:
        fe = fg.add_entry()
        item_url = f"{feed_url}/{it.link_suffix}" if it.link_suffix else feed_url
        fe.id(f"{feed_url}#{it.guid}")
        fe.title(it.title)
        fe.description(it.summary)
        fe.link(href=item_url)
        fe.published(it.published)
        fe.updated(it.published)
        for cat in it.categories:
            fe.category(term=cat)

    if fmt == "atom":
        return fg.atom_str(pretty=True)
    return fg.rss_str(pretty=True)
