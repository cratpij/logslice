"""Tests for logslice.output module."""
import io
import pytest
from logslice.output import format_json, format_kv, format_pretty, write_records


SAMPLE = {"level": "info", "msg": "hello world", "code": 42}


class TestFormatJson:
    def test_compact(self):
        result = format_json(SAMPLE)
        assert result == '{"level": "info", "msg": "hello world", "code": 42}'

    def test_no_newline(self):
        assert "\n" not in format_json(SAMPLE)


class TestFormatKv:
    def test_quotes_values_with_spaces(self):
        result = format_kv(SAMPLE)
        assert 'msg="hello world"' in result

    def test_plain_values(self):
        result = format_kv(SAMPLE)
        assert "level=info" in result
        assert "code=42" in result


class TestFormatPretty:
    def test_indented(self):
        result = format_pretty(SAMPLE)
        assert "\n" in result
        assert "  " in result

    def test_valid_json(self):
        import json
        assert json.loads(format_pretty(SAMPLE)) == SAMPLE


class TestWriteRecords:
    def _run(self, records, fmt="json"):
        buf = io.StringIO()
        count = write_records(records, fmt=fmt, out=buf)
        return count, buf.getvalue()

    def test_returns_count(self):
        records = [{"a": 1}, {"a": 2}]
        count, _ = self._run(records)
        assert count == 2

    def test_each_record_on_own_line(self):
        records = [{"a": 1}, {"b": 2}]
        _, output = self._run(records)
        lines = output.strip().splitlines()
        assert len(lines) == 2

    def test_kv_format(self):
        records = [{"level": "warn", "code": 9}]
        _, output = self._run(records, fmt="kv")
        assert "level=warn" in output
        assert "code=9" in output

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown format"):
            write_records([], fmt="xml", out=io.StringIO())

    def test_empty_input(self):
        count, output = self._run([])
        assert count == 0
        assert output == ""
