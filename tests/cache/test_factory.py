# tests/cache/test_factory.py
from datetime import UTC, datetime

from app.cache.factory import build_cache
from app.cache.memory import MemoryCache
from app.cache.redis import RedisCache
from app.clock import FixedClock, SystemClock
from app.config import Settings


def test_builds_memory_by_default():
    cache = build_cache(Settings(env={}), clock=SystemClock())
    assert isinstance(cache, MemoryCache)


def test_builds_redis_when_redis_url_set():
    settings = Settings(env={"REDIS_URL": "redis://localhost:6379"})
    cache = build_cache(settings, clock=SystemClock())
    assert isinstance(cache, RedisCache)


def test_memory_cache_uses_injected_clock_for_expiry():
    clock = FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC))
    cache = build_cache(Settings(env={}), clock=clock)
    cache.set("feeds", "k", {"v": 1}, ttl_seconds=60)
    assert cache.get("feeds", "k") == {"v": 1}
    clock.advance(seconds=61)
    assert cache.get("feeds", "k") is None  # expired on the shared clock
