"""Tests for logslice.slicer module."""

import json
import pytest
from datetime import datetime
from logslice.slicer import Slicer


def make_lines(*entries):
    return [json.dumps(e) for e in entries]


ENTRIES = [
    {"timestamp": "2024-03-01T09:00:00Z", "level": "info", "service": "api", "msg": "started"},
    {"timestamp": "2024-03-01T10:00:00Z", "level": "error", "service": "api", "msg": "connection refused"},
    {"timestamp": "2024-03-01T11:00:00Z", "level": "info", "service": "worker", "msg": "job done"},
    {"timestamp": "2024-03-01T12:00:00Z", "level": "error", "service": "worker", "msg": "timeout error"},
]


class TestSlicerTimeRange:
    def test_filters_by_start(self):
        lines = make_lines(*ENTRIES)
        start = datetime(2024, 3, 1, 10, 30, 0)
        result = list(Slicer(lines).time_range(start=start).run())
        assert len(result) == 2
        assert result[0]["msg"] == "job done"

    def test_filters_by_end(self):
        lines = make_lines(*ENTRIES)
        end = datetime(2024, 3, 1, 9, 30, 0)
        result = list(Slicer(lines).time_range(end=end).run())
        assert len(result) == 1
        assert result[0]["msg"] == "started"

    def test_filters_by_range(self):
        lines = make_lines(*ENTRIES)
        start = datetime(2024, 3, 1, 9, 30, 0)
        end = datetime(2024, 3, 1, 11, 30, 0)
        result = list(Slicer(lines).time_range(start=start, end=end).run())
        assert len(result) == 2


class TestSlicerFieldFilter:
    def test_where_exact(self):
        lines = make_lines(*ENTRIES)
        result = list(Slicer(lines).where("level", "error").run())
        assert len(result) == 2
        assert all(e["level"] == "error" for e in result)

    def test_where_chained(self):
        lines = make_lines(*ENTRIES)
        result = list(Slicer(lines).where("level", "error").where("service", "worker").run())
        assert len(result) == 1
        assert result[0]["msg"] == "timeout error"

    def test_where_contains(self):
        lines = make_lines(*ENTRIES)
        result = list(Slicer(lines).where_contains("msg", "error").run())
        assert len(result) == 1
        assert result[0]["msg"] == "timeout error"


class TestSlicerCombined:
    def test_time_and_field(self):
        lines = make_lines(*ENTRIES)
        start = datetime(2024, 3, 1, 9, 30, 0)
        result = list(
            Slicer(lines).time_range(start=start).where("level", "error").run()
        )
        assert len(result) == 2

    def test_no_match_returns_empty(self):
        lines = make_lines(*ENTRIES)
        result = list(Slicer(lines).where("level", "debug").run())
        assert result == []

    def test_invalid_lines_skipped(self):
        lines = ["not json", json.dumps(ENTRIES[0]), "also bad"]
        result = list(Slicer(lines).run())
        assert len(result) == 1
