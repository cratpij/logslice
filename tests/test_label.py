"""Tests for logslice.label."""

import pytest
from logslice.label import (
    label_by_condition,
    label_by_range,
    label_by_value,
    label_records,
)


RECORD = {"level": "error", "latency": 250, "status": 500}


class TestLabelByCondition:
    def test_first_matching_label_used(self):
        conditions = [
            ("high", lambda r: r.get("latency", 0) > 200),
            ("low", lambda r: r.get("latency", 0) <= 200),
        ]
        result = label_by_condition(RECORD, conditions)
        assert result["label"] == "high"

    def test_second_condition_matches(self):
        conditions = [
            ("critical", lambda r: r.get("status") == 503),
            ("error", lambda r: r.get("status") == 500),
        ]
        result = label_by_condition(RECORD, conditions)
        assert result["label"] == "error"

    def test_no_match_returns_default(self):
        result = label_by_condition(RECORD, [], default="unknown")
        assert result["label"] == "unknown"

    def test_no_match_no_default_omits_field(self):
        result = label_by_condition(RECORD, [])
        assert "label" not in result

    def test_does_not_mutate_original(self):
        original = {"x": 1}
        conditions = [("yes", lambda r: True)]
        label_by_condition(original, conditions)
        assert "label" not in original

    def test_custom_field_name(self):
        conditions = [("ok", lambda r: True)]
        result = label_by_condition(RECORD, conditions, field="category")
        assert result["category"] == "ok"
        assert "label" not in result

    def test_predicate_exception_skips_condition(self):
        def bad(r):
            raise ValueError("boom")

        conditions = [("bad", bad), ("good", lambda r: True)]
        result = label_by_condition(RECORD, conditions)
        assert result["label"] == "good"


class TestLabelByRange:
    def test_value_in_range(self):
        ranges = [(0, 100, "low"), (100, 300, "medium"), (300, 1000, "high")]
        result = label_by_range(RECORD, "latency", ranges)
        assert result["label"] == "medium"

    def test_value_at_lower_boundary(self):
        ranges = [(100, 300, "medium")]
        result = label_by_range({"latency": 100}, "latency", ranges)
        assert result["label"] == "medium"

    def test_value_at_upper_boundary_excluded(self):
        ranges = [(100, 300, "medium"), (300, 1000, "high")]
        result = label_by_range({"latency": 300}, "latency", ranges)
        assert result["label"] == "high"

    def test_no_range_match_uses_default(self):
        result = label_by_range({"latency": 9999}, "latency", [], default="other")
        assert result["label"] == "other"

    def test_non_numeric_field_uses_default(self):
        result = label_by_range({"latency": "fast"}, "latency", [], default="unknown")
        assert result["label"] == "unknown"

    def test_missing_field_uses_default(self):
        result = label_by_range({}, "latency", [(0, 100, "low")], default="n/a")
        assert result["label"] == "n/a"


class TestLabelByValue:
    def test_exact_match(self):
        mapping = {"error": "bad", "info": "ok"}
        result = label_by_value(RECORD, "level", mapping)
        assert result["label"] == "bad"

    def test_no_match_uses_default(self):
        result = label_by_value({"level": "debug"}, "level", {}, default="other")
        assert result["label"] == "other"

    def test_no_match_no_default_omits_field(self):
        result = label_by_value({"level": "debug"}, "level", {})
        assert "label" not in result


class TestLabelRecords:
    def test_applies_to_all_records(self):
        records = [{"v": 1}, {"v": 2}, {"v": 3}]
        conditions = [("odd", lambda r: r["v"] % 2 != 0), ("even", lambda r: r["v"] % 2 == 0)]
        results = label_records(records, conditions)
        assert [r["label"] for r in results] == ["odd", "even", "odd"]

    def test_empty_input(self):
        assert label_records([], []) == []
