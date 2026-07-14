# tests/test_api.py
from xml.etree import ElementTree as ET


def test_healthz(client):
    assert client.get("/healthz").json() == {"status": "ok"}


def test_domains_lists_seven(client):
    keys = {d["domain"] for d in client.get("/domains").json()["domains"]}
    assert keys == {"financial", "news", "weather", "sports", "ecommerce", "iot", "social"}


def test_create_feed_requires_key(client):
    resp = client.post("/feeds", json={"domain": "financial"})
    assert resp.status_code == 401


def test_create_and_read_feed_rss(client, api_key):
    resp = client.post("/feeds", json={"domain": "financial"}, headers={"X-API-Key": api_key})
    assert resp.status_code == 201
    path = resp.json()["path"]

    read = client.get(path)
    assert read.status_code == 200
    assert "application/rss+xml" in read.headers["content-type"]
    root = ET.fromstring(read.content)
    assert root.tag == "rss"


def test_read_feed_atom_via_query_and_accept(client, api_key):
    fid = client.post("/feeds", json={"domain": "news"}, headers={"X-API-Key": api_key}).json()["feed_id"]

    q = client.get(f"/feeds/{fid}?format=atom")
    assert "application/atom+xml" in q.headers["content-type"]

    a = client.get(f"/feeds/{fid}", headers={"Accept": "application/atom+xml"})
    assert "application/atom+xml" in a.headers["content-type"]


def test_absolute_urls_reflect_forwarded_proto(client, api_key):
    fid = client.post("/feeds", json={"domain": "iot"}, headers={"X-API-Key": api_key}).json()["feed_id"]
    resp = client.get(f"/feeds/{fid}", headers={"X-Forwarded-Proto": "https", "Host": "public.example"})
    # TestClient + proxy headers: Host header drives absolute links.
    assert b"public.example" in resp.content


def test_bad_domain_returns_422(client, api_key):
    resp = client.post("/feeds", json={"domain": "nope"}, headers={"X-API-Key": api_key})
    assert resp.status_code == 422


def test_stream_advances_between_reads(client, api_key, clock):
    fid = client.post("/feeds", json={"domain": "weather", "interval_seconds": 30, "variance_pct": 0},
                      headers={"X-API-Key": api_key}).json()["feed_id"]
    first = client.get(f"/feeds/{fid}")
    n_first = first.content.count(b"<item")
    clock.advance(seconds=90)
    second = client.get(f"/feeds/{fid}")
    n_second = second.content.count(b"<item")
    assert n_first > n_second  # first read seeds full window; second only ~3 new items


def test_delete_then_read_404(client, api_key):
    fid = client.post("/feeds", json={"domain": "sports"}, headers={"X-API-Key": api_key}).json()["feed_id"]
    assert client.delete(f"/feeds/{fid}").status_code == 204
    assert client.get(f"/feeds/{fid}").status_code == 404


def test_ttl_expiry_feed_404_and_key_401(client, api_key, clock):
    # Feed and key both created at t0 with a 3600s TTL (see conftest settings).
    fid = client.post("/feeds", json={"domain": "financial"},
                      headers={"X-API-Key": api_key}).json()["feed_id"]
    assert client.get(f"/feeds/{fid}").status_code == 200
    # Advance past the shared-clock TTL: feed expires -> 404, key expires -> 401.
    clock.advance(seconds=3601)
    assert client.get(f"/feeds/{fid}").status_code == 404
    assert client.post("/feeds", json={"domain": "financial"},
                       headers={"X-API-Key": api_key}).status_code == 401
