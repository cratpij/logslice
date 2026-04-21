"""Tests for logslice.compare."""

import pytest
from logslice.compare import compare_records, compare_streams, changed_only


class TestCompareRecords:
    def test_equal_records_return_empty(self):
        a = {"id": 1, "level": "info"}
        assert compare_records(a, a.copy()) == {}

    def test_detects_changed_value(self):
        diffs = compare_records({"level": "info"}, {"level": "error"})
        assert diffs == {"level": ("info", "error")}

    def test_detects_missing_left_key(self):
        diffs = compare_records({}, {"msg": "hi"})
        assert diffs == {"msg": ("<missing>", "hi")}

    def test_detects_missing_right_key(self):
        diffs = compare_records({"msg": "hi"}, {})
        assert diffs == {"msg": ("hi", "<missing>")}

    def test_field_filter_limits_comparison(self):
        a = {"id": 1, "level": "info", "msg": "hello"}
        b = {"id": 1, "level": "error", "msg": "world"}
        diffs = compare_records(a, b, fields=["id"])
        assert diffs == {}

    def test_does_not_mutate_inputs(self):
        a = {"x": 1}
        b = {"x": 2}
        compare_records(a, b)
        assert a == {"x": 1}
        assert b == {"x": 2}

    def test_none_value_vs_missing(self):
        diffs = compare_records({"k": None}, {})
        assert "k" in diffs


class TestCompareStreams:
    def _left(self):
        return [
            {"id": "1", "level": "info"},
            {"id": "2", "level": "warn"},
        ]

    def _right(self):
        return [
            {"id": "1", "level": "info"},
            {"id": "3", "level": "error"},
        ]

    def test_equal_record_marked_equal(self):
        reports = list(compare_streams(self._left(), self._right(), key_field="id"))
        eq = next(r for r in reports if r["key"] == "1")
        assert eq["status"] == "equal"

    def test_left_only_detected(self):
        reports = list(compare_streams(self._left(), self._right(), key_field="id"))
        lo = next(r for r in reports if r["key"] == "2")
        assert lo["status"] == "left_only"

    def test_right_only_detected(self):
        reports = list(compare_streams(self._left(), self._right(), key_field="id"))
        ro = next(r for r in reports if r["key"] == "3")
        assert ro["status"] == "right_only"

    def test_changed_status_on_diff(self):
        left = [{"id": "1", "level": "info"}]
        right = [{"id": "1", "level": "error"}]
        reports = list(compare_streams(left, right, key_field="id"))
        assert reports[0]["status"] == "changed"
        assert "level" in reports[0]["diffs"]

    def test_empty_streams(self):
        assert list(compare_streams([], [], key_field="id")) == []


class TestChangedOnly:
    def test_filters_equal_records(self):
        reports = [
            {"key": "1", "status": "equal"},
            {"key": "2", "status": "changed", "diffs": {}},
        ]
        result = list(changed_only(iter(reports)))
        assert len(result) == 1
        assert result[0]["key"] == "2"

    def test_empty_input(self):
        assert list(changed_only(iter([]))) == []
