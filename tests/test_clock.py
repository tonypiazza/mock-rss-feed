# tests/test_clock.py
from datetime import UTC, datetime

from app.clock import FixedClock, SystemClock


def test_system_clock_is_utc_aware():
    now = SystemClock().now()
    assert now.tzinfo is not None
    assert now.utcoffset().total_seconds() == 0


def test_fixed_clock_returns_set_time_and_can_advance():
    t = datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC)
    c = FixedClock(t)
    assert c.now() == t
    c.advance(seconds=90)
    assert c.now() == datetime(2026, 7, 14, 12, 1, 30, tzinfo=UTC)
