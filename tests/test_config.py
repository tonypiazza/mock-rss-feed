# tests/test_config.py
from app.config import Settings


def test_defaults_when_env_empty():
    s = Settings(env={})
    assert s.port == 80
    assert s.feed_ttl_seconds == 3600
    assert s.cache_backend == "memory"
    assert s.redis_url is None
    assert s.max_feeds == 100
    assert s.max_keys == 100
    assert s.default_interval_seconds == 30
    assert s.default_variance_pct == 20
    assert s.max_items_per_response == 200
    assert s.enabled_domains is None
    assert s.public_base_url is None


def test_reads_and_coerces_env():
    s = Settings(env={
        "PORT": "8000",
        "FEED_TTL_SECONDS": "600",
        "CACHE_BACKEND": "redis",
        "REDIS_URL": "rediss://host:6379",
        "DEFAULT_VARIANCE_PCT": "10",
        "ENABLED_DOMAINS": "financial, news",
        "PUBLIC_BASE_URL": "https://example.com",
    })
    assert s.port == 8000
    assert s.feed_ttl_seconds == 600
    assert s.cache_backend == "redis"
    assert s.redis_url == "rediss://host:6379"
    assert s.default_variance_pct == 10
    assert s.enabled_domains == ["financial", "news"]
    assert s.public_base_url == "https://example.com"


def test_redis_backend_requires_url():
    import pytest
    with pytest.raises(ValueError, match="REDIS_URL"):
        Settings(env={"CACHE_BACKEND": "redis"})
