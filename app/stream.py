# app/stream.py
from __future__ import annotations

import random
from datetime import datetime, timedelta


def jittered_timestamps(
    *,
    start: datetime,
    end: datetime,
    interval_seconds: float,
    variance_pct: float,
    max_items: int,
    rng: random.Random,
) -> list[datetime]:
    """Timestamps in (start, end], mean gap interval_seconds ± variance_pct,
    capped to the most recent max_items."""
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")

    frac = max(0.0, min(1.0, variance_pct / 100.0))
    low = interval_seconds * (1.0 - frac)
    high = interval_seconds * (1.0 + frac)

    out: list[datetime] = []
    cursor = start
    while True:
        gap = rng.uniform(low, high) if high > low else interval_seconds
        cursor = cursor + timedelta(seconds=gap)
        if cursor > end:
            break
        out.append(cursor)

    if len(out) > max_items:
        out = out[-max_items:]
    return out
