# tests/test_enabled_domains.py
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.clock import FixedClock
from app.config import Settings
from app.main import create_app


def _client():
    settings = Settings(env={"ENABLED_DOMAINS": "financial,news"})
    clock = FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC))
    return TestClient(create_app(settings=settings, clock=clock))


def test_domains_endpoint_filtered():
    client = _client()
    keys = {d["domain"] for d in client.get("/domains").json()["domains"]}
    assert keys == {"financial", "news"}


def test_create_disabled_domain_rejected():
    client = _client()
    key = client.post("/keys", json={"email": "u@example.com"}).json()["api_key"]
    resp = client.post("/feeds", json={"domain": "weather"}, headers={"X-API-Key": key})
    assert resp.status_code == 422
