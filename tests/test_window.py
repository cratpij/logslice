"""Tests for logslice.window."""

from datetime import datetime, timezone
from logslice.window import tumbling_windows, sliding_windows


def _r(ts: str, **extra) -> dict:
    return {"timestamp": ts, **extra}


T0 = "2024-01-01T00:00:00Z"
T30 = "2024-01-01T00:00:30Z"
T60 = "2024-01-01T00:01:00Z"
T90 = "2024-01-01T00:01:30Z"
T120 = "2024-01-01T00:02:00Z"


class TestTumblingWindows:
    def test_empty_input(self):
        result = list(tumbling_windows([], 60))
        assert result == []

    def test_single_window(self):
        records = [_r(T0), _r(T30)]
        windows = list(tumbling_windows(records, 60))
        assert len(windows) == 1
        assert len(windows[0]["records"]) == 2

    def test_two_windows(self):
        records = [_r(T0), _r(T30), _r(T60), _r(T90)]
        windows = list(tumbling_windows(records, 60))
        assert len(windows) == 2
        assert len(windows[0]["records"]) == 2
        assert len(windows[1]["records"]) == 2

    def test_window_boundaries(self):
        records = [_r(T0), _r(T60)]
        windows = list(tumbling_windows(records, 60))
        assert len(windows) == 2

    def test_skips_unparseable_timestamp(self):
        records = [{"timestamp": "not-a-date"}, _r(T0)]
        windows = list(tumbling_windows(records, 60))
        assert len(windows) == 1
        assert len(windows[0]["records"]) == 1

    def test_missing_ts_field_skipped(self):
        records = [{"msg": "no ts"}, _r(T0)]
        windows = list(tumbling_windows(records, 60))
        assert len(windows) == 1

    def test_window_has_start_end_records_keys(self):
        windows = list(tumbling_windows([_r(T0)], 60))
        assert "start" in windows[0]
        assert "end" in windows[0]
        assert "records" in windows[0]

    def test_custom_ts_field(self):
        records = [{"ts": T0}, {"ts": T30}]
        windows = list(tumbling_windows(records, 60, ts_field="ts"))
        assert len(windows) == 1


class TestSlidingWindows:
    def test_empty_input(self):
        result = list(sliding_windows([], 60, 30))
        assert result == []

    def test_overlapping_windows(self):
        records = [_r(T0), _r(T30), _r(T60), _r(T90)]
        windows = list(sliding_windows(records, 60, 30))
        assert len(windows) >= 2

    def test_first_window_contains_first_record(self):
        records = [_r(T0), _r(T30)]
        windows = list(sliding_windows(records, 60, 30))
        assert any(r["timestamp"] == T0 for r in windows[0]["records"])

    def test_record_appears_in_multiple_windows(self):
        records = [_r(T0), _r(T30), _r(T60)]
        windows = list(sliding_windows(records, 90, 30))
        counts = sum(1 for w in windows if any(r["timestamp"] == T30 for r in w["records"]))
        assert counts > 1

    def test_skips_unparseable(self):
        records = [{"timestamp": "bad"}, _r(T0)]
        windows = list(sliding_windows(records, 60, 30))
        for w in windows:
            assert all(r["timestamp"] != "bad" for r in w["records"])
