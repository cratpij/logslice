"""Tests for logslice.split."""

import pytest
from logslice.split import (
    split_by_field,
    split_by_predicate,
    split_by_value_set,
    split_into_chunks,
)


RECORDS = [
    {"level": "info", "msg": "a"},
    {"level": "error", "msg": "b"},
    {"level": "info", "msg": "c"},
    {"level": "warn", "msg": "d"},
    {"msg": "e"},  # missing 'level'
]


class TestSplitByField:
    def test_groups_by_field_value(self):
        result = split_by_field(RECORDS, "level")
        assert len(result["info"]) == 2
        assert len(result["error"]) == 1
        assert len(result["warn"]) == 1

    def test_missing_field_goes_to_default_key(self):
        result = split_by_field(RECORDS, "level")
        assert result["__missing__"] == [{"msg": "e"}]

    def test_custom_missing_key(self):
        result = split_by_field(RECORDS, "level", missing_key="unknown")
        assert "unknown" in result
        assert "__missing__" not in result

    def test_empty_input_returns_empty_dict(self):
        assert split_by_field([], "level") == {}

    def test_does_not_mutate_records(self):
        originals = [{"level": "info", "x": 1}]
        split_by_field(originals, "level")
        assert originals[0] == {"level": "info", "x": 1}


class TestSplitByPredicate:
    def _is_error(self, r):
        return r.get("level") == "error"

    def test_true_bucket_contains_matches(self):
        result = split_by_predicate(RECORDS, self._is_error)
        assert all(r["level"] == "error" for r in result["match"])

    def test_false_bucket_contains_non_matches(self):
        result = split_by_predicate(RECORDS, self._is_error)
        assert len(result["no_match"]) == len(RECORDS) - 1

    def test_custom_bucket_names(self):
        result = split_by_predicate(RECORDS, self._is_error, true_key="yes", false_key="no")
        assert "yes" in result and "no" in result

    def test_empty_input(self):
        result = split_by_predicate([], self._is_error)
        assert result == {"match": [], "no_match": []}


class TestSplitByValueSet:
    def test_known_values_bucketed(self):
        result = split_by_value_set(RECORDS, "level", ["info", "error"])
        assert len(result["info"]) == 2
        assert len(result["error"]) == 1

    def test_unmatched_go_to_other(self):
        result = split_by_value_set(RECORDS, "level", ["info"])
        assert len(result["__other__"]) == 3  # error, warn, missing

    def test_other_key_none_discards_unmatched(self):
        result = split_by_value_set(RECORDS, "level", ["info"], other_key=None)
        assert "__other__" not in result
        assert len(result["info"]) == 2

    def test_empty_input(self):
        result = split_by_value_set([], "level", ["info"])
        assert result["info"] == []


class TestSplitIntoChunks:
    def test_even_split(self):
        records = [{"i": i} for i in range(6)]
        chunks = split_into_chunks(records, 2)
        assert len(chunks) == 3
        assert all(len(c) == 2 for c in chunks)

    def test_remainder_chunk(self):
        records = [{"i": i} for i in range(5)]
        chunks = split_into_chunks(records, 2)
        assert len(chunks) == 3
        assert len(chunks[-1]) == 1

    def test_chunk_larger_than_input(self):
        records = [{"i": 0}]
        chunks = split_into_chunks(records, 100)
        assert chunks == [[{"i": 0}]]

    def test_empty_input_returns_empty_list(self):
        assert split_into_chunks([], 5) == []

    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            split_into_chunks([{"x": 1}], 0)
