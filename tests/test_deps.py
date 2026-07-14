# tests/test_deps.py
from types import SimpleNamespace

from app.config import Settings
from app.deps import resolve_base_url


def _request(scheme, host, base_url):
    # Mimic the parts of starlette.Request used by resolve_base_url.
    return SimpleNamespace(
        url=SimpleNamespace(scheme=scheme),
        headers={"host": host},
        base_url=base_url,
    )


def test_public_base_url_wins():
    s = Settings(env={"PUBLIC_BASE_URL": "https://configured.example"})
    req = _request("http", "internal:80", "http://internal/")
    assert resolve_base_url(req, s) == "https://configured.example"


def test_falls_back_to_forwarded_scheme_and_host():
    s = Settings(env={})
    req = _request("https", "public.example", "https://public.example/")
    assert resolve_base_url(req, s) == "https://public.example"
