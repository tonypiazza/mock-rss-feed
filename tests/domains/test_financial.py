# tests/domains/test_financial.py
import random
from datetime import UTC, datetime

from app.domains.financial import FinancialDomain


def test_financial_item_uses_a_ticker_and_price():
    d = FinancialDomain()
    ts = datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC)
    item = d.make_item(ts, {"tickers": ["AAPL"]}, ["markets"], random.Random(1))
    assert "AAPL" in item.title
    assert item.published == ts
    assert item.categories == ["markets"]
    assert item.guid
