"""Tests for logslice.parser module."""

import pytest
from logslice.parser import parse_json_line, parse_kv_line, parse_line, parse_lines


class TestParseJsonLine:
    def test_valid_json_object(self):
        line = '{"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"}'
        result = parse_json_line(line)
        assert result == {"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"}

    def test_invalid_json_returns_none(self):
        assert parse_json_line("not json at all") is None

    def test_json_array_returns_none(self):
        assert parse_json_line('["a", "b"]') is None

    def test_empty_line_returns_none(self):
        assert parse_json_line("") is None

    def test_whitespace_line_returns_none(self):
        assert parse_json_line("   ") is None


class TestParseKvLine:
    def test_simple_kv(self):
        result = parse_kv_line("level=info msg=started")
        assert result == {"level": "info", "msg": "started"}

    def test_quoted_values(self):
        result = parse_kv_line('level=error msg="something went wrong"')
        assert result == {"level": "error", "msg": "something went wrong"}

    def test_no_kv_pairs_returns_none(self):
        assert parse_kv_line("plain text log line") is None

    def test_empty_line_returns_none(self):
        assert parse_kv_line("") is None


class TestParseLine:
    def test_prefers_json(self):
        line = '{"level": "debug"}'
        result = parse_line(line)
        assert result == {"level": "debug"}

    def test_falls_back_to_kv(self):
        result = parse_line("level=warn ts=2024-01-01")
        assert result == {"level": "warn", "ts": "2024-01-01"}

    def test_unparseable_returns_none(self):
        assert parse_line("just a plain sentence") is None


class TestParseLines:
    def test_mixed_lines(self):
        lines = [
            '{"level": "info"}',
            "level=warn ts=2024-01-02",
            "unparseable garbage!!!",
            '{"level": "error", "code": 500}',
        ]
        results = parse_lines(lines)
        assert len(results) == 3
        assert results[0] == {"level": "info"}
        assert results[1] == {"level": "warn", "ts": "2024-01-02"}
        assert results[2] == {"level": "error", "code": 500}

    def test_all_unparseable(self):
        assert parse_lines(["foo bar", "baz qux"]) == []

    def test_empty_input(self):
        assert parse_lines([]) == []
