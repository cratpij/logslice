"""Tests for logslice.normalize."""

import pytest
from logslice.normalize import (
    normalize_default,
    normalize_field,
    normalize_records,
    normalize_replace,
    normalize_strip,
    normalize_to_lowercase,
    normalize_to_uppercase,
)


class TestNormalizeField:
    def test_applies_fn_to_field(self):
        record = {"level": "INFO", "msg": "hello"}
        result = normalize_field(record, "level", str.lower)
        assert result["level"] == "info"

    def test_missing_field_unchanged(self):
        record = {"msg": "hello"}
        result = normalize_field(record, "level", str.lower)
        assert result == {"msg": "hello"}

    def test_does_not_mutate_original(self):
        record = {"level": "INFO"}
        normalize_field(record, "level", str.lower)
        assert record["level"] == "INFO"

    def test_other_fields_preserved(self):
        record = {"level": "INFO", "msg": "hello", "ts": "2024-01-01"}
        result = normalize_field(record, "level", str.lower)
        assert result["msg"] == "hello"
        assert result["ts"] == "2024-01-01"


class TestNormalizeToLowercase:
    def test_lowercases_string(self):
        result = normalize_to_lowercase({"level": "ERROR"}, "level")
        assert result["level"] == "error"

    def test_non_string_unchanged(self):
        result = normalize_to_lowercase({"code": 404}, "code")
        assert result["code"] == 404

    def test_missing_field_unchanged(self):
        result = normalize_to_lowercase({"msg": "hi"}, "level")
        assert "level" not in result


class TestNormalizeToUppercase:
    def test_uppercases_string(self):
        result = normalize_to_uppercase({"env": "production"}, "env")
        assert result["env"] == "PRODUCTION"


class TestNormalizeStrip:
    def test_strips_whitespace(self):
        result = normalize_strip({"msg": "  hello  "}, "msg")
        assert result["msg"] == "hello"

    def test_non_string_unchanged(self):
        result = normalize_strip({"count": 5}, "count")
        assert result["count"] == 5


class TestNormalizeReplace:
    def test_replaces_substring(self):
        result = normalize_replace({"path": "/foo/bar"}, "path", "/", "-")
        assert result["path"] == "-foo-bar"

    def test_no_match_unchanged(self):
        result = normalize_replace({"msg": "hello"}, "msg", "x", "y")
        assert result["msg"] == "hello"

    def test_non_string_unchanged(self):
        result = normalize_replace({"n": 42}, "n", "4", "5")
        assert result["n"] == 42


class TestNormalizeDefault:
    def test_sets_default_for_missing_field(self):
        result = normalize_default({"msg": "hi"}, "level", "INFO")
        assert result["level"] == "INFO"

    def test_sets_default_for_none_value(self):
        result = normalize_default({"level": None}, "level", "INFO")
        assert result["level"] == "INFO"

    def test_existing_value_not_overwritten(self):
        result = normalize_default({"level": "ERROR"}, "level", "INFO")
        assert result["level"] == "ERROR"


class TestNormalizeRecords:
    def test_applies_to_all_records(self):
        records = [{"level": "INFO"}, {"level": "ERROR"}, {"level": "WARN"}]
        result = normalize_records(records, "level", str.lower)
        assert [r["level"] for r in result] == ["info", "error", "warn"]

    def test_empty_input(self):
        assert normalize_records([], "level", str.lower) == []

    def test_returns_new_list(self):
        records = [{"level": "INFO"}]
        result = normalize_records(records, "level", str.lower)
        assert result is not records
