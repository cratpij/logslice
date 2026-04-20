import pytest
from logslice.mask import mask_field, mask_fields, mask_pattern, mask_records


class TestMaskField:
    def test_masks_entire_value_by_default(self):
        record = {"token": "abcdef"}
        result = mask_field(record, "token")
        assert result["token"] == "******"

    def test_keeps_visible_start(self):
        record = {"token": "abcdef"}
        result = mask_field(record, "token", visible_start=2)
        assert result["token"] == "ab****"

    def test_keeps_visible_end(self):
        record = {"token": "abcdef"}
        result = mask_field(record, "token", visible_end=2)
        assert result["token"] == "****ef"

    def test_keeps_start_and_end(self):
        record = {"card": "1234567890123456"}
        result = mask_field(record, "card", visible_start=4, visible_end=4)
        assert result["card"] == "1234********3456"

    def test_missing_field_unchanged(self):
        record = {"other": "value"}
        result = mask_field(record, "token")
        assert result == {"other": "value"}

    def test_does_not_mutate_original(self):
        record = {"token": "secret"}
        mask_field(record, "token")
        assert record["token"] == "secret"

    def test_custom_mask_char(self):
        record = {"pin": "1234"}
        result = mask_field(record, "pin", char="#")
        assert result["pin"] == "####"

    def test_value_too_short_for_windows(self):
        record = {"pin": "12"}
        result = mask_field(record, "pin", visible_start=2, visible_end=2)
        assert result["pin"] == "**"


class TestMaskFields:
    def test_masks_multiple_fields(self):
        record = {"a": "hello", "b": "world"}
        result = mask_fields(record, ["a", "b"])
        assert result["a"] == "*****"
        assert result["b"] == "*****"

    def test_unaffected_fields_preserved(self):
        record = {"a": "hello", "keep": "safe"}
        result = mask_fields(record, ["a"])
        assert result["keep"] == "safe"

    def test_empty_fields_list(self):
        record = {"a": "hello"}
        result = mask_fields(record, [])
        assert result == {"a": "hello"}


class TestMaskPattern:
    def test_replaces_pattern_match(self):
        record = {"message": "user=john email=john@example.com"}
        result = mask_pattern(record, "message", r"\S+@\S+")
        assert result["message"] == "user=john email=***"

    def test_missing_field_unchanged(self):
        record = {"other": "value"}
        result = mask_pattern(record, "message", r"\d+")
        assert result == {"other": "value"}

    def test_custom_replacement(self):
        record = {"text": "call 555-1234 now"}
        result = mask_pattern(record, "text", r"\d{3}-\d{4}", "[PHONE]")
        assert result["text"] == "call [PHONE] now"


class TestMaskRecords:
    def test_applies_to_all_records(self):
        records = [{"token": "abc"}, {"token": "xyz"}]
        result = mask_records(records, ["token"])
        assert all(r["token"] == "***" for r in result)

    def test_empty_input(self):
        assert mask_records([], ["token"]) == []
