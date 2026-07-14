# app/cache/factory.py
from __future__ import annotations

from app.cache.base import CacheBackend
from app.cache.memory import MemoryCache
from app.cache.redis import RedisCache
from app.clock import Clock
from app.config import Settings


def build_cache(settings: Settings, *, clock: Clock) -> CacheBackend:
    if settings.use_redis:
        return RedisCache(url=settings.redis_url)
    return MemoryCache(
        sizes={"feeds": settings.max_feeds, "keys": settings.max_keys},
        time_fn=lambda: clock.now().timestamp(),
    )
