"""Tests for logslice/segment.py."""

import pytest
from logslice.segment import (
    segment_by_field,
    segment_by_predicate,
    segment_counts,
    split_segments,
)


def _r(**kw):
    return dict(kw)


BOUNDARIES = [("100", "low"), ("500", "mid"), ("1000", "high")]


class TestSegmentByField:
    def test_assigns_correct_label(self):
        records = [_r(val="600")]
        result = list(segment_by_field(records, "val", BOUNDARIES))
        assert result[0]["_segment"] == "mid"

    def test_below_all_boundaries_uses_default(self):
        records = [_r(val="50")]
        result = list(segment_by_field(records, "val", BOUNDARIES))
        assert result[0]["_segment"] == "other"

    def test_custom_default_label(self):
        records = [_r(val="10")]
        result = list(segment_by_field(records, "val", BOUNDARIES, default="tiny"))
        assert result[0]["_segment"] == "tiny"

    def test_highest_boundary_met(self):
        records = [_r(val="9999")]
        result = list(segment_by_field(records, "val", BOUNDARIES))
        assert result[0]["_segment"] == "high"

    def test_missing_field_uses_default(self):
        records = [_r(other="x")]
        result = list(segment_by_field(records, "val", BOUNDARIES))
        assert result[0]["_segment"] == "other"

    def test_does_not_mutate_original(self):
        original = _r(val="200")
        list(segment_by_field([original], "val", BOUNDARIES))
        assert "_segment" not in original

    def test_empty_input_returns_empty(self):
        result = list(segment_by_field([], "val", BOUNDARIES))
        assert result == []

    def test_original_fields_preserved(self):
        records = [_r(val="200", msg="hello")]
        result = list(segment_by_field(records, "val", BOUNDARIES))
        assert result[0]["msg"] == "hello"


class TestSegmentByPredicate:
    def test_first_matching_predicate_wins(self):
        predicates = [
            (lambda r: r.get("level") == "error", "critical"),
            (lambda r: r.get("level") == "warn", "warning"),
        ]
        records = [_r(level="warn")]
        result = list(segment_by_predicate(records, predicates))
        assert result[0]["_segment"] == "warning"

    def test_no_match_uses_default(self):
        predicates = [(lambda r: False, "never")]
        records = [_r(level="info")]
        result = list(segment_by_predicate(records, predicates))
        assert result[0]["_segment"] == "other"

    def test_empty_predicates_all_default(self):
        records = [_r(x="1"), _r(x="2")]
        result = list(segment_by_predicate(records, []))
        assert all(r["_segment"] == "other" for r in result)


class TestSegmentCounts:
    def test_counts_per_segment(self):
        records = [
            {"_segment": "low"},
            {"_segment": "low"},
            {"_segment": "high"},
        ]
        counts = segment_counts(records)
        assert counts == {"low": 2, "high": 1}

    def test_missing_segment_field(self):
        records = [{"x": 1}]
        counts = segment_counts(records)
        assert "__missing__" in counts


class TestSplitSegments:
    def test_partitions_correctly(self):
        records = [
            {"_segment": "a", "v": 1},
            {"_segment": "b", "v": 2},
            {"_segment": "a", "v": 3},
        ]
        result = split_segments(records)
        assert len(result["a"]) == 2
        assert len(result["b"]) == 1

    def test_empty_input_returns_empty_dict(self):
        assert split_segments([]) == {}
