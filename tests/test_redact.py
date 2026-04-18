"""Tests for logslice.redact."""

import pytest
from logslice.redact import redact_field, redact_fields, redact_pattern, redact_all


class TestRedactField:
    def test_redacts_existing_field(self):
        r = redact_field({"user": "alice", "msg": "hello"}, "user")
        assert r["user"] == "***"
        assert r["msg"] == "hello"

    def test_missing_field_unchanged(self):
        r = redact_field({"msg": "hello"}, "password")
        assert r == {"msg": "hello"}

    def test_custom_mask(self):
        r = redact_field({"token": "abc123"}, "token", mask="[REDACTED]")
        assert r["token"] == "[REDACTED]"

    def test_does_not_mutate_original(self):
        original = {"user": "alice"}
        redact_field(original, "user")
        assert original["user"] == "alice"


class TestRedactFields:
    def test_redacts_multiple_fields(self):
        r = redact_fields({"user": "alice", "pass": "secret", "msg": "hi"}, ["user", "pass"])
        assert r["user"] == "***"
        assert r["pass"] == "***"
        assert r["msg"] == "hi"

    def test_skips_missing_fields(self):
        r = redact_fields({"msg": "hi"}, ["user", "pass"])
        assert r == {"msg": "hi"}

    def test_empty_fields_list(self):
        original = {"user": "alice"}
        r = redact_fields(original, [])
        assert r == original


class TestRedactPattern:
    def test_replaces_pattern_in_field(self):
        r = redact_pattern({"msg": "token=abc123 ok"}, "msg", r"token=\w+")
        assert r["msg"] == "*** ok"

    def test_no_match_unchanged(self):
        r = redact_pattern({"msg": "hello world"}, "msg", r"token=\w+")
        assert r["msg"] == "hello world"

    def test_missing_field_unchanged(self):
        r = redact_pattern({"level": "info"}, "msg", r"\d+")
        assert "msg" not in r

    def test_does_not_mutate_original(self):
        original = {"msg": "pass=secret"}
        redact_pattern(original, "msg", r"pass=\w+")
        assert original["msg"] == "pass=secret"


class TestRedactAll:
    def test_redacts_all_records(self):
        records = [{"user": "alice", "x": 1}, {"user": "bob", "x": 2}]
        result = list(redact_all(records, ["user"]))
        assert all(r["user"] == "***" for r in result)
        assert result[0]["x"] == 1

    def test_empty_input(self):
        assert list(redact_all([], ["user"])) == []

    def test_returns_iterator(self):
        records = [{"a": "b"}]
        result = redact_all(records, ["a"])
        import types
        assert isinstance(result, types.GeneratorType)
