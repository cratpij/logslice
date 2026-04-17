"""Tests for logslice.sort module."""

import pytest
from logslice.sort import sort_by_field, sort_by_timestamp, sort_by_numeric


RECORDS = [
    {"id": 1, "name": "charlie", "score": 80, "ts": "2024-01-03T10:00:00Z"},
    {"id": 2, "name": "alice",   "score": 95, "ts": "2024-01-01T08:00:00Z"},
    {"id": 3, "name": "bob",     "score": 70, "ts": "2024-01-02T09:00:00Z"},
]


class TestSortByField:
    def test_sorts_ascending(self):
        result = sort_by_field(RECORDS, "name")
        assert [r["name"] for r in result] == ["alice", "bob", "charlie"]

    def test_sorts_descending(self):
        result = sort_by_field(RECORDS, "name", reverse=True)
        assert [r["name"] for r in result] == ["charlie", "bob", "alice"]

    def test_missing_field_sorts_last(self):
        records = [{"name": "z"}, {}, {"name": "a"}]
        result = sort_by_field(records, "name")
        assert result[0]["name"] == "a"
        assert result[-1] == {}

    def test_empty_input(self):
        assert sort_by_field([], "name") == []

    def test_does_not_mutate_input(self):
        original = list(RECORDS)
        sort_by_field(RECORDS, "name")
        assert list(RECORDS) == original


class TestSortByTimestamp:
    def test_sorts_chronologically(self):
        result = sort_by_timestamp(RECORDS, field="ts")
        assert [r["id"] for r in result] == [2, 3, 1]

    def test_sorts_reverse(self):
        result = sort_by_timestamp(RECORDS, field="ts", reverse=True)
        assert [r["id"] for r in result] == [1, 3, 2]

    def test_missing_ts_placed_last(self):
        records = [{"ts": "2024-01-01T00:00:00Z", "id": 1}, {"id": 2}]
        result = sort_by_timestamp(records, field="ts")
        assert result[0]["id"] == 1
        assert result[-1]["id"] == 2

    def test_invalid_ts_placed_last(self):
        records = [{"ts": "not-a-date", "id": 1}, {"ts": "2024-06-01T00:00:00Z", "id": 2}]
        result = sort_by_timestamp(records, field="ts")
        assert result[0]["id"] == 2

    def test_empty_input(self):
        assert sort_by_timestamp([], field="ts") == []


class TestSortByNumeric:
    def test_sorts_ascending(self):
        result = sort_by_numeric(RECORDS, "score")
        assert [r["score"] for r in result] == [70, 80, 95]

    def test_sorts_descending(self):
        result = sort_by_numeric(RECORDS, "score", reverse=True)
        assert [r["score"] for r in result] == [95, 80, 70]

    def test_non_numeric_placed_last(self):
        records = [{"v": 5}, {"v": "abc"}, {"v": 1}]
        result = sort_by_numeric(records, "v")
        assert result[0]["v"] == 1
        assert result[-1]["v"] == "abc"

    def test_missing_field_placed_last(self):
        records = [{"v": 3}, {}]
        result = sort_by_numeric(records, "v")
        assert result[0]["v"] == 3

    def test_float_strings_parsed(self):
        records = [{"v": "3.5"}, {"v": "1.2"}]
        result = sort_by_numeric(records, "v")
        assert result[0]["v"] == "1.2"
