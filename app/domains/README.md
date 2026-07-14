# Adding a domain

A **domain** defines what kind of content a feed produces (financial tickers,
weather reports, IoT readings, …). Domains are plain Python — adding one is a
single self-contained file plus one import line, and the test suite picks it up
automatically.

## The `DomainGenerator` interface

Every domain subclasses `DomainGenerator` (see [`base.py`](base.py)), sets four
class attributes, and implements one method:

| Member | Type | Purpose |
|---|---|---|
| `domain_key` | `str` | Stable identifier used in the API (`{"domain": "..."}`) and as the registry key. |
| `default_params` | `dict` | Domain-specific knobs and their defaults (e.g. `{"tickers": [...]}`). |
| `param_schema` | `dict` | Maps each allowed param name to its expected type (e.g. `{"tickers": list}`). Callers can only override params listed here; anything else is rejected with a 422. |
| `default_categories` | `list[str]` | The pool of `<category>` tags. Each item gets a random 1–N subset unless the caller overrides `categories`. |
| `make_item(ts, params, categories, rng)` | method | Build **one** `FeedItem` for timestamp `ts`. Use the injected `rng` for **all** randomness so output is reproducible. |

The base class handles the rest — merging/validating params, choosing the
category subset per item, driving the timestamp/stream engine, and applying the
per-response cap. You only write `make_item`.

## Steps

1. **Create `app/domains/<yourdomain>.py`.** Subclass `DomainGenerator`, decorate
   with `@register`, set the four attributes, and implement `make_item`.

2. **Register it** by adding the module to the import list in
   [`__init__.py`](__init__.py) (imported for its registration side effect):

   ```python
   from app.domains import (  # noqa: F401
       ...,
       yourdomain,
   )
   ```

3. **That's it.** The domain now appears in `GET /domains`, can be used in
   `POST /feeds`, and is exercised by the generic contract test in
   `tests/domains/test_contract.py` (add its `domain_key` to that test's
   `EXPECTED` set so the suite asserts it is registered).

## Example

```python
# app/domains/aviation.py
from __future__ import annotations

from app.domains.base import DomainGenerator, FeedItem, register

_STATUSES = ["on time", "delayed", "boarding", "departed", "cancelled"]


@register
class AviationDomain(DomainGenerator):
    domain_key = "aviation"
    default_params = {"airports": ["JFK", "LHR", "NRT", "SFO"]}
    param_schema = {"airports": list}
    default_categories = ["departures", "arrivals", "delays", "gate-changes"]

    def make_item(self, ts, params, categories, rng):
        airport = rng.choice(params["airports"])
        flight = f"{rng.choice(['AA', 'BA', 'JL', 'UA'])}{rng.randint(100, 999)}"
        status = rng.choice(_STATUSES)
        return FeedItem(
            guid=f"{self.domain_key}-{flight}-{ts.isoformat()}",
            title=f"{flight} @ {airport}: {status}",
            summary=f"Flight {flight} at {airport} is {status}.",
            published=ts,
            categories=categories,
            link_suffix=flight.lower(),
        )
```

## Guidelines

- **Use `rng` for everything random.** Never call the `random` module directly or
  use wall-clock time — determinism per `(feed, window)` depends on the injected
  `rng`.
- **Build a stable-ish `guid`** from `domain_key` + identifying detail + `ts`.
- **`link_suffix`** is optional; when set it forms a per-item link path under the
  feed URL. Leave it `None` if items have no natural sub-resource.
- **Keep it small.** One file, one responsibility — mirror the existing domains
  (e.g. [`financial.py`](financial.py), [`weather.py`](weather.py)).
