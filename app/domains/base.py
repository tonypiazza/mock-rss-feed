# app/domains/base.py
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FeedItem:
    guid: str
    title: str
    summary: str
    published: datetime
    categories: list[str] = field(default_factory=list)
    link_suffix: str | None = None  # optional per-item path suffix for the item URL


class DomainGenerator(ABC):
    domain_key: str
    default_params: dict
    param_schema: dict  # {param_name: expected_type}
    default_categories: list[str]

    def merge_params(self, params: dict | None) -> dict:
        merged = dict(self.default_params)
        if params:
            merged.update(params)
        return merged

    def validate_params(self, params: dict | None) -> None:
        if not params:
            return
        for key, value in params.items():
            if key not in self.param_schema:
                raise ValueError(f"unknown param '{key}' for domain '{self.domain_key}'")
            expected = self.param_schema[key]
            if not isinstance(value, expected):
                raise ValueError(f"param '{key}' must be {expected.__name__}")

    def _pick_categories(self, pool: list[str], rng: random.Random) -> list[str]:
        if not pool:
            return []
        n = rng.randint(1, len(pool))
        return rng.sample(pool, n)

    def generate_items(
        self,
        *,
        params: dict | None,
        categories: list[str] | None,
        start: datetime,
        end: datetime,
        interval_seconds: float,
        variance_pct: float,
        max_items: int,
        rng: random.Random,
    ) -> list[FeedItem]:
        from app.stream import jittered_timestamps

        merged = self.merge_params(params)
        pool = categories if categories else self.default_categories
        timestamps = jittered_timestamps(
            start=start, end=end, interval_seconds=interval_seconds,
            variance_pct=variance_pct, max_items=max_items, rng=rng,
        )
        items: list[FeedItem] = []
        for ts in timestamps:
            item_cats = self._pick_categories(pool, rng)
            items.append(self.make_item(ts, merged, item_cats, rng))
        return items

    @abstractmethod
    def make_item(
        self, ts: datetime, params: dict, categories: list[str], rng: random.Random
    ) -> FeedItem: ...

    def describe(self) -> dict:
        return {
            "domain": self.domain_key,
            "default_params": self.default_params,
            "params": {k: v.__name__ for k, v in self.param_schema.items()},
            "default_categories": self.default_categories,
        }


_REGISTRY: dict[str, DomainGenerator] = {}


def register(cls: type[DomainGenerator]) -> type[DomainGenerator]:
    _REGISTRY[cls.domain_key] = cls()
    return cls


def registry() -> dict[str, DomainGenerator]:
    return dict(_REGISTRY)


def get_domain(key: str) -> DomainGenerator | None:
    return _REGISTRY.get(key)
