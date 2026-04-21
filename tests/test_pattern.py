"""Tests for logslice.pattern."""

import pytest
from logslice.pattern import (
    compile_pattern,
    match_field,
    filter_by_pattern,
    filter_any_field,
    extract_matches,
)


class TestCompilePattern:
    def test_basic_pattern(self):
        p = compile_pattern(r"error")
        assert p.search("an error occurred")

    def test_case_sensitive_by_default(self):
        p = compile_pattern(r"error")
        assert not p.search("ERROR")

    def test_ignore_case(self):
        p = compile_pattern(r"error", ignore_case=True)
        assert p.search("ERROR")

    def test_regex_special_chars(self):
        p = compile_pattern(r"\d{3}")
        assert p.search("code 404")


class TestMatchField:
    def test_matching_field(self):
        p = compile_pattern(r"fail")
        assert match_field({"msg": "failed to connect"}, "msg", p)

    def test_non_matching_field(self):
        p = compile_pattern(r"fail")
        assert not match_field({"msg": "all good"}, "msg", p)

    def test_missing_field_returns_false(self):
        p = compile_pattern(r"fail")
        assert not match_field({"level": "error"}, "msg", p)

    def test_numeric_field_coerced_to_str(self):
        p = compile_pattern(r"404")
        assert match_field({"status": 404}, "status", p)


class TestFilterByPattern:
    RECORDS = [
        {"msg": "connection failed", "level": "error"},
        {"msg": "request ok", "level": "info"},
        {"msg": "timeout failure", "level": "warn"},
    ]

    def test_filters_matching(self):
        p = compile_pattern(r"fail")
        result = list(filter_by_pattern(self.RECORDS, "msg", p))
        assert len(result) == 2
        assert all("fail" in r["msg"] for r in result)

    def test_invert_returns_non_matching(self):
        p = compile_pattern(r"fail")
        result = list(filter_by_pattern(self.RECORDS, "msg", p, invert=True))
        assert len(result) == 1
        assert result[0]["msg"] == "request ok"

    def test_empty_input(self):
        p = compile_pattern(r"fail")
        assert list(filter_by_pattern([], "msg", p)) == []

    def test_no_match_returns_empty(self):
        p = compile_pattern(r"xyz")
        result = list(filter_by_pattern(self.RECORDS, "msg", p))
        assert result == []


class TestFilterAnyField:
    RECORDS = [
        {"msg": "all good", "level": "info"},
        {"msg": "something broke", "level": "error"},
    ]

    def test_matches_any_field(self):
        p = compile_pattern(r"error")
        result = list(filter_any_field(self.RECORDS, p))
        assert len(result) == 1
        assert result[0]["level"] == "error"

    def test_invert(self):
        p = compile_pattern(r"error")
        result = list(filter_any_field(self.RECORDS, p, invert=True))
        assert len(result) == 1
        assert result[0]["level"] == "info"


class TestExtractMatches:
    def test_extracts_match_to_dest(self):
        p = compile_pattern(r"\d+")
        records = [{"msg": "status 200 ok"}]
        result = list(extract_matches(records, "msg", p))
        assert result[0]["_match"] == "200"

    def test_no_match_no_dest_field(self):
        p = compile_pattern(r"\d+")
        records = [{"msg": "no numbers here"}]
        result = list(extract_matches(records, "msg", p))
        assert "_match" not in result[0]

    def test_missing_field_passes_through(self):
        p = compile_pattern(r"\d+")
        records = [{"level": "info"}]
        result = list(extract_matches(records, "msg", p))
        assert result == [{"level": "info"}]

    def test_custom_dest_field(self):
        p = compile_pattern(r"[A-Z]+")
        records = [{"msg": "ERROR occurred"}]
        result = list(extract_matches(records, "msg", p, dest_field="extracted"))
        assert result[0]["extracted"] == "ERROR"

    def test_does_not_mutate_original(self):
        p = compile_pattern(r"\d+")
        original = {"msg": "code 42"}
        records = [original]
        list(extract_matches(records, "msg", p))
        assert "_match" not in original
