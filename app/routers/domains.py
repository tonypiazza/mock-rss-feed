# app/routers/domains.py
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import Settings
from app.deps import get_settings
from app.domains.base import registry

router = APIRouter()


@router.get("/domains")
def list_domains(settings: Settings = Depends(get_settings)) -> dict:
    enabled = settings.enabled_domains
    out = []
    for key, gen in registry().items():
        if enabled and key not in enabled:
            continue
        out.append(gen.describe())
    return {"domains": out}


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
