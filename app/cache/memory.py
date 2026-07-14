# app/cache/memory.py
from __future__ import annotations

import copy
import time
from typing import Callable

from app.cache.base import CacheBackend

_DEFAULT_SIZE = 100


class MemoryCache(CacheBackend):
    def __init__(
        self,
        sizes: dict[str, int] | None = None,
        *,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self._sizes = sizes or {}
        self._time = time_fn
        # namespace -> {key: (value, expires_at)}
        self._store: dict[str, dict[str, tuple[dict, float]]] = {}

    def _ns(self, namespace: str) -> dict[str, tuple[dict, float]]:
        return self._store.setdefault(namespace, {})

    def _live(self, namespace: str, key: str) -> tuple[dict, float] | None:
        entry = self._ns(namespace).get(key)
        if entry is None:
            return None
        _, expires_at = entry
        if self._time() >= expires_at:
            self._ns(namespace).pop(key, None)
            return None
        return entry

    def get(self, namespace: str, key: str) -> dict | None:
        entry = self._live(namespace, key)
        return copy.deepcopy(entry[0]) if entry is not None else None

    def set(self, namespace: str, key: str, value: dict, ttl_seconds: int) -> None:
        ns = self._ns(namespace)
        ns[key] = (copy.deepcopy(value), self._time() + ttl_seconds)
        self._evict_if_needed(namespace)

    def set_keep_ttl(self, namespace: str, key: str, value: dict) -> None:
        entry = self._live(namespace, key)
        if entry is None:
            return  # key already gone; nothing to update
        _, expires_at = entry
        self._ns(namespace)[key] = (copy.deepcopy(value), expires_at)

    def delete(self, namespace: str, key: str) -> None:
        self._ns(namespace).pop(key, None)

    def list(self, namespace: str) -> list[dict]:
        now = self._time()
        ns = self._ns(namespace)
        for key in [k for k, (_, exp) in ns.items() if now >= exp]:
            ns.pop(key, None)
        return [copy.deepcopy(v) for v, _ in ns.values()]

    def _evict_if_needed(self, namespace: str) -> None:
        maxsize = self._sizes.get(namespace, _DEFAULT_SIZE)
        ns = self._ns(namespace)
        while len(ns) > maxsize:
            # evict the soonest-expiring entry
            oldest = min(ns, key=lambda k: ns[k][1])
            ns.pop(oldest, None)
