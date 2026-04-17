"""Tests for logslice.aggregate."""
import pytest
from logslice.aggregate import group_by, count_by, sum_by, avg_by


RECORDS = [
    {"level": "info", "duration": 10},
    {"level": "error", "duration": 50},
    {"level": "info", "duration": 20},
    {"level": "warn", "duration": 5},
    {"level": "error", "duration": 30},
]


class TestGroupBy:
    def test_groups_correctly(self):
        result = group_by(RECORDS, "level")
        assert len(result["info"]) == 2
        assert len(result["error"]) == 2
        assert len(result["warn"]) == 1

    def test_missing_field_grouped_under_missing(self):
        records = [{"level": "info"}, {"other": "x"}]
        result = group_by(records, "level")
        assert "__missing__" in result
        assert len(result["info"]) == 1

    def test_empty_input(self):
        assert group_by([], "level") == {}


class TestCountBy:
    def test_counts_correctly(self):
        result = count_by(RECORDS, "level")
        assert result["info"] == 2
        assert result["error"] == 2
        assert result["warn"] == 1

    def test_missing_field_counted(self):
        records = [{"level": "info"}, {}]
        result = count_by(records, "level")
        assert result["__missing__"] == 1

    def test_empty_input(self):
        assert count_by([], "level") == {}


class TestSumBy:
    def test_sums_correctly(self):
        result = sum_by(RECORDS, "level", "duration")
        assert result["info"] == 30.0
        assert result["error"] == 80.0
        assert result["warn"] == 5.0

    def test_skips_non_numeric(self):
        records = [{"level": "info", "duration": "fast"}, {"level": "info", "duration": 10}]
        result = sum_by(records, "level", "duration")
        assert result["info"] == 10.0

    def test_empty_input(self):
        assert sum_by([], "level", "duration") == {}


class TestAvgBy:
    def test_averages_correctly(self):
        result = avg_by(RECORDS, "level", "duration")
        assert result["info"] == 15.0
        assert result["error"] == 40.0
        assert result["warn"] == 5.0

    def test_skips_non_numeric(self):
        records = [{"level": "info", "duration": "x"}, {"level": "info", "duration": 20}]
        result = avg_by(records, "level", "duration")
        assert result["info"] == 20.0

    def test_empty_input(self):
        assert avg_by([], "level", "duration") == {}
