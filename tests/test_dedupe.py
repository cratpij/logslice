"""Tests for logslice.dedupe."""
from logslice.dedupe import dedupe_by_field, dedupe_by_fields, dedupe_exact


RECORDS = [
    {"id": "1", "level": "info", "msg": "started"},
    {"id": "2", "level": "warn", "msg": "slow"},
    {"id": "1", "level": "info", "msg": "started"},  # duplicate id
    {"id": "3", "level": "info", "msg": "done"},
]


class TestDedupeByField:
    def test_removes_duplicate_ids(self):
        result = list(dedupe_by_field(RECORDS, "id"))
        ids = [r["id"] for r in result]
        assert ids == ["1", "2", "3"]

    def test_keeps_first_occurrence(self):
        result = list(dedupe_by_field(RECORDS, "id"))
        assert result[0]["msg"] == "started"

    def test_missing_field_passed_through(self):
        records = [{"msg": "no id"}, {"msg": "also no id"}]
        result = list(dedupe_by_field(records, "id"))
        assert len(result) == 2

    def test_empty_input(self):
        assert list(dedupe_by_field([], "id")) == []

    def test_all_unique(self):
        result = list(dedupe_by_field(RECORDS[:2], "id"))
        assert len(result) == 2


class TestDedupeByFields:
    def test_composite_key(self):
        records = [
            {"host": "a", "svc": "x", "msg": "1"},
            {"host": "a", "svc": "x", "msg": "2"},  # dup on host+svc
            {"host": "a", "svc": "y", "msg": "3"},
        ]
        result = list(dedupe_by_fields(records, ["host", "svc"]))
        assert len(result) == 2

    def test_missing_any_field_passes_through(self):
        records = [{"host": "a"}, {"host": "a"}]  # no 'svc'
        result = list(dedupe_by_fields(records, ["host", "svc"]))
        assert len(result) == 2

    def test_empty_fields_list(self):
        records = [{"a": 1}, {"a": 1}]
        result = list(dedupe_by_fields(records, []))
        # empty key tuple — both deduplicated to one
        assert len(result) == 1


class TestDedupeExact:
    def test_removes_exact_duplicates(self):
        records = [{"a": 1, "b": 2}, {"a": 1, "b": 2}, {"a": 1, "b": 3}]
        result = list(dedupe_exact(records))
        assert len(result) == 2

    def test_different_values_kept(self):
        records = [{"a": 1}, {"a": 2}, {"a": 3}]
        assert list(dedupe_exact(records)) == records

    def test_empty_input(self):
        assert list(dedupe_exact([])) == []
