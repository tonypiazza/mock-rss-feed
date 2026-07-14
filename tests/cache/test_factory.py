# tests/cache/test_factory.py
from app.cache.factory import build_cache
from app.cache.memory import MemoryCache
from app.cache.redis import RedisCache
from app.config import Settings


def test_builds_memory_by_default():
    cache = build_cache(Settings(env={}))
    assert isinstance(cache, MemoryCache)


def test_builds_redis_when_redis_url_set():
    settings = Settings(env={"REDIS_URL": "redis://localhost:6379"})
    cache = build_cache(settings)
    assert isinstance(cache, RedisCache)
