"""Tests for logslice.stats."""
from collections import Counter
import pytest
from logslice.stats import count_by_field, field_values, summary


RECORDS = [
    {"level": "info",  "msg": "started",  "code": 200},
    {"level": "info",  "msg": "ok",        "code": 200},
    {"level": "warn",  "msg": "slow",      "code": 200},
    {"level": "error", "msg": "failed",    "code": 500},
    {"msg": "no-level", "code": 404},
]


class TestCountByField:
    def test_counts_known_field(self):
        c = count_by_field(RECORDS, "level")
        assert c["info"] == 2
        assert c["warn"] == 1
        assert c["error"] == 1

    def test_missing_field_excluded(self):
        c = count_by_field(RECORDS, "level")
        assert sum(c.values()) == 4  # record without 'level' skipped

    def test_empty_records(self):
        assert count_by_field([], "level") == Counter()

    def test_field_not_present_in_any(self):
        c = count_by_field(RECORDS, "nonexistent")
        assert len(c) == 0


class TestFieldValues:
    def test_returns_all_values(self):
        vals = field_values(RECORDS, "code")
        assert vals == [200, 200, 200, 500, 404]

    def test_missing_field_gives_none(self):
        vals = field_values(RECORDS, "level")
        assert vals[-1] is None

    def test_empty_records(self):
        assert field_values([], "level") == []


class TestSummary:
    def test_total(self):
        s = summary(RECORDS)
        assert s["total"] == 5

    def test_fields_includes_all_keys(self):
        s = summary(RECORDS)
        assert "level" in s["fields"]
        assert "msg" in s["fields"]
        assert "code" in s["fields"]

    def test_level_counts(self):
        s = summary(RECORDS)
        assert s["level_counts"]["info"] == 2
        assert s["level_counts"]["error"] == 1

    def test_empty_records(self):
        s = summary([])
        assert s["total"] == 0
        assert s["fields"] == set()
        assert s["level_counts"] == Counter()
