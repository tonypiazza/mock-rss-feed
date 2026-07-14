# app/models.py
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class CreateKeyRequest(BaseModel):
    email: EmailStr
    label: str | None = None


class CreateKeyResponse(BaseModel):
    api_key: str
    expires_at: str


class CreateFeedRequest(BaseModel):
    domain: str
    title: str | None = None
    description: str | None = None
    interval_seconds: int | None = Field(default=None, gt=0)
    variance_pct: float | None = Field(default=None, ge=0, le=100)
    categories: list[str] | None = None
    params: dict | None = None


class CreateFeedResponse(BaseModel):
    feed_id: str
    path: str
    expires_at: str
