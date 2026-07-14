# app/keys.py
from __future__ import annotations

import secrets
from datetime import timedelta

from app.cache.base import CacheBackend
from app.clock import Clock

_NS = "keys"


class KeyStore:
    def __init__(self, *, cache: CacheBackend, clock: Clock, ttl_seconds: int) -> None:
        self._cache = cache
        self._clock = clock
        self._ttl = ttl_seconds

    def mint(self, *, email: str, label: str | None) -> dict:
        api_key = secrets.token_urlsafe(24)
        expires_at = (self._clock.now() + timedelta(seconds=self._ttl)).isoformat()
        record = {"api_key": api_key, "email": email, "label": label, "expires_at": expires_at}
        self._cache.set(_NS, api_key, record, ttl_seconds=self._ttl)
        return record

    def is_valid(self, api_key: str | None) -> bool:
        if not api_key:
            return False
        return self._cache.get(_NS, api_key) is not None
