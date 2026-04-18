import pytest
from logslice.diff import diff_by_field, diff_field_values, count_diff

LEFT = [
    {"id": "1", "level": "info", "msg": "start"},
    {"id": "2", "level": "warn", "msg": "slow"},
    {"id": "3", "level": "error", "msg": "fail"},
]
RIGHT = [
    {"id": "2", "level": "info", "msg": "slow"},
    {"id": "3", "level": "error", "msg": "fail"},
    {"id": "4", "level": "debug", "msg": "trace"},
]


class TestDiffByField:
    def test_only_left(self):
        r = diff_by_field(LEFT, RIGHT, "id")
        assert [x["id"] for x in r["only_left"]] == ["1"]

    def test_only_right(self):
        r = diff_by_field(LEFT, RIGHT, "id")
        assert [x["id"] for x in r["only_right"]] == ["4"]

    def test_in_both(self):
        r = diff_by_field(LEFT, RIGHT, "id")
        assert [x["id"] for x in r["in_both"]] == ["2", "3"]

    def test_empty_inputs(self):
        r = diff_by_field([], [], "id")
        assert r == {"only_left": [], "only_right": [], "in_both": []}

    def test_missing_key_excluded(self):
        left = [{"id": "1"}, {"msg": "no id"}]
        right = [{"id": "1"}]
        r = diff_by_field(left, right, "id")
        assert r["in_both"] == [{"id": "1"}]
        assert r["only_left"] == []


class TestDiffFieldValues:
    def test_detects_changed_field(self):
        changes = diff_field_values(LEFT, RIGHT, "id")
        ids = [c["id"] for c in changes]
        assert "2" in ids

    def test_unchanged_record_not_reported(self):
        changes = diff_field_values(LEFT, RIGHT, "id")
        ids = [c["id"] for c in changes]
        assert "3" not in ids

    def test_change_detail(self):
        changes = diff_field_values(LEFT, RIGHT, "id")
        rec = next(c for c in changes if c["id"] == "2")
        assert rec["changes"]["level"] == {"left": "warn", "right": "info"}

    def test_empty_returns_empty(self):
        assert diff_field_values([], [], "id") == []


class TestCountDiff:
    def test_counts(self):
        c = count_diff(LEFT, RIGHT, "id")
        assert c == {"only_left": 1, "only_right": 1, "in_both": 2}

    def test_identical_sets(self):
        c = count_diff(LEFT, LEFT, "id")
        assert c["only_left"] == 0
        assert c["only_right"] == 0
        assert c["in_both"] == 3
