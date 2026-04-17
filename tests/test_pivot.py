"""Tests for logslice.pivot."""
import pytest
from logslice.pivot import pivot_count, pivot_sum, pivot_avg


RECORDS = [
    {"level": "info", "duration": 10},
    {"level": "error", "duration": 50},
    {"level": "info", "duration": 20},
    {"level": "warn", "duration": 5},
    {"level": "error", "duration": 30},
]


class TestPivotCount:
    def test_sorted_descending(self):
        result = pivot_count(RECORDS, "level")
        counts = [r["count"] for r in result]
        assert counts == sorted(counts, reverse=True)

    def test_contains_all_groups(self):
        result = pivot_count(RECORDS, "level")
        levels = {r["level"] for r in result}
        assert levels == {"info", "error", "warn"}

    def test_correct_counts(self):
        result = pivot_count(RECORDS, "level")
        by_level = {r["level"]: r["count"] for r in result}
        assert by_level["info"] == 2
        assert by_level["error"] == 2
        assert by_level["warn"] == 1

    def test_empty_input(self):
        assert pivot_count([], "level") == []


class TestPivotSum:
    def test_sorted_descending(self):
        result = pivot_sum(RECORDS, "level", "duration")
        sums = [r["sum"] for r in result]
        assert sums == sorted(sums, reverse=True)

    def test_correct_sums(self):
        result = pivot_sum(RECORDS, "level", "duration")
        by_level = {r["level"]: r["sum"] for r in result}
        assert by_level["info"] == 30.0
        assert by_level["error"] == 80.0

    def test_empty_input(self):
        assert pivot_sum([], "level", "duration") == []


class TestPivotAvg:
    def test_sorted_descending(self):
        result = pivot_avg(RECORDS, "level", "duration")
        avgs = [r["avg"] for r in result]
        assert avgs == sorted(avgs, reverse=True)

    def test_correct_avgs(self):
        result = pivot_avg(RECORDS, "level", "duration")
        by_level = {r["level"]: r["avg"] for r in result}
        assert by_level["info"] == 15.0
        assert by_level["error"] == 40.0

    def test_empty_input(self):
        assert pivot_avg([], "level", "duration") == []
