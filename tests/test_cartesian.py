"""Tests for logslice.cartesian."""

import pytest
from logslice.cartesian import cartesian_product, cartesian_with_lookup, dedup_cartesian


LEFT = [{"id": 1, "color": "red"}, {"id": 2, "color": "blue"}]
RIGHT = [{"size": "S"}, {"size": "M"}]


class TestCartesianProduct:
    def test_correct_count(self):
        result = cartesian_product(LEFT, RIGHT)
        assert len(result) == 4

    def test_keys_merged(self):
        result = cartesian_product(LEFT, RIGHT)
        for row in result:
            assert "id" in row
            assert "color" in row
            assert "size" in row

    def test_prefix_left(self):
        result = cartesian_product(LEFT, RIGHT, prefix_left="l")
        assert all("l_id" in row and "l_color" in row for row in result)

    def test_prefix_right(self):
        result = cartesian_product(LEFT, RIGHT, prefix_right="r")
        assert all("r_size" in row for row in result)

    def test_both_prefixes(self):
        result = cartesian_product(LEFT, RIGHT, prefix_left="l", prefix_right="r")
        assert result[0] == {"l_id": 1, "l_color": "red", "r_size": "S"}

    def test_empty_left(self):
        assert cartesian_product([], RIGHT) == []

    def test_empty_right(self):
        assert cartesian_product(LEFT, []) == []

    def test_does_not_mutate_inputs(self):
        left_copy = [{"a": 1}]
        right_copy = [{"b": 2}]
        cartesian_product(left_copy, right_copy, prefix_left="l", prefix_right="r")
        assert left_copy == [{"a": 1}]
        assert right_copy == [{"b": 2}]


class TestCartesianWithLookup:
    def test_no_join_field_cross_joins_all(self):
        records = [{"host": "a"}, {"host": "b"}]
        lookup = [{"env": "prod"}, {"env": "staging"}]
        result = cartesian_with_lookup(records, lookup)
        assert len(result) == 4

    def test_join_field_filters_matches(self):
        records = [{"region": "us"}, {"region": "eu"}]
        lookup = [{"region": "us", "dc": "us-east"}, {"region": "eu", "dc": "eu-west"}]
        result = cartesian_with_lookup(records, lookup, join_field="region")
        assert len(result) == 2
        assert result[0]["dc"] == "us-east"
        assert result[1]["dc"] == "eu-west"

    def test_no_match_returns_empty(self):
        records = [{"region": "ap"}]
        lookup = [{"region": "us", "dc": "us-east"}]
        result = cartesian_with_lookup(records, lookup, join_field="region")
        assert result == []

    def test_right_fields_overwrite_left_on_conflict(self):
        records = [{"env": "dev", "host": "h1"}]
        lookup = [{"env": "prod"}]
        result = cartesian_with_lookup(records, lookup)
        assert result[0]["env"] == "prod"


class TestDedupCartesian:
    def test_removes_duplicate_key_combos(self):
        pairs = [
            {"a": 1, "b": 2},
            {"a": 1, "b": 2},
            {"a": 1, "b": 3},
        ]
        result = dedup_cartesian(pairs, key_fields=["a", "b"])
        assert len(result) == 2

    def test_keeps_first_occurrence(self):
        pairs = [
            {"a": 1, "extra": "first"},
            {"a": 1, "extra": "second"},
        ]
        result = dedup_cartesian(pairs, key_fields=["a"])
        assert result[0]["extra"] == "first"

    def test_empty_input(self):
        assert dedup_cartesian([], key_fields=["a"]) == []
