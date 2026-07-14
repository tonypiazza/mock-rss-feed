# app/domains/financial.py
from __future__ import annotations

import random
from datetime import datetime

from app.domains.base import DomainGenerator, FeedItem, register


@register
class FinancialDomain(DomainGenerator):
    domain_key = "financial"
    default_params = {"tickers": ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA"]}
    param_schema = {"tickers": list}
    default_categories = ["markets", "equities", "earnings", "forex", "commodities"]

    def make_item(self, ts, params, categories, rng):
        ticker = rng.choice(params["tickers"])
        price = round(rng.uniform(20, 500), 2)
        move = round(rng.uniform(-5, 5), 2)
        arrow = "▲" if move >= 0 else "▼"
        return FeedItem(
            guid=f"{self.domain_key}-{ticker}-{ts.isoformat()}",
            title=f"{ticker} {arrow} {abs(move)}% to ${price}",
            summary=f"{ticker} trades at ${price}, {move:+}% on the session.",
            published=ts,
            categories=categories,
            link_suffix=ticker.lower(),
        )
