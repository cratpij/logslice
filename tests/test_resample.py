"""Tests for logslice.resample."""

import pytest
from logslice.resample import resample_count, resample_sum, resample_avg


def _r(ts, **kwargs):
    return {"timestamp": ts, **kwargs}


RECORDS = [
    _r("2024-01-01T00:00:10Z", duration=10, status="ok"),
    _r("2024-01-01T00:00:40Z", duration=20, status="ok"),
    _r("2024-01-01T00:01:05Z", duration=30, status="err"),
    _r("2024-01-01T00:01:50Z", duration=40, status="ok"),
    _r("2024-01-01T00:02:15Z", duration=50, status="ok"),
]


class TestResampleCount:
    def test_groups_into_buckets(self):
        result = list(resample_count(RECORDS, interval_seconds=60))
        assert len(result) == 3

    def test_correct_counts_per_bucket(self):
        result = list(resample_count(RECORDS, interval_seconds=60))
        counts = {r["bucket"]: r["count"] for r in result}
        assert counts["2024-01-01T00:00:00+00:00"] == 2
        assert counts["2024-01-01T00:01:00+00:00"] == 2
        assert counts["2024-01-01T00:02:00+00:00"] == 1

    def test_empty_input_returns_empty(self):
        result = list(resample_count([], interval_seconds=60))
        assert result == []

    def test_missing_timestamp_skipped(self):
        records = [{"msg": "no ts"}, _r("2024-01-01T00:00:05Z")]
        result = list(resample_count(records, interval_seconds=60))
        assert len(result) == 1
        assert result[0]["count"] == 1

    def test_buckets_sorted_ascending(self):
        result = list(resample_count(RECORDS, interval_seconds=60))
        buckets = [r["bucket"] for r in result]
        assert buckets == sorted(buckets)

    def test_custom_ts_field(self):
        records = [{"ts": "2024-01-01T00:00:05Z"}, {"ts": "2024-01-01T00:00:55Z"}]
        result = list(resample_count(records, interval_seconds=60, ts_field="ts"))
        assert len(result) == 1
        assert result[0]["count"] == 2


class TestResampleSum:
    def test_sums_field_per_bucket(self):
        result = list(resample_sum(RECORDS, "duration", interval_seconds=60))
        sums = {r["bucket"]: r["duration"] for r in result}
        assert sums["2024-01-01T00:00:00+00:00"] == 30.0
        assert sums["2024-01-01T00:01:00+00:00"] == 70.0
        assert sums["2024-01-01T00:02:00+00:00"] == 50.0

    def test_missing_field_skipped(self):
        records = [_r("2024-01-01T00:00:10Z"), _r("2024-01-01T00:00:20Z", duration=5)]
        result = list(resample_sum(records, "duration", interval_seconds=60))
        assert result[0]["duration"] == 5.0

    def test_empty_input(self):
        assert list(resample_sum([], "duration", interval_seconds=60)) == []

    def test_non_numeric_field_skipped(self):
        records = [
            _r("2024-01-01T00:00:10Z", duration="fast"),
            _r("2024-01-01T00:00:20Z", duration=10),
        ]
        result = list(resample_sum(records, "duration", interval_seconds=60))
        assert result[0]["duration"] == 10.0


class TestResampleAvg:
    def test_averages_field_per_bucket(self):
        result = list(resample_avg(RECORDS, "duration", interval_seconds=60))
        avgs = {r["bucket"]: r["duration"] for r in result}
        assert avgs["2024-01-01T00:00:00+00:00"] == pytest.approx(15.0)
        assert avgs["2024-01-01T00:01:00+00:00"] == pytest.approx(35.0)
        assert avgs["2024-01-01T00:02:00+00:00"] == pytest.approx(50.0)

    def test_empty_input(self):
        assert list(resample_avg([], "duration", interval_seconds=60)) == []

    def test_single_record_avg_equals_value(self):
        records = [_r("2024-01-01T00:00:10Z", duration=42)]
        result = list(resample_avg(records, "duration", interval_seconds=60))
        assert result[0]["duration"] == pytest.approx(42.0)
