# tests/domains/test_contract.py
import random
from datetime import UTC, datetime, timedelta

import app.domains  # noqa: F401  (triggers registration)
from app.domains.base import FeedItem, registry

EXPECTED = {"financial", "news", "weather", "sports", "ecommerce", "iot", "social"}


def _dt(s: int) -> datetime:
    return datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC) + timedelta(seconds=s)


def test_all_expected_domains_registered():
    assert EXPECTED <= set(registry())


import pytest


@pytest.mark.parametrize("key", sorted(EXPECTED))
def test_domain_generates_items_in_window(key):
    gen = registry()[key]
    items = gen.generate_items(
        params=None, categories=None,
        start=_dt(0), end=_dt(600),
        interval_seconds=30, variance_pct=20, max_items=200,
        rng=random.Random(7),
    )
    assert len(items) > 0
    for it in items:
        assert isinstance(it, FeedItem)
        assert _dt(0) < it.published <= _dt(600)
        assert it.guid and it.title
        assert 1 <= len(it.categories) <= len(gen.default_categories)


@pytest.mark.parametrize("key", sorted(EXPECTED))
def test_domain_describe_shape(key):
    d = registry()[key].describe()
    assert d["domain"] == key
    assert isinstance(d["default_categories"], list) and d["default_categories"]
    assert isinstance(d["params"], dict)
