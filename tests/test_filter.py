"""Tests for logslice.filter module."""

import pytest
from datetime import datetime
from logslice.filter import (
    parse_timestamp,
    filter_by_time,
    filter_by_field,
    filter_by_field_contains,
)


class TestParseTimestamp:
    def test_iso_with_microseconds_utc(self):
        dt = parse_timestamp("2024-01-15T10:30:00.123456Z")
        assert dt == datetime(2024, 1, 15, 10, 30, 0, 123456)

    def test_iso_utc(self):
        dt = parse_timestamp("2024-01-15T10:30:00Z")
        assert dt == datetime(2024, 1, 15, 10, 30, 0)

    def test_iso_no_tz(self):
        dt = parse_timestamp("2024-01-15T10:30:00")
        assert dt == datetime(2024, 1, 15, 10, 30, 0)

    def test_space_separated(self):
        dt = parse_timestamp("2024-01-15 10:30:00")
        assert dt == datetime(2024, 1, 15, 10, 30, 0)

    def test_invalid_returns_none(self):
        assert parse_timestamp("not-a-date") is None

    def test_none_input_returns_none(self):
        assert parse_timestamp(None) is None


class TestFilterByTime:
    ENTRIES = [
        {"timestamp": "2024-01-01T08:00:00Z", "msg": "a"},
        {"timestamp": "2024-01-01T10:00:00Z", "msg": "b"},
        {"timestamp": "2024-01-01T12:00:00Z", "msg": "c"},
    ]

    def test_filter_with_start_and_end(self):
        start = datetime(2024, 1, 1, 9, 0, 0)
        end = datetime(2024, 1, 1, 11, 0, 0)
        result = list(filter_by_time(iter(self.ENTRIES), start=start, end=end))
        assert len(result) == 1
        assert result[0]["msg"] == "b"

    def test_filter_with_start_only(self):
        start = datetime(2024, 1, 1, 9, 0, 0)
        result = list(filter_by_time(iter(self.ENTRIES), start=start))
        assert [e["msg"] for e in result] == ["b", "c"]

    def test_filter_with_end_only(self):
        end = datetime(2024, 1, 1, 9, 0, 0)
        result = list(filter_by_time(iter(self.ENTRIES), end=end))
        assert [e["msg"] for e in result] == ["a"]

    def test_missing_timestamp_field_skipped(self):
        entries = [{"msg": "no-ts"}, {"timestamp": "2024-01-01T10:00:00Z", "msg": "ok"}]
        result = list(filter_by_time(iter(entries)))
        assert len(result) == 1

    def test_custom_timestamp_field(self):
        entries = [{"time": "2024-01-01T10:00:00Z", "msg": "x"}]
        result = list(filter_by_time(iter(entries), timestamp_field="time"))
        assert len(result) == 1


class TestFilterByField:
    ENTRIES = [
        {"level": "info", "msg": "started"},
        {"level": "error", "msg": "failed"},
        {"level": "info", "msg": "done"},
    ]

    def test_exact_match(self):
        result = list(filter_by_field(iter(self.ENTRIES), "level", "error"))
        assert len(result) == 1
        assert result[0]["msg"] == "failed"

    def test_no_match_returns_empty(self):
        result = list(filter_by_field(iter(self.ENTRIES), "level", "debug"))
        assert result == []

    def test_missing_field_skipped(self):
        result = list(filter_by_field(iter(self.ENTRIES), "service", "api"))
        assert result == []


class TestFilterByFieldContains:
    ENTRIES = [
        {"msg": "connection refused"},
        {"msg": "request completed"},
        {"msg": "connection timeout"},
    ]

    def test_substring_match(self):
        result = list(filter_by_field_contains(iter(self.ENTRIES), "msg", "connection"))
        assert len(result) == 2

    def test_no_match(self):
        result = list(filter_by_field_contains(iter(self.ENTRIES), "msg", "error"))
        assert result == []
