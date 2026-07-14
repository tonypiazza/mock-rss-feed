# tests/test_feeds.py
from datetime import UTC, datetime

import pytest

import app.domains  # noqa: F401
from app.cache.memory import MemoryCache
from app.clock import FixedClock
from app.config import Settings
from app.feeds import FeedNotFound, FeedStore, InvalidFeedRequest


def _store(clock):
    return FeedStore(
        cache=MemoryCache(sizes={"feeds": 100}),
        clock=clock,
        settings=Settings(env={"FEED_TTL_SECONDS": "3600", "DEFAULT_INTERVAL_SECONDS": "30"}),
    )


def test_create_unknown_domain_raises():
    store = _store(FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC)))
    with pytest.raises(InvalidFeedRequest):
        store.create(domain="nope", title=None, description=None,
                     interval_seconds=None, variance_pct=None, categories=None, params=None)


def test_create_rejects_unknown_param():
    store = _store(FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC)))
    with pytest.raises(InvalidFeedRequest):
        store.create(domain="financial", title=None, description=None,
                     interval_seconds=None, variance_pct=None, categories=None,
                     params={"bogus": 1})


def test_first_read_seeds_full_ttl_window():
    clock = FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC))
    store = _store(clock)
    rec = store.create(domain="financial", title="F", description=None,
                       interval_seconds=30, variance_pct=0, categories=None, params=None)
    items, title, desc = store.read(rec["feed_id"])
    # 3600s / 30s ≈ 120 items across the seeded window
    assert 100 <= len(items) <= 140
    assert title == "F"
    # earliest item is within the seed window (not before now - ttl)
    assert items[0].published >= datetime(2026, 7, 14, 11, 0, 0, tzinfo=UTC)


def test_second_read_only_returns_new_items_and_advances_watermark():
    clock = FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC))
    store = _store(clock)
    rec = store.create(domain="news", title="N", description=None,
                       interval_seconds=30, variance_pct=0, categories=None, params=None)
    store.read(rec["feed_id"])          # first read seeds + sets watermark to now
    clock.advance(seconds=90)            # 3 intervals later
    items, _, _ = store.read(rec["feed_id"])
    assert 2 <= len(items) <= 4          # ~3 new items in 90s at 30s interval
    assert all(it.published > datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC) for it in items)


def test_read_missing_feed_raises():
    store = _store(FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC)))
    with pytest.raises(FeedNotFound):
        store.read("does-not-exist")


def test_delete_removes_feed():
    store = _store(FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC)))
    rec = store.create(domain="iot", title="I", description=None,
                       interval_seconds=30, variance_pct=0, categories=None, params=None)
    store.delete(rec["feed_id"])
    with pytest.raises(FeedNotFound):
        store.read(rec["feed_id"])
