# app/deps.py
from __future__ import annotations

from fastapi import Header, HTTPException, Request

from app.config import Settings
from app.feeds import FeedStore
from app.keys import KeyStore


def resolve_base_url(request: Request, settings: Settings) -> str:
    if settings.public_base_url:
        return settings.public_base_url.rstrip("/")
    host = request.headers.get("host", "localhost")
    return f"{request.url.scheme}://{host}"


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_key_store(request: Request) -> KeyStore:
    return request.app.state.key_store


def get_feed_store(request: Request) -> FeedStore:
    return request.app.state.feed_store


def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> str:
    key = x_api_key
    if not key and authorization and authorization.lower().startswith("bearer "):
        key = authorization[7:].strip()
    store: KeyStore = request.app.state.key_store
    if not store.is_valid(key):
        raise HTTPException(status_code=401, detail="missing or invalid API key")
    return key
