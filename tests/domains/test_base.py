# tests/domains/test_base.py
import random
from datetime import UTC, datetime, timedelta

from app.domains.base import DomainGenerator, FeedItem, get_domain, registry, register


def _dt(s: int) -> datetime:
    return datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC) + timedelta(seconds=s)


@register
class _FakeDomain(DomainGenerator):
    domain_key = "fake"
    default_params = {"widgets": ["a", "b"]}
    param_schema = {"widgets": list}
    default_categories = ["one", "two", "three"]

    def make_item(self, ts, params, categories, rng):
        return FeedItem(
            guid=f"fake-{ts.isoformat()}",
            title=f"Widget {params['widgets'][0]}",
            summary="hello",
            published=ts,
            categories=categories,
        )


def test_registry_registers_and_looks_up():
    assert "fake" in registry()
    assert get_domain("fake") is not None


def test_generate_items_produces_items_in_window():
    d = get_domain("fake")
    items = d.generate_items(
        params={"widgets": ["a"]}, categories=None,
        start=_dt(0), end=_dt(300),
        interval_seconds=30, variance_pct=20, max_items=200,
        rng=random.Random(1),
    )
    assert len(items) > 0
    assert all(_dt(0) < it.published <= _dt(300) for it in items)
    assert all(1 <= len(it.categories) <= 3 for it in items)
    assert all(set(it.categories) <= {"one", "two", "three"} for it in items)


def test_category_override_replaces_pool():
    d = get_domain("fake")
    items = d.generate_items(
        params={"widgets": ["a"]}, categories=["crypto", "defi"],
        start=_dt(0), end=_dt(300),
        interval_seconds=30, variance_pct=0, max_items=200,
        rng=random.Random(2),
    )
    assert all(set(it.categories) <= {"crypto", "defi"} for it in items)


def test_merged_params_fill_defaults():
    d = get_domain("fake")
    merged = d.merge_params({})
    assert merged == {"widgets": ["a", "b"]}
    merged2 = d.merge_params({"widgets": ["z"]})
    assert merged2 == {"widgets": ["z"]}
