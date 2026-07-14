# app/routers/feeds.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.deps import get_feed_store, get_settings, require_api_key, resolve_base_url
from app.feed_render import render_feed
from app.feeds import FeedNotFound, FeedStore, InvalidFeedRequest
from app.models import CreateFeedRequest, CreateFeedResponse

router = APIRouter()


def _choose_format(fmt_param: str | None, accept: str) -> str:
    if fmt_param in ("rss", "atom"):
        return fmt_param
    if "application/atom+xml" in accept:
        return "atom"
    return "rss"


@router.post("/feeds", response_model=CreateFeedResponse, status_code=201)
def create_feed(
    body: CreateFeedRequest,
    store: FeedStore = Depends(get_feed_store),
    _key: str = Depends(require_api_key),
) -> CreateFeedResponse:
    try:
        record = store.create(
            domain=body.domain, title=body.title, description=body.description,
            interval_seconds=body.interval_seconds, variance_pct=body.variance_pct,
            categories=body.categories, params=body.params,
        )
    except InvalidFeedRequest as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return CreateFeedResponse(
        feed_id=record["feed_id"],
        path=f"/feeds/{record['feed_id']}",
        expires_at=record["expires_at"],
    )


@router.get("/feeds/{feed_id}")
def read_feed(
    feed_id: str,
    request: Request,
    format: str | None = None,
    store: FeedStore = Depends(get_feed_store),
) -> Response:
    try:
        items, title, description = store.read(feed_id)
    except FeedNotFound as exc:
        raise HTTPException(status_code=404, detail="feed not found") from exc

    fmt = _choose_format(format, request.headers.get("accept", ""))
    base_url = resolve_base_url(request, get_settings(request))
    xml = render_feed(
        feed_id=feed_id, title=title, description=description,
        items=items, fmt=fmt, base_url=base_url,
    )
    media = "application/atom+xml" if fmt == "atom" else "application/rss+xml"
    return Response(content=xml, media_type=media)


@router.delete("/feeds/{feed_id}", status_code=204)
def delete_feed(feed_id: str, store: FeedStore = Depends(get_feed_store)) -> Response:
    try:
        store.delete(feed_id)
    except FeedNotFound as exc:
        raise HTTPException(status_code=404, detail="feed not found") from exc
    return Response(status_code=204)
