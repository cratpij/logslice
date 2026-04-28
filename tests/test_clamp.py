"""Tests for logslice.clamp."""

import pytest
from logslice.clamp import clamp_field, clamp_fields, clamp_records


class TestClampField:
    def test_value_below_min_raised_to_min(self):
        rec = {"x": 3}
        assert clamp_field(rec, "x", min_val=5)["x"] == 5

    def test_value_above_max_lowered_to_max(self):
        rec = {"x": 20}
        assert clamp_field(rec, "x", max_val=10)["x"] == 10

    def test_value_within_range_unchanged(self):
        rec = {"x": 7}
        assert clamp_field(rec, "x", min_val=0, max_val=10)["x"] == 7

    def test_value_at_min_boundary_unchanged(self):
        rec = {"x": 0}
        assert clamp_field(rec, "x", min_val=0, max_val=10)["x"] == 0

    def test_value_at_max_boundary_unchanged(self):
        rec = {"x": 10}
        assert clamp_field(rec, "x", min_val=0, max_val=10)["x"] == 10

    def test_float_value_clamped(self):
        rec = {"temp": 105.7}
        result = clamp_field(rec, "temp", max_val=100.0)
        assert result["temp"] == 100.0

    def test_string_numeric_clamped(self):
        rec = {"score": "150"}
        result = clamp_field(rec, "score", max_val=100)
        assert result["score"] == 100

    def test_non_numeric_string_unchanged(self):
        rec = {"level": "high"}
        assert clamp_field(rec, "level", min_val=0, max_val=10)["level"] == "high"

    def test_missing_field_unchanged(self):
        rec = {"a": 1}
        result = clamp_field(rec, "missing", min_val=0, max_val=10)
        assert result == {"a": 1}

    def test_does_not_mutate_original(self):
        rec = {"x": 200}
        clamp_field(rec, "x", max_val=100)
        assert rec["x"] == 200

    def test_preserves_int_type_when_clamped(self):
        rec = {"x": 50}
        result = clamp_field(rec, "x", min_val=10, max_val=100)
        assert isinstance(result["x"], int)

    def test_no_bounds_returns_unchanged(self):
        rec = {"x": 999}
        assert clamp_field(rec, "x")["x"] == 999

    def test_other_fields_preserved(self):
        rec = {"x": 5, "label": "ok"}
        result = clamp_field(rec, "x", min_val=0, max_val=10)
        assert result["label"] == "ok"


class TestClampFields:
    def test_clamps_multiple_fields(self):
        rec = {"a": -5, "b": 200, "c": 50}
        result = clamp_fields(rec, ["a", "b"], min_val=0, max_val=100)
        assert result["a"] == 0
        assert result["b"] == 100
        assert result["c"] == 50

    def test_empty_field_list_unchanged(self):
        rec = {"x": -99}
        assert clamp_fields(rec, [], min_val=0)["x"] == -99


class TestClampRecords:
    def test_clamps_across_all_records(self):
        records = [{"v": i * 10} for i in range(6)]
        results = list(clamp_records(records, ["v"], min_val=10, max_val=40))
        assert [r["v"] for r in results] == [10, 10, 20, 30, 40, 40]

    def test_empty_input_returns_empty(self):
        assert list(clamp_records([], ["v"], min_val=0, max_val=10)) == []

    def test_returns_iterator(self):
        records = [{"v": 5}]
        result = clamp_records(records, ["v"], max_val=3)
        import types
        assert isinstance(result, types.GeneratorType)
