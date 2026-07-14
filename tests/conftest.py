# tests/conftest.py
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.clock import FixedClock
from app.config import Settings
from app.main import create_app


@pytest.fixture
def clock():
    return FixedClock(datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC))


@pytest.fixture
def client(clock):
    settings = Settings(env={"FEED_TTL_SECONDS": "3600", "DEFAULT_INTERVAL_SECONDS": "30"})
    app = create_app(settings=settings, clock=clock)
    return TestClient(app)


@pytest.fixture
def api_key(client):
    resp = client.post("/keys", json={"email": "user@example.com"})
    assert resp.status_code == 201
    return resp.json()["api_key"]
