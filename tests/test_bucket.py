"""Tests for logslice.bucket."""

import pytest
from logslice.bucket import bucket_counts, bucket_label, bucket_records, iter_buckets


# ---------------------------------------------------------------------------
# bucket_label
# ---------------------------------------------------------------------------

class TestBucketLabel:
    def test_integer_boundaries(self):
        assert bucket_label(5.0, 10.0) == "[0, 10)"

    def test_value_at_upper_boundary_goes_to_next_bucket(self):
        assert bucket_label(10.0, 10.0) == "[10, 20)"

    def test_negative_value(self):
        assert bucket_label(-3.0, 10.0) == "[-10, 0)"

    def test_float_bucket_size(self):
        label = bucket_label(0.7, 0.5)
        assert label == "[0.5, 1.0)"

    def test_large_value(self):
        assert bucket_label(95.0, 10.0) == "[90, 100)"


# ---------------------------------------------------------------------------
# bucket_records
# ---------------------------------------------------------------------------

class TestBucketRecords:
    def _records(self):
        return [
            {"id": 1, "latency": 5},
            {"id": 2, "latency": 12},
            {"id": 3, "latency": 8},
            {"id": 4, "latency": 25},
            {"id": 5, "latency": 10},
        ]

    def test_groups_into_correct_buckets(self):
        result = bucket_records(self._records(), "latency", 10)
        assert "[0, 10)" in result
        assert "[10, 20)" in result
        assert "[20, 30)" in result

    def test_bucket_membership(self):
        result = bucket_records(self._records(), "latency", 10)
        ids_0_10 = [r["id"] for r in result["[0, 10)"]]
        assert ids_0_10 == [1, 3]

    def test_missing_field_goes_to_missing_key(self):
        records = [{"id": 1}, {"id": 2, "latency": 5}]
        result = bucket_records(records, "latency", 10)
        assert "__missing__" in result
        assert result["__missing__"][0]["id"] == 1

    def test_non_numeric_field_goes_to_missing(self):
        records = [{"latency": "fast"}, {"latency": 7}]
        result = bucket_records(records, "latency", 10)
        assert "__missing__" in result

    def test_empty_input_returns_empty_dict(self):
        assert bucket_records([], "latency", 10) == {}

    def test_buckets_sorted_by_lower_bound(self):
        records = [{"v": 50}, {"v": 5}, {"v": 25}]
        result = bucket_records(records, "v", 10)
        keys = list(result.keys())
        assert keys == ["[0, 10)", "[20, 30)", "[50, 60)"]

    def test_missing_sorted_last(self):
        records = [{"v": None}, {"v": 5}]
        result = bucket_records(records, "v", 10)
        assert list(result.keys())[-1] == "__missing__"


# ---------------------------------------------------------------------------
# bucket_counts
# ---------------------------------------------------------------------------

class TestBucketCounts:
    def test_returns_correct_counts(self):
        records = [{"n": i} for i in range(20)]
        counts = bucket_counts(records, "n", 10)
        assert counts["[0, 10)"] == 10
        assert counts["[10, 20)"] == 10

    def test_empty_input(self):
        assert bucket_counts([], "n", 10) == {}


# ---------------------------------------------------------------------------
# iter_buckets
# ---------------------------------------------------------------------------

class TestIterBuckets:
    def test_yields_label_and_records(self):
        records = [{"x": 3}, {"x": 15}]
        pairs = list(iter_buckets(records, "x", 10))
        assert pairs[0][0] == "[0, 10)"
        assert pairs[1][0] == "[10, 20)"

    def test_yields_in_sorted_order(self):
        records = [{"x": 55}, {"x": 2}]
        labels = [label for label, _ in iter_buckets(records, "x", 10)]
        assert labels == ["[0, 10)", "[50, 60)"]
