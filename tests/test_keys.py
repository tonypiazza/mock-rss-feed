# tests/test_keys.py
from datetime import UTC, datetime

from app.cache.memory import MemoryCache
from app.clock import FixedClock
from app.keys import KeyStore


def _store():
    return KeyStore(
        cache=MemoryCache(sizes={"keys": 100}),
        clock=FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC)),
        ttl_seconds=3600,
    )


def test_mint_returns_key_and_expiry():
    store = _store()
    record = store.mint(email="user@example.com", label="acme")
    assert record["api_key"]
    assert record["email"] == "user@example.com"
    assert record["expires_at"] == "2026-07-14T13:00:00+00:00"


def test_minted_key_is_valid_and_unknown_key_is_not():
    store = _store()
    record = store.mint(email="user@example.com", label=None)
    assert store.is_valid(record["api_key"]) is True
    assert store.is_valid("bogus") is False
