import pytest
from logslice.transform import rename_field, drop_fields, keep_fields, add_field, cast_field

RECORDS = [
    {"level": "info", "msg": "started", "code": "200"},
    {"level": "error", "msg": "failed", "code": "500"},
]


class TestRenameField:
    def test_renames_existing_key(self):
        result = rename_field(RECORDS, "level", "severity")
        assert all("severity" in r for r in result)
        assert all("level" not in r for r in result)

    def test_missing_key_unchanged(self):
        result = rename_field(RECORDS, "nonexistent", "x")
        assert result == RECORDS

    def test_does_not_mutate_original(self):
        rename_field(RECORDS, "level", "severity")
        assert "level" in RECORDS[0]


class TestDropFields:
    def test_drops_specified_fields(self):
        result = drop_fields(RECORDS, ["msg", "code"])
        assert all("msg" not in r and "code" not in r for r in result)

    def test_keeps_other_fields(self):
        result = drop_fields(RECORDS, ["code"])
        assert all("level" in r and "msg" in r for r in result)

    def test_empty_fields_list(self):
        result = drop_fields(RECORDS, [])
        assert result == RECORDS


class TestKeepFields:
    def test_keeps_only_specified(self):
        result = keep_fields(RECORDS, ["level"])
        assert all(list(r.keys()) == ["level"] for r in result)

    def test_missing_field_omitted(self):
        result = keep_fields(RECORDS, ["level", "missing"])
        assert all("missing" not in r for r in result)


class TestAddField:
    def test_adds_new_field(self):
        result = add_field(RECORDS, "env", "prod")
        assert all(r["env"] == "prod" for r in result)

    def test_does_not_overwrite_by_default(self):
        result = add_field(RECORDS, "level", "debug")
        assert result[0]["level"] == "info"

    def test_overwrites_when_flag_set(self):
        result = add_field(RECORDS, "level", "debug", overwrite=True)
        assert all(r["level"] == "debug" for r in result)


class TestCastField:
    def test_casts_string_to_int(self):
        result = cast_field(RECORDS, "code", int)
        assert all(isinstance(r["code"], int) for r in result)

    def test_invalid_cast_leaves_original(self):
        records = [{"code": "abc"}]
        result = cast_field(records, "code", int)
        assert result[0]["code"] == "abc"

    def test_missing_key_unchanged(self):
        result = cast_field(RECORDS, "nonexistent", int)
        assert result == RECORDS
