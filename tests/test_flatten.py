"""Tests for logslice.flatten."""
import pytest
from logslice.flatten import flatten_record, flatten_records, unflatten_record


class TestFlattenRecord:
    def test_flat_record_unchanged(self):
        rec = {"a": 1, "b": "hello"}
        assert flatten_record(rec) == {"a": 1, "b": "hello"}

    def test_single_level_nesting(self):
        rec = {"a": {"b": 1, "c": 2}}
        assert flatten_record(rec) == {"a.b": 1, "a.c": 2}

    def test_deep_nesting(self):
        rec = {"x": {"y": {"z": 42}}}
        assert flatten_record(rec) == {"x.y.z": 42}

    def test_custom_separator(self):
        rec = {"a": {"b": 1}}
        assert flatten_record(rec, sep="_") == {"a_b": 1}

    def test_does_not_mutate_original(self):
        rec = {"a": {"b": 1}}
        original = {"a": {"b": 1}}
        flatten_record(rec)
        assert rec == original

    def test_non_dict_value_kept(self):
        rec = {"a": [1, 2, 3], "b": None}
        result = flatten_record(rec)
        assert result["a"] == [1, 2, 3]
        assert result["b"] is None

    def test_empty_record(self):
        assert flatten_record({}) == {}

    def test_empty_nested_dict_kept_as_is(self):
        rec = {"a": {}}
        result = flatten_record(rec)
        assert result == {"a": {}}

    def test_max_depth_limits_flattening(self):
        rec = {"a": {"b": {"c": 1}}}
        result = flatten_record(rec, max_depth=1)
        # depth 1 flattens first level only
        assert "a.b" in result
        assert result["a.b"] == {"c": 1}

    def test_mixed_nested_and_flat(self):
        rec = {"ts": "2024-01-01", "ctx": {"user": "alice", "ip": "1.2.3.4"}}
        result = flatten_record(rec)
        assert result["ts"] == "2024-01-01"
        assert result["ctx.user"] == "alice"
        assert result["ctx.ip"] == "1.2.3.4"


class TestFlattenRecords:
    def test_processes_all_records(self):
        records = [{"a": {"b": i}} for i in range(3)]
        result = flatten_records(iter(records))
        assert len(result) == 3
        assert result[0] == {"a.b": 0}

    def test_empty_list(self):
        assert flatten_records(iter([])) == []


class TestUnflattenRecord:
    def test_rebuilds_nested(self):
        flat = {"a.b": 1, "a.c": 2}
        assert unflatten_record(flat) == {"a": {"b": 1, "c": 2}}

    def test_no_sep_unchanged(self):
        flat = {"x": 1, "y": 2}
        assert unflatten_record(flat) == {"x": 1, "y": 2}

    def test_deep_key(self):
        flat = {"x.y.z": 42}
        assert unflatten_record(flat) == {"x": {"y": {"z": 42}}}

    def test_roundtrip(self):
        original = {"level": "info", "ctx": {"user": "bob", "req": {"id": 99}}}
        assert unflatten_record(flatten_record(original)) == original
