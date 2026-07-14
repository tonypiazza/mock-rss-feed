# tests/cache/test_contract.py
import time

import pytest

from app.cache.memory import MemoryCache


def make_memory():
    return MemoryCache(sizes={"feeds": 100, "keys": 100})


BACKENDS = [make_memory]


@pytest.fixture(params=BACKENDS)
def cache(request):
    return request.param()


def test_set_get_roundtrip(cache):
    cache.set("feeds", "a", {"x": 1}, ttl_seconds=60)
    assert cache.get("feeds", "a") == {"x": 1}


def test_get_missing_returns_none(cache):
    assert cache.get("feeds", "nope") is None


def test_namespaces_are_isolated(cache):
    cache.set("feeds", "a", {"n": "feed"}, ttl_seconds=60)
    cache.set("keys", "a", {"n": "key"}, ttl_seconds=60)
    assert cache.get("feeds", "a") == {"n": "feed"}
    assert cache.get("keys", "a") == {"n": "key"}


def test_delete(cache):
    cache.set("feeds", "a", {"x": 1}, ttl_seconds=60)
    cache.delete("feeds", "a")
    assert cache.get("feeds", "a") is None


def test_list_returns_all_live_values(cache):
    cache.set("feeds", "a", {"i": 1}, ttl_seconds=60)
    cache.set("feeds", "b", {"i": 2}, ttl_seconds=60)
    got = sorted(cache.list("feeds"), key=lambda d: d["i"])
    assert got == [{"i": 1}, {"i": 2}]


def test_ttl_expiry(cache):
    cache.set("feeds", "a", {"x": 1}, ttl_seconds=1)
    time.sleep(1.1)
    assert cache.get("feeds", "a") is None


def test_set_keep_ttl_preserves_expiry(cache):
    cache.set("feeds", "a", {"v": 1}, ttl_seconds=1)
    time.sleep(0.5)
    cache.set_keep_ttl("feeds", "a", {"v": 2})
    assert cache.get("feeds", "a") == {"v": 2}  # value updated
    time.sleep(0.7)
    assert cache.get("feeds", "a") is None  # original 1s expiry preserved, not reset
