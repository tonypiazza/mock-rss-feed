# app/cache/redis.py
from __future__ import annotations

import json

import redis

from app.cache.base import CacheBackend


class RedisCache(CacheBackend):
    def __init__(self, *, url: str | None = None, client: redis.Redis | None = None) -> None:
        if client is not None:
            self._r = client
        elif url is not None:
            self._r = redis.Redis.from_url(url, decode_responses=True)
        else:
            raise ValueError("RedisCache requires either url or client")

    def _k(self, namespace: str, key: str) -> str:
        return f"{namespace}:{key}"

    def get(self, namespace: str, key: str) -> dict | None:
        raw = self._r.get(self._k(namespace, key))
        return json.loads(raw) if raw is not None else None

    def set(self, namespace: str, key: str, value: dict, ttl_seconds: int) -> None:
        self._r.set(self._k(namespace, key), json.dumps(value), ex=ttl_seconds)

    def set_keep_ttl(self, namespace: str, key: str, value: dict) -> None:
        # KEEPTTL retains the existing expiry; XX ensures we only write if it exists.
        self._r.set(self._k(namespace, key), json.dumps(value), keepttl=True, xx=True)

    def delete(self, namespace: str, key: str) -> None:
        self._r.delete(self._k(namespace, key))

    def list(self, namespace: str) -> list[dict]:
        out: list[dict] = []
        for k in self._r.scan_iter(match=f"{namespace}:*"):
            raw = self._r.get(k)
            if raw is not None:
                out.append(json.loads(raw))
        return out
