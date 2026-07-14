# app/domains/sports.py
from __future__ import annotations

from app.domains.base import DomainGenerator, FeedItem, register

_TEAMS = ["Lions", "Sharks", "Eagles", "Wolves", "Titans", "Rovers"]


@register
class SportsDomain(DomainGenerator):
    domain_key = "sports"
    default_params = {"leagues": ["premier", "national", "regional"]}
    param_schema = {"leagues": list}
    default_categories = ["football", "basketball", "tennis", "cricket", "hockey"]

    def make_item(self, ts, params, categories, rng):
        home, away = rng.sample(_TEAMS, 2)
        hs, as_ = rng.randint(0, 5), rng.randint(0, 5)
        league = rng.choice(params["leagues"])
        return FeedItem(
            guid=f"{self.domain_key}-{ts.isoformat()}",
            title=f"{home} {hs} - {as_} {away}",
            summary=f"[{league}] Final: {home} {hs}, {away} {as_}.",
            published=ts,
            categories=categories,
        )
