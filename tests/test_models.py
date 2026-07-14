# tests/test_models.py
import pytest
from pydantic import ValidationError

from app.models import CreateFeedRequest, CreateKeyRequest


def test_create_key_requires_valid_email():
    req = CreateKeyRequest(email="user@example.com", label="acme")
    assert req.email == "user@example.com"
    assert req.label == "acme"
    with pytest.raises(ValidationError):
        CreateKeyRequest(email="not-an-email")


def test_create_feed_minimal_requires_domain():
    req = CreateFeedRequest(domain="financial")
    assert req.domain == "financial"
    assert req.interval_seconds is None  # filled from config later
    with pytest.raises(ValidationError):
        CreateFeedRequest()


def test_create_feed_rejects_bad_variance():
    with pytest.raises(ValidationError):
        CreateFeedRequest(domain="news", variance_pct=150)
    with pytest.raises(ValidationError):
        CreateFeedRequest(domain="news", interval_seconds=0)
