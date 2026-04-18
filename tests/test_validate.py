import pytest
from logslice.validate import (
    require_fields,
    validate_type,
    validate_schema,
    filter_valid,
    partition_valid,
)


class TestRequireFields:
    def test_all_present(self):
        assert require_fields({"a": 1, "b": 2}, ["a", "b"]) == []

    def test_missing_one(self):
        assert require_fields({"a": 1}, ["a", "b"]) == ["b"]

    def test_missing_all(self):
        assert require_fields({}, ["x", "y"]) == ["x", "y"]

    def test_empty_required(self):
        assert require_fields({"a": 1}, []) == []


class TestValidateType:
    def test_correct_type(self):
        assert validate_type({"level": "info"}, "level", str) is True

    def test_wrong_type(self):
        assert validate_type({"count": "3"}, "count", int) is False

    def test_missing_field(self):
        assert validate_type({}, "level", str) is False

    def test_int_field(self):
        assert validate_type({"count": 5}, "count", int) is True


class TestValidateSchema:
    def test_valid_record(self):
        r = {"ts": "2024-01-01", "level": "info", "msg": "ok"}
        errors = validate_schema(r, required=["ts", "level"], types={"level": str})
        assert errors == []

    def test_missing_required(self):
        errors = validate_schema({"msg": "hi"}, required=["ts", "level"])
        assert any("ts" in e for e in errors)
        assert any("level" in e for e in errors)

    def test_wrong_type_error(self):
        errors = validate_schema({"count": "five"}, types={"count": int})
        assert len(errors) == 1
        assert "count" in errors[0]

    def test_no_constraints(self):
        assert validate_schema({"a": 1}) == []


class TestFilterValid:
    def test_keeps_valid(self):
        records = [{"a": 1}, {"b": 2}, {"a": 3}]
        result = filter_valid(records, required=["a"])
        assert result == [{"a": 1}, {"a": 3}]

    def test_empty_input(self):
        assert filter_valid([], required=["a"]) == []

    def test_all_invalid(self):
        assert filter_valid([{"x": 1}], required=["a"]) == []


class TestPartitionValid:
    def test_splits_correctly(self):
        records = [{"a": 1}, {"b": 2}, {"a": 3}]
        valid, invalid = partition_valid(records, required=["a"])
        assert valid == [{"a": 1}, {"a": 3}]
        assert invalid == [{"b": 2}]

    def test_all_valid(self):
        records = [{"a": 1}, {"a": 2}]
        valid, invalid = partition_valid(records, required=["a"])
        assert len(valid) == 2
        assert invalid == []

    def test_empty_input(self):
        valid, invalid = partition_valid([])
        assert valid == [] and invalid == []
