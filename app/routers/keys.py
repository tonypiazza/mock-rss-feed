# app/routers/keys.py
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import get_key_store
from app.keys import KeyStore
from app.models import CreateKeyRequest, CreateKeyResponse

router = APIRouter()


@router.post("/keys", response_model=CreateKeyResponse, status_code=201)
def create_key(body: CreateKeyRequest, store: KeyStore = Depends(get_key_store)) -> CreateKeyResponse:
    record = store.mint(email=str(body.email), label=body.label)
    return CreateKeyResponse(api_key=record["api_key"], expires_at=record["expires_at"])
