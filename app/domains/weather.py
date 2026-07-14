# app/domains/weather.py
from __future__ import annotations

from app.domains.base import DomainGenerator, FeedItem, register

_CONDITIONS = ["Sunny", "Cloudy", "Rain", "Thunderstorms", "Snow", "Fog", "Windy"]


@register
class WeatherDomain(DomainGenerator):
    domain_key = "weather"
    default_params = {"cities": ["London", "Tokyo", "New York", "Sydney"]}
    param_schema = {"cities": list}
    default_categories = ["forecast", "alert", "current", "marine", "aviation"]

    def make_item(self, ts, params, categories, rng):
        city = rng.choice(params["cities"])
        condition = rng.choice(_CONDITIONS)
        temp = rng.randint(-10, 38)
        return FeedItem(
            guid=f"{self.domain_key}-{city}-{ts.isoformat()}",
            title=f"{city}: {condition}, {temp}°C",
            summary=f"Current conditions in {city}: {condition}, {temp}°C.",
            published=ts,
            categories=categories,
            link_suffix=city.lower().replace(" ", "-"),
        )
