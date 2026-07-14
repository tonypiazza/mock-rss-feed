# tests/test_stream.py
import random
from datetime import UTC, datetime, timedelta

from app.stream import jittered_timestamps


def _dt(s: int) -> datetime:
    return datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC) + timedelta(seconds=s)


def test_timestamps_fall_within_window_and_are_ordered():
    ts = jittered_timestamps(
        start=_dt(0), end=_dt(300), interval_seconds=30, variance_pct=20,
        max_items=200, rng=random.Random(1),
    )
    assert ts == sorted(ts)
    assert all(_dt(0) < t <= _dt(300) for t in ts)


def test_average_rate_is_approximately_interval():
    ts = jittered_timestamps(
        start=_dt(0), end=_dt(3600), interval_seconds=30, variance_pct=20,
        max_items=100000, rng=random.Random(2),
    )
    # ~3600/30 = ~120 items, within a tolerance band for jitter.
    assert 100 <= len(ts) <= 140


def test_jitter_respects_variance_bounds():
    ts = jittered_timestamps(
        start=_dt(0), end=_dt(3600), interval_seconds=30, variance_pct=20,
        max_items=100000, rng=random.Random(3),
    )
    gaps = [(b - a).total_seconds() for a, b in zip(ts, ts[1:])]
    assert all(24.0 <= g <= 36.0 for g in gaps)  # 30 ± 20%


def test_cap_keeps_most_recent_items():
    ts = jittered_timestamps(
        start=_dt(0), end=_dt(3600), interval_seconds=1, variance_pct=0,
        max_items=200, rng=random.Random(4),
    )
    assert len(ts) == 200
    assert ts[-1] <= _dt(3600)
    # kept items are the most recent → last item near the end of the window
    assert ts[-1] >= _dt(3600) - timedelta(seconds=5)


def test_empty_when_no_time_elapsed():
    ts = jittered_timestamps(
        start=_dt(100), end=_dt(100), interval_seconds=30, variance_pct=20,
        max_items=200, rng=random.Random(5),
    )
    assert ts == []
