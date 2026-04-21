"""Tests for logslice.annotate."""

import pytest
from logslice.annotate import (
    annotate_with_label,
    annotate_with_fn,
    annotate_with_index,
    annotate_conditional,
)


RECORDS = [
    {"msg": "hello", "level": "info"},
    {"msg": "world", "level": "error"},
]


class TestAnnotateWithLabel:
    def test_adds_static_field(self):
        out = annotate_with_label(RECORDS, "env", "prod")
        assert all(r["env"] == "prod" for r in out)

    def test_does_not_mutate_original(self):
        annotate_with_label(RECORDS, "env", "prod")
        assert "env" not in RECORDS[0]

    def test_empty_input(self):
        assert annotate_with_label([], "env", "prod") == []

    def test_overwrites_existing_field(self):
        records = [{"level": "info"}]
        out = annotate_with_label(records, "level", "debug")
        assert out[0]["level"] == "debug"


class TestAnnotateWithFn:
    def test_derived_field(self):
        out = annotate_with_fn(RECORDS, "upper_msg", lambda r: r["msg"].upper())
        assert out[0]["upper_msg"] == "HELLO"
        assert out[1]["upper_msg"] == "WORLD"

    def test_does_not_mutate_original(self):
        annotate_with_fn(RECORDS, "x", lambda r: 1)
        assert "x" not in RECORDS[0]

    def test_empty_input(self):
        assert annotate_with_fn([], "x", lambda r: 1) == []


class TestAnnotateWithIndex:
    def test_default_start(self):
        out = annotate_with_index(RECORDS)
        assert out[0]["_index"] == 0
        assert out[1]["_index"] == 1

    def test_custom_start(self):
        out = annotate_with_index(RECORDS, start=10)
        assert out[0]["_index"] == 10

    def test_custom_field_name(self):
        out = annotate_with_index(RECORDS, field="seq")
        assert "seq" in out[0]

    def test_empty_input(self):
        assert annotate_with_index([]) == []


class TestAnnotateConditional:
    def test_true_branch(self):
        out = annotate_conditional(
            RECORDS, "is_error", lambda r: r["level"] == "error", True, False
        )
        assert out[0]["is_error"] is False
        assert out[1]["is_error"] is True

    def test_default_false_value_is_none(self):
        out = annotate_conditional(
            RECORDS, "flag", lambda r: r["level"] == "info", "yes"
        )
        assert out[0]["flag"] == "yes"
        assert out[1]["flag"] is None

    def test_empty_input(self):
        assert annotate_conditional([], "f", lambda r: True, 1) == []
