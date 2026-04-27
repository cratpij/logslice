"""Tests for logslice.timeline."""

from __future__ import annotations

from datetime import datetime

import pytest

from logslice.timeline import (
    _floor_timestamp,
    build_timeline,
    render_timeline,
    timeline_counts,
)


def _r(ts: str, **kwargs) -> dict:
    return {"timestamp": ts, **kwargs}


class TestFloorTimestamp:
    def test_floors_to_minute(self):
        ts = datetime(2024, 1, 1, 12, 3, 45)
        result = _floor_timestamp(ts, 60)
        assert result == datetime(2024, 1, 1, 12, 3, 0)

    def test_floors_to_five_minutes(self):
        ts = datetime(2024, 1, 1, 12, 7, 30)
        result = _floor_timestamp(ts, 300)
        assert result == datetime(2024, 1, 1, 12, 5, 0)

    def test_floors_to_hour(self):
        ts = datetime(2024, 1, 1, 15, 45, 0)
        result = _floor_timestamp(ts, 3600)
        assert result == datetime(2024, 1, 1, 15, 0, 0)


class TestBuildTimeline:
    def test_empty_input_returns_empty(self):
        assert build_timeline([]) == []

    def test_single_record(self):
        records = [_r("2024-01-01T10:00:30Z")]
        tl = build_timeline(records, bucket_seconds=60)
        assert len(tl) == 1
        bucket, recs = tl[0]
        assert bucket == datetime(2024, 1, 1, 10, 0, 0)
        assert len(recs) == 1

    def test_groups_into_buckets(self):
        records = [
            _r("2024-01-01T10:00:10Z"),
            _r("2024-01-01T10:00:50Z"),
            _r("2024-01-01T10:01:05Z"),
        ]
        tl = build_timeline(records, bucket_seconds=60)
        assert len(tl) == 2
        assert len(tl[0][1]) == 2
        assert len(tl[1][1]) == 1

    def test_sorted_by_bucket(self):
        records = [
            _r("2024-01-01T10:02:00Z"),
            _r("2024-01-01T10:00:00Z"),
        ]
        tl = build_timeline(records, bucket_seconds=60)
        assert tl[0][0] < tl[1][0]

    def test_missing_ts_field_skipped(self):
        records = [{"msg": "no timestamp"}, _r("2024-01-01T10:00:00Z")]
        tl = build_timeline(records, bucket_seconds=60)
        assert len(tl) == 1

    def test_invalid_ts_skipped(self):
        records = [_r("not-a-date"), _r("2024-01-01T10:00:00Z")]
        tl = build_timeline(records, bucket_seconds=60)
        assert len(tl) == 1

    def test_custom_ts_field(self):
        records = [{"time": "2024-01-01T10:00:00Z"}]
        tl = build_timeline(records, bucket_seconds=60, ts_field="time")
        assert len(tl) == 1


class TestTimelineCounts:
    def test_returns_bucket_and_count(self):
        records = [_r("2024-01-01T10:00:00Z"), _r("2024-01-01T10:00:30Z")]
        counts = timeline_counts(records, bucket_seconds=60)
        assert len(counts) == 1
        assert counts[0]["count"] == 2
        assert "bucket" in counts[0]

    def test_empty_returns_empty(self):
        assert timeline_counts([]) == []


class TestRenderTimeline:
    def test_empty_returns_empty_string(self):
        assert render_timeline([]) == ""

    def test_contains_bucket_label(self):
        records = [_r("2024-01-01T10:00:00Z")]
        tl = build_timeline(records, bucket_seconds=60)
        output = render_timeline(tl)
        assert "2024-01-01" in output

    def test_bar_uses_bar_char(self):
        records = [_r("2024-01-01T10:00:00Z")]
        tl = build_timeline(records, bucket_seconds=60)
        output = render_timeline(tl, bar_char="*")
        assert "*" in output

    def test_count_appears_in_output(self):
        records = [_r("2024-01-01T10:00:00Z"), _r("2024-01-01T10:00:20Z")]
        tl = build_timeline(records, bucket_seconds=60)
        output = render_timeline(tl)
        assert "2" in output
