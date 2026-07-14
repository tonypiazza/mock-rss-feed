# tests/test_feed_render.py
from datetime import UTC, datetime
from xml.etree import ElementTree as ET

from app.domains.base import FeedItem
from app.feed_render import render_feed


def _items():
    return [
        FeedItem(
            guid="financial-AAPL-1",
            title="AAPL up 1%",
            summary="Apple rises.",
            published=datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC),
            categories=["markets", "equities"],
            link_suffix="aapl",
        )
    ]


def test_rss_is_well_formed_and_has_absolute_links():
    xml = render_feed(
        feed_id="abc", title="My Feed", description="desc",
        items=_items(), fmt="rss", base_url="https://example.com",
    )
    root = ET.fromstring(xml)  # raises if malformed
    assert root.tag == "rss"
    assert b"https://example.com/feeds/abc" in xml
    assert b"markets" in xml and b"equities" in xml


def test_atom_is_well_formed():
    xml = render_feed(
        feed_id="abc", title="My Feed", description="desc",
        items=_items(), fmt="atom", base_url="https://example.com",
    )
    root = ET.fromstring(xml)
    assert root.tag.endswith("feed")  # Atom namespace-qualified
    assert b"https://example.com/feeds/abc" in xml


def test_items_carry_multiple_categories():
    xml = render_feed(
        feed_id="abc", title="t", description="d",
        items=_items(), fmt="rss", base_url="https://example.com",
    )
    assert xml.count(b"<category") >= 2
