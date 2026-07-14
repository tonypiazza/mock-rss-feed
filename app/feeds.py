# app/feeds.py
from __future__ import annotations

import random
import secrets
from datetime import datetime, timedelta

from app.cache.base import CacheBackend
from app.clock import Clock
from app.config import Settings
from app.domains.base import FeedItem, get_domain

_NS = "feeds"


class InvalidFeedRequest(Exception):
    pass


class FeedNotFound(Exception):
    pass


class FeedStore:
    def __init__(self, *, cache: CacheBackend, clock: Clock, settings: Settings) -> None:
        self._cache = cache
        self._clock = clock
        self._s = settings

    def create(
        self, *, domain: str, title: str | None, description: str | None,
        interval_seconds: int | None, variance_pct: float | None,
        categories: list[str] | None, params: dict | None,
    ) -> dict:
        gen = get_domain(domain)
        if gen is None or (self._s.enabled_domains and domain not in self._s.enabled_domains):
            raise InvalidFeedRequest(f"unknown or disabled domain '{domain}'")
        try:
            gen.validate_params(params)
        except ValueError as exc:
            raise InvalidFeedRequest(str(exc)) from exc

        feed_id = secrets.token_urlsafe(9)
        now = self._clock.now()
        expires_at = (now + timedelta(seconds=self._s.feed_ttl_seconds)).isoformat()
        record = {
            "feed_id": feed_id,
            "domain": domain,
            "title": title or f"{domain.title()} Feed",
            "description": description or f"Mock {domain} feed",
            "interval_seconds": interval_seconds or self._s.default_interval_seconds,
            "variance_pct": self._s.default_variance_pct if variance_pct is None else variance_pct,
            "categories": categories,
            "params": params,
            "created_at": now.isoformat(),
            "expires_at": expires_at,
            "last_served_at": None,
        }
        self._cache.set(_NS, feed_id, record, ttl_seconds=self._s.feed_ttl_seconds)
        return record

    def read(self, feed_id: str) -> tuple[list[FeedItem], str, str]:
        record = self._cache.get(_NS, feed_id)
        if record is None:
            raise FeedNotFound(feed_id)

        now = self._clock.now()
        if record["last_served_at"] is None:
            start = now - timedelta(seconds=self._s.feed_ttl_seconds)
        else:
            start = datetime.fromisoformat(record["last_served_at"])

        gen = get_domain(record["domain"])
        # Deterministic within a (feed, window) but advances as the watermark moves.
        seed = f"{feed_id}:{start.isoformat()}"
        rng = random.Random(seed)
        items = gen.generate_items(
            params=record["params"],
            categories=record["categories"],
            start=start,
            end=now,
            interval_seconds=record["interval_seconds"],
            variance_pct=record["variance_pct"],
            max_items=self._s.max_items_per_response,
            rng=rng,
        )

        record["last_served_at"] = now.isoformat()
        self._cache.set_keep_ttl(_NS, feed_id, record)
        return items, record["title"], record["description"]

    def delete(self, feed_id: str) -> None:
        if self._cache.get(_NS, feed_id) is None:
            raise FeedNotFound(feed_id)
        self._cache.delete(_NS, feed_id)
