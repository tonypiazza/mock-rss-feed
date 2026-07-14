# app/domains/iot.py
from __future__ import annotations

from app.domains.base import DomainGenerator, FeedItem, register

_METRICS = {
    "temperature": ("°C", -20, 60),
    "humidity": ("%", 0, 100),
    "pressure": ("hPa", 950, 1050),
    "co2": ("ppm", 350, 2000),
}


@register
class IotDomain(DomainGenerator):
    domain_key = "iot"
    default_params = {"sensors": ["sensor-01", "sensor-02", "sensor-03"]}
    param_schema = {"sensors": list}
    default_categories = ["telemetry", "alert", "status", "diagnostic"]

    def make_item(self, ts, params, categories, rng):
        sensor = rng.choice(params["sensors"])
        metric = rng.choice(list(_METRICS))
        unit, lo, hi = _METRICS[metric]
        value = round(rng.uniform(lo, hi), 2)
        return FeedItem(
            guid=f"{self.domain_key}-{sensor}-{ts.isoformat()}",
            title=f"{sensor} {metric}={value}{unit}",
            summary=f"Reading from {sensor}: {metric} {value}{unit}.",
            published=ts,
            categories=categories,
            link_suffix=sensor,
        )
