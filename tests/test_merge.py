"""Tests for logslice.merge."""

import pytest
from logslice.merge import merge_records, merge_sorted, merge_dedupe


A = [
    {"id": 1, "timestamp": "2024-01-01T10:00:00Z", "msg": "a1"},
    {"id": 2, "timestamp": "2024-01-01T12:00:00Z", "msg": "a2"},
]

B = [
    {"id": 3, "timestamp": "2024-01-01T11:00:00Z", "msg": "b1"},
    {"id": 4, "timestamp": "2024-01-01T13:00:00Z", "msg": "b2"},
]

C = [
    {"id": 5, "msg": "no-ts"},
]


class TestMergeRecords:
    def test_combines_two_streams(self):
        result = merge_records(A, B)
        assert len(result) == 4

    def test_preserves_order(self):
        result = merge_records(A, B)
        assert result[0]["id"] == 1
        assert result[2]["id"] == 3

    def test_empty_stream(self):
        result = merge_records([], A)
        assert result == A

    def test_all_empty(self):
        assert merge_records([], []) == []

    def test_single_stream(self):
        result = merge_records(A)
        assert result == A


class TestMergeSorted:
    def test_sorted_by_timestamp(self):
        result = merge_sorted(A, B)
        ids = [r["id"] for r in result]
        assert ids == [1, 3, 2, 4]

    def test_missing_timestamp_appended_last(self):
        result = merge_sorted(A, C)
        assert result[-1]["id"] == 5

    def test_empty_streams(self):
        assert merge_sorted([], []) == []

    def test_single_record(self):
        result = merge_sorted([{"timestamp": "2024-01-01T09:00:00Z", "id": 0}], A)
        assert result[0]["id"] == 0

    def test_custom_timestamp_field(self):
        s1 = [{"ts": "2024-01-01T10:00:00Z", "v": 1}]
        s2 = [{"ts": "2024-01-01T09:00:00Z", "v": 2}]
        result = merge_sorted(s1, s2, timestamp_field="ts")
        assert result[0]["v"] == 2


class TestMergeDedupe:
    def test_removes_duplicate_keys(self):
        s1 = [{"id": "x", "v": 1}]
        s2 = [{"id": "x", "v": 2}]
        result = merge_dedupe(s1, s2, key_field="id")
        assert len(result) == 1
        assert result[0]["v"] == 1

    def test_keeps_unique_keys(self):
        result = merge_dedupe(A, B, key_field="id")
        assert len(result) == 4

    def test_missing_key_always_included(self):
        s1 = [{"msg": "no-id"}, {"msg": "also-no-id"}]
        result = merge_dedupe(s1, key_field="id")
        assert len(result) == 2

    def test_empty_input(self):
        assert merge_dedupe([], key_field="id") == []
