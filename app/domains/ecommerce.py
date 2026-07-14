# app/domains/ecommerce.py
from __future__ import annotations

from app.domains.base import DomainGenerator, FeedItem, register

_PRODUCTS = ["Widget", "Gadget", "Gizmo", "Doohickey", "Contraption", "Sprocket"]
_STATUSES = ["placed", "shipped", "delivered", "returned", "cancelled"]


@register
class EcommerceDomain(DomainGenerator):
    domain_key = "ecommerce"
    default_params = {"currency": "USD"}
    param_schema = {"currency": str}
    default_categories = ["electronics", "home", "apparel", "toys", "grocery"]

    def make_item(self, ts, params, categories, rng):
        product = rng.choice(_PRODUCTS)
        status = rng.choice(_STATUSES)
        order_id = rng.randint(100000, 999999)
        amount = round(rng.uniform(5, 500), 2)
        return FeedItem(
            guid=f"{self.domain_key}-{order_id}-{ts.isoformat()}",
            title=f"Order #{order_id} {status}",
            summary=f"{product} — {amount} {params['currency']} — {status}.",
            published=ts,
            categories=categories,
            link_suffix=str(order_id),
        )
