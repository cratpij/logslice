"""Tests for logslice.jmespath_filter."""

import pytest

from logslice.jmespath_filter import (
    compile_expression,
    evaluate,
    extract_field,
    filter_by_expression,
    project,
)


RECORDS = [
    {"level": "error", "msg": "disk full", "code": 500},
    {"level": "info",  "msg": "started",   "code": 200},
    {"level": "warn",  "msg": "low memory", "code": 300},
    {"level": "error", "msg": "timeout",    "code": 503},
]


class TestCompileExpression:
    def test_valid_expression_returns_object(self):
        expr = compile_expression("level")
        assert expr is not None

    def test_invalid_expression_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid JMESPath"):
            compile_expression("[invalid")


class TestEvaluate:
    def test_simple_field(self):
        assert evaluate({"level": "error"}, "level") == "error"

    def test_nested_field(self):
        record = {"meta": {"host": "web-01"}}
        assert evaluate(record, "meta.host") == "web-01"

    def test_missing_field_returns_none(self):
        assert evaluate({"level": "info"}, "missing") is None

    def test_condition_expression(self):
        record = {"code": 500}
        result = evaluate(record, "code")
        assert result == 500


class TestFilterByExpression:
    def test_filters_by_simple_condition(self):
        results = list(filter_by_expression(RECORDS, "level == 'error'"))
        assert len(results) == 2
        assert all(r["level"] == "error" for r in results)

    def test_empty_input_returns_empty(self):
        assert list(filter_by_expression([], "level")) == []

    def test_no_match_returns_empty(self):
        results = list(filter_by_expression(RECORDS, "level == 'debug'"))
        assert results == []

    def test_all_match_returns_all(self):
        results = list(filter_by_expression(RECORDS, "level"))
        assert len(results) == len(RECORDS)


class TestExtractField:
    def test_adds_extracted_field(self):
        records = [{"meta": {"host": "web-01"}, "level": "info"}]
        results = list(extract_field(records, "meta.host", "host"))
        assert results[0]["host"] == "web-01"

    def test_does_not_mutate_original(self):
        original = {"meta": {"host": "web-01"}}
        list(extract_field([original], "meta.host", "host"))
        assert "host" not in original

    def test_overwrite_false_preserves_existing(self):
        records = [{"host": "old", "meta": {"host": "new"}}]
        results = list(extract_field(records, "meta.host", "host", overwrite=False))
        assert results[0]["host"] == "old"

    def test_none_result_passes_record_through(self):
        records = [{"level": "info"}]
        results = list(extract_field(records, "missing", "dest"))
        assert "dest" not in results[0]


class TestProject:
    def test_builds_new_record_from_expressions(self):
        records = [{"level": "error", "code": 500, "msg": "oops"}]
        results = list(project(records, {"severity": "level", "status": "code"}))
        assert results[0] == {"severity": "error", "status": 500}

    def test_omits_none_values(self):
        records = [{"level": "info"}]
        results = list(project(records, {"level": "level", "host": "host"}))
        assert "host" not in results[0]

    def test_empty_input_returns_empty(self):
        assert list(project([], {"level": "level"})) == []
