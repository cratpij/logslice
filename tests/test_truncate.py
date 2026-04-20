"""Tests for logslice.truncate."""

import pytest
from logslice.truncate import (
    truncate_field,
    truncate_fields,
    truncate_all,
    truncate_records,
)


class TestTruncateField:
    def test_truncates_long_string(self):
        rec = {"msg": "hello world"}
        result = truncate_field(rec, "msg", 7)
        assert result["msg"] == "hell..."

    def test_short_string_unchanged(self):
        rec = {"msg": "hi"}
        result = truncate_field(rec, "msg", 10)
        assert result["msg"] == "hi"

    def test_exact_length_unchanged(self):
        rec = {"msg": "hello"}
        result = truncate_field(rec, "msg", 5)
        assert result["msg"] == "hello"

    def test_missing_field_unchanged(self):
        rec = {"level": "info"}
        result = truncate_field(rec, "msg", 5)
        assert "msg" not in result
        assert result["level"] == "info"

    def test_non_string_field_unchanged(self):
        rec = {"count": 12345678}
        result = truncate_field(rec, "count", 3)
        assert result["count"] == 12345678

    def test_does_not_mutate_original(self):
        rec = {"msg": "hello world"}
        truncate_field(rec, "msg", 5)
        assert rec["msg"] == "hello world"

    def test_custom_suffix(self):
        rec = {"msg": "hello world"}
        result = truncate_field(rec, "msg", 7, suffix=">>")
        assert result["msg"] == "hello>>"

    def test_max_length_shorter_than_suffix(self):
        rec = {"msg": "hello world"}
        result = truncate_field(rec, "msg", 2)
        assert result["msg"] == "..."


class TestTruncateFields:
    def test_truncates_multiple_fields(self):
        rec = {"a": "long value here", "b": "another long value"}
        result = truncate_fields(rec, ["a", "b"], 8)
        assert result["a"] == "long ..."
        assert result["b"] == "anoth..."

    def test_skips_missing_fields(self):
        rec = {"a": "hello"}
        result = truncate_fields(rec, ["a", "b"], 3)
        assert result["a"] == "..."
        assert "b" not in result


class TestTruncateAll:
    def test_truncates_all_string_fields(self):
        rec = {"msg": "hello world", "src": "my_module"}
        result = truncate_all(rec, 6)
        assert result["msg"] == "hel..."
        assert result["src"] == "my_..."

    def test_skips_specified_fields(self):
        rec = {"msg": "hello world", "level": "information"}
        result = truncate_all(rec, 5, skip=["level"])
        assert result["msg"] == "he..."
        assert result["level"] == "information"

    def test_non_string_fields_untouched(self):
        rec = {"msg": "hello world", "count": 999}
        result = truncate_all(rec, 5)
        assert result["count"] == 999


class TestTruncateRecords:
    def test_applies_to_all_records(self):
        records = [{"msg": "hello world"}, {"msg": "another long message"}]
        result = truncate_records(records, "msg", 8)
        assert result[0]["msg"] == "hello..."
        assert result[1]["msg"] == "anoth..."

    def test_empty_input(self):
        assert truncate_records([], "msg", 10) == []
