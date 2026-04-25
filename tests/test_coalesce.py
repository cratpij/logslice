"""Tests for logslice.coalesce."""

import pytest
from logslice.coalesce import coalesce_fields, coalesce_records, coalesce_value


# ---------------------------------------------------------------------------
# coalesce_fields
# ---------------------------------------------------------------------------

class TestCoalesceFields:
    def test_picks_first_present_field(self):
        rec = {"a": None, "b": "hello", "c": "world"}
        out = coalesce_fields(rec, ["a", "b", "c"], target="result")
        assert out["result"] == "hello"

    def test_picks_first_field_when_all_present(self):
        rec = {"x": "first", "y": "second"}
        out = coalesce_fields(rec, ["x", "y"], target="out")
        assert out["out"] == "first"

    def test_skips_empty_string_by_default(self):
        rec = {"a": "", "b": "value"}
        out = coalesce_fields(rec, ["a", "b"], target="out")
        assert out["out"] == "value"

    def test_keeps_empty_string_when_skip_empty_false(self):
        rec = {"a": "", "b": "value"}
        out = coalesce_fields(rec, ["a", "b"], target="out", skip_empty=False)
        assert out["out"] == ""

    def test_no_candidate_found_target_absent(self):
        rec = {"a": None, "b": ""}
        out = coalesce_fields(rec, ["a", "b"], target="out")
        assert "out" not in out

    def test_does_not_mutate_original(self):
        rec = {"a": "val"}
        coalesce_fields(rec, ["a"], target="out")
        assert "out" not in rec

    def test_target_overwrites_existing_key(self):
        rec = {"a": "new", "out": "old"}
        out = coalesce_fields(rec, ["a"], target="out")
        assert out["out"] == "new"

    def test_other_fields_preserved(self):
        rec = {"a": "val", "extra": 42}
        out = coalesce_fields(rec, ["a"], target="result")
        assert out["extra"] == 42

    def test_empty_fields_list_returns_copy(self):
        rec = {"a": "val"}
        out = coalesce_fields(rec, [], target="result")
        assert "result" not in out
        assert out["a"] == "val"


# ---------------------------------------------------------------------------
# coalesce_records
# ---------------------------------------------------------------------------

class TestCoalesceRecords:
    def test_applies_to_all_records(self):
        records = [
            {"a": None, "b": "x"},
            {"a": "y", "b": "z"},
        ]
        out = coalesce_records(records, ["a", "b"], target="v")
        assert out[0]["v"] == "x"
        assert out[1]["v"] == "y"

    def test_empty_input(self):
        assert coalesce_records([], ["a"], target="v") == []


# ---------------------------------------------------------------------------
# coalesce_value
# ---------------------------------------------------------------------------

class TestCoalesceValue:
    def test_returns_first_non_none(self):
        rec = {"a": None, "b": 99}
        assert coalesce_value(rec, ["a", "b"]) == 99

    def test_returns_default_when_nothing_found(self):
        rec = {"a": None}
        assert coalesce_value(rec, ["a"], default="fallback") == "fallback"

    def test_default_is_none_when_unspecified(self):
        rec = {}
        assert coalesce_value(rec, ["missing"]) is None

    def test_skips_empty_string(self):
        rec = {"a": "", "b": "ok"}
        assert coalesce_value(rec, ["a", "b"]) == "ok"

    def test_integer_zero_is_not_skipped(self):
        rec = {"a": 0, "b": 1}
        assert coalesce_value(rec, ["a", "b"]) == 0
