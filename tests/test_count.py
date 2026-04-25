"""Tests for logslice.count."""
import pytest

from logslice.count import (
    count_records,
    count_where,
    frequency_by_field,
    running_count,
    top_n,
)


RECORDS = [
    {"level": "info",  "svc": "api"},
    {"level": "error", "svc": "api"},
    {"level": "info",  "svc": "worker"},
    {"level": "warn",  "svc": "api"},
    {"level": "info",  "svc": "api"},
]


class TestCountRecords:
    def test_correct_total(self):
        assert count_records(RECORDS) == 5

    def test_empty_input(self):
        assert count_records([]) == 0

    def test_single_record(self):
        assert count_records([{"a": 1}]) == 1


class TestFrequencyByField:
    def test_counts_all_values(self):
        freq = frequency_by_field(RECORDS, "level")
        assert freq["info"] == 3
        assert freq["error"] == 1
        assert freq["warn"] == 1

    def test_sorted_descending(self):
        freq = frequency_by_field(RECORDS, "level")
        counts = list(freq.values())
        assert counts == sorted(counts, reverse=True)

    def test_missing_field_uses_placeholder(self):
        records = [{"level": "info"}, {"other": "x"}, {}]
        freq = frequency_by_field(records, "level")
        assert freq["<missing>"] == 2

    def test_custom_missing_label(self):
        records = [{"x": 1}, {}]
        freq = frequency_by_field(records, "level", missing="N/A")
        assert "N/A" in freq

    def test_empty_input_returns_empty(self):
        assert frequency_by_field([], "level") == {}


class TestTopN:
    def test_returns_n_items(self):
        result = top_n(RECORDS, "level", 2)
        assert len(result) == 2

    def test_first_is_most_common(self):
        result = top_n(RECORDS, "level", 1)
        assert result[0][0] == "info"
        assert result[0][1] == 3

    def test_n_larger_than_unique_values(self):
        result = top_n(RECORDS, "level", 100)
        assert len(result) == 3  # info, error, warn

    def test_empty_input_returns_empty(self):
        assert top_n([], "level", 5) == []


class TestCountWhere:
    def test_counts_matching_records(self):
        assert count_where(RECORDS, "level", "info") == 3

    def test_no_matches_returns_zero(self):
        assert count_where(RECORDS, "level", "debug") == 0

    def test_missing_field_not_counted(self):
        records = [{"other": "info"}, {"level": "info"}]
        assert count_where(records, "level", "info") == 1


class TestRunningCount:
    def test_yields_correct_totals(self):
        pairs = list(running_count(RECORDS))
        assert [n for _, n in pairs] == [1, 2, 3, 4, 5]

    def test_records_are_unchanged(self):
        pairs = list(running_count(RECORDS))
        assert [r for r, _ in pairs] == RECORDS

    def test_empty_input_yields_nothing(self):
        assert list(running_count([])) == []
