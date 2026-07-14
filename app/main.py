# app/main.py
from __future__ import annotations

from fastapi import FastAPI

import app.domains  # noqa: F401  (register domains)
from app.cache.factory import build_cache
from app.clock import Clock, SystemClock
from app.config import Settings
from app.feeds import FeedStore
from app.keys import KeyStore
from app.routers import domains as domains_router
from app.routers import feeds as feeds_router
from app.routers import keys as keys_router


def create_app(settings: Settings | None = None, clock: Clock | None = None) -> FastAPI:
    settings = settings or Settings()
    clock = clock or SystemClock()
    cache = build_cache(settings, clock=clock)

    application = FastAPI(title="Mock RSS Feed Service")
    application.state.settings = settings
    application.state.clock = clock
    application.state.cache = cache
    application.state.key_store = KeyStore(
        cache=cache, clock=clock, ttl_seconds=settings.feed_ttl_seconds
    )
    application.state.feed_store = FeedStore(cache=cache, clock=clock, settings=settings)

    application.include_router(keys_router.router)
    application.include_router(feeds_router.router)
    application.include_router(domains_router.router)
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = Settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
