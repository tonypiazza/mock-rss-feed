# app/domains/news.py
from __future__ import annotations

from app.domains.base import DomainGenerator, FeedItem, register

_HEADLINES = [
    "Officials announce new policy", "Markets react to global news",
    "Study reveals surprising trend", "Local community rallies together",
    "Tech firm unveils latest product", "Weather disrupts travel plans",
]


@register
class NewsDomain(DomainGenerator):
    domain_key = "news"
    default_params = {"sections": ["politics", "tech", "world", "business"]}
    param_schema = {"sections": list}
    default_categories = ["politics", "tech", "sports", "world", "business", "science"]

    def make_item(self, ts, params, categories, rng):
        headline = rng.choice(_HEADLINES)
        section = rng.choice(params["sections"])
        return FeedItem(
            guid=f"{self.domain_key}-{ts.isoformat()}",
            title=headline,
            summary=f"[{section}] {headline}. Full story developing.",
            published=ts,
            categories=categories,
        )
