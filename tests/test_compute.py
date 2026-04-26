"""Tests for logslice.compute."""

import pytest
from logslice.compute import (
    compute_field,
    compute_sum,
    compute_ratio,
    compute_concat,
    compute_records,
)


class TestComputeField:
    def test_adds_new_field(self):
        r = {"a": 2, "b": 3}
        out = compute_field(r, "c", lambda rec: rec["a"] + rec["b"])
        assert out["c"] == 5

    def test_does_not_mutate_original(self):
        r = {"a": 1}
        compute_field(r, "x", lambda rec: 99)
        assert "x" not in r

    def test_overwrite_true_replaces_existing(self):
        r = {"a": 1, "result": 0}
        out = compute_field(r, "result", lambda rec: 42)
        assert out["result"] == 42

    def test_overwrite_false_keeps_existing(self):
        r = {"a": 1, "result": 7}
        out = compute_field(r, "result", lambda rec: 42, overwrite=False)
        assert out["result"] == 7

    def test_key_error_stores_none(self):
        r = {"a": 1}
        out = compute_field(r, "c", lambda rec: rec["missing"])
        assert out["c"] is None

    def test_zero_division_stores_none(self):
        r = {"a": 1}
        out = compute_field(r, "c", lambda rec: 1 / 0)
        assert out["c"] is None


class TestComputeSum:
    def test_sums_present_fields(self):
        r = {"x": 3, "y": 4, "z": 5}
        out = compute_sum(r, "total", ["x", "y", "z"])
        assert out["total"] == 12.0

    def test_skips_missing_fields(self):
        r = {"x": 10}
        out = compute_sum(r, "total", ["x", "missing"])
        assert out["total"] == 10.0

    def test_all_missing_returns_none(self):
        r = {"a": 1}
        out = compute_sum(r, "total", ["x", "y"])
        assert out["total"] is None


class TestComputeRatio:
    def test_computes_ratio(self):
        r = {"hits": 10, "total": 100}
        out = compute_ratio(r, "rate", "hits", "total")
        assert out["rate"] == pytest.approx(0.1)

    def test_zero_denominator_gives_none(self):
        r = {"hits": 5, "total": 0}
        out = compute_ratio(r, "rate", "hits", "total")
        assert out["rate"] is None

    def test_missing_field_gives_none(self):
        r = {"hits": 5}
        out = compute_ratio(r, "rate", "hits", "total")
        assert out["rate"] is None


class TestComputeConcat:
    def test_concatenates_with_default_sep(self):
        r = {"first": "hello", "second": "world"}
        out = compute_concat(r, "msg", ["first", "second"])
        assert out["msg"] == "hello world"

    def test_custom_separator(self):
        r = {"a": "foo", "b": "bar"}
        out = compute_concat(r, "out", ["a", "b"], sep="-")
        assert out["out"] == "foo-bar"

    def test_missing_fields_skipped(self):
        r = {"a": "only"}
        out = compute_concat(r, "out", ["a", "missing"])
        assert out["out"] == "only"


def test_compute_records_applies_to_all():
    records = [{"v": i} for i in range(4)]
    out = compute_records(records, "doubled", lambda r: r["v"] * 2)
    assert [o["doubled"] for o in out] == [0, 2, 4, 6]


def test_compute_records_empty_input():
    assert compute_records([], "x", lambda r: 1) == []
