# app/config.py
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    port: int
    feed_ttl_seconds: int
    cache_backend: str
    redis_url: str | None
    max_feeds: int
    max_keys: int
    default_interval_seconds: int
    default_variance_pct: float
    max_items_per_response: int
    enabled_domains: list[str] | None
    public_base_url: str | None

    def __init__(self, env: dict[str, str] | None = None) -> None:
        e = os.environ if env is None else env

        def _int(name: str, default: int) -> int:
            return int(e.get(name, default))

        enabled = e.get("ENABLED_DOMAINS")
        object.__setattr__(self, "port", _int("PORT", 80))
        object.__setattr__(self, "feed_ttl_seconds", _int("FEED_TTL_SECONDS", 3600))
        object.__setattr__(self, "cache_backend", e.get("CACHE_BACKEND", "memory"))
        object.__setattr__(self, "redis_url", e.get("REDIS_URL") or None)
        object.__setattr__(self, "max_feeds", _int("MAX_FEEDS", 100))
        object.__setattr__(self, "max_keys", _int("MAX_KEYS", 100))
        object.__setattr__(self, "default_interval_seconds", _int("DEFAULT_INTERVAL_SECONDS", 30))
        object.__setattr__(self, "default_variance_pct", float(e.get("DEFAULT_VARIANCE_PCT", 20)))
        object.__setattr__(self, "max_items_per_response", _int("MAX_ITEMS_PER_RESPONSE", 200))
        object.__setattr__(
            self,
            "enabled_domains",
            [d.strip() for d in enabled.split(",") if d.strip()] if enabled else None,
        )
        object.__setattr__(self, "public_base_url", e.get("PUBLIC_BASE_URL") or None)

        if self.cache_backend == "redis" and not self.redis_url:
            raise ValueError("REDIS_URL is required when CACHE_BACKEND=redis")
