"""Tests for logslice.enrich."""

import pytest
from logslice.enrich import (
    enrich_with_derived,
    enrich_with_constant,
    enrich_with_hour,
    enrich_with_date,
)


RECORDS = [
    {"timestamp": "2024-03-15T08:30:00Z", "level": "info", "msg": "started"},
    {"timestamp": "2024-03-15T14:05:22Z", "level": "error", "msg": "failed"},
    {"timestamp": "2024-03-16T23:59:00Z", "level": "warn", "msg": "slow"},
]


class TestEnrichWithDerived:
    def test_adds_new_field(self):
        result = enrich_with_derived(RECORDS, "upper_level", lambda r: r["level"].upper())
        assert result[0]["upper_level"] == "INFO"
        assert result[1]["upper_level"] == "ERROR"

    def test_does_not_mutate_original(self):
        original = [{"a": 1}]
        enrich_with_derived(original, "b", lambda r: 2)
        assert "b" not in original[0]

    def test_empty_input(self):
        assert enrich_with_derived([], "x", lambda r: 1) == []

    def test_all_records_processed(self):
        result = enrich_with_derived(RECORDS, "n", lambda r: 42)
        assert all(r["n"] == 42 for r in result)


class TestEnrichWithConstant:
    def test_sets_missing_field(self):
        records = [{"a": 1}, {"a": 2}]
        result = enrich_with_constant(records, "env", "prod")
        assert all(r["env"] == "prod" for r in result)

    def test_does_not_overwrite_existing(self):
        records = [{"env": "dev"}, {"a": 1}]
        result = enrich_with_constant(records, "env", "prod")
        assert result[0]["env"] == "dev"
        assert result[1]["env"] == "prod"

    def test_empty_input(self):
        assert enrich_with_constant([], "x", "v") == []


class TestEnrichWithHour:
    def test_extracts_hour(self):
        result = enrich_with_hour(RECORDS)
        assert result[0]["hour"] == 8
        assert result[1]["hour"] == 14
        assert result[2]["hour"] == 23

    def test_missing_timestamp_no_hour(self):
        records = [{"msg": "no ts"}]
        result = enrich_with_hour(records)
        assert "hour" not in result[0]

    def test_custom_fields(self):
        records = [{"ts": "2024-01-01T06:00:00Z"}]
        result = enrich_with_hour(records, ts_field="ts", out_field="h")
        assert result[0]["h"] == 6


class TestEnrichWithDate:
    def test_extracts_date(self):
        result = enrich_with_date(RECORDS)
        assert result[0]["date"] == "2024-03-15"
        assert result[2]["date"] == "2024-03-16"

    def test_missing_timestamp_no_date(self):
        records = [{"msg": "no ts"}]
        result = enrich_with_date(records)
        assert "date" not in result[0]

    def test_custom_fields(self):
        records = [{"ts": "2024-06-20T00:00:00Z"}]
        result = enrich_with_date(records, ts_field="ts", out_field="day")
        assert result[0]["day"] == "2024-06-20"
