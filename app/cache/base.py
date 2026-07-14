# app/cache/base.py
from __future__ import annotations

from abc import ABC, abstractmethod


class CacheBackend(ABC):
    """TTL cache abstraction. Values are JSON-serializable dicts."""

    @abstractmethod
    def get(self, namespace: str, key: str) -> dict | None: ...

    @abstractmethod
    def set(self, namespace: str, key: str, value: dict, ttl_seconds: int) -> None: ...

    @abstractmethod
    def set_keep_ttl(self, namespace: str, key: str, value: dict) -> None:
        """Overwrite the value, preserving the existing expiry."""

    @abstractmethod
    def delete(self, namespace: str, key: str) -> None: ...

    @abstractmethod
    def list(self, namespace: str) -> list[dict]: ...
