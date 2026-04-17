"""Tests for logslice.export."""
import io
import json
import pytest
from logslice.export import to_jsonl, to_csv, to_tsv, write_export


RECORDS = [
    {"ts": "2024-01-01T00:00:00Z", "level": "INFO", "msg": "started"},
    {"ts": "2024-01-01T00:01:00Z", "level": "ERROR", "msg": "oh no"},
]


class TestToJsonl:
    def test_two_records(self):
        out = to_jsonl(RECORDS)
        lines = out.strip().splitlines()
        assert len(lines) == 2

    def test_each_line_valid_json(self):
        for line in to_jsonl(RECORDS).strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_empty_returns_empty_string(self):
        assert to_jsonl([]) == ""

    def test_trailing_newline(self):
        assert to_jsonl(RECORDS).endswith("\n")

    def test_record_fields_preserved(self):
        """Each serialised line must contain all original fields and values."""
        lines = to_jsonl(RECORDS).strip().splitlines()
        for original, line in zip(RECORDS, lines):
            obj = json.loads(line)
            assert obj == original


class TestToCsv:
    def test_header_row(self):
        out = to_csv(RECORDS)
        header = out.splitlines()[0]
        assert "ts" in header and "level" in header and "msg" in header

    def test_row_count(self):
        out = to_csv(RECORDS)
        assert len(out.splitlines()) == 3  # header + 2 rows

    def test_empty_returns_empty_string(self):
        assert to_csv([]) == ""

    def test_custom_fieldnames_limits_columns(self):
        out = to_csv(RECORDS, fieldnames=["level", "msg"])
        header = out.splitlines()[0]
        assert "ts" not in header
        assert "level" in header

    def test_values_present(self):
        out = to_csv(RECORDS)
        assert "ERROR" in out
        assert "started" in out


class TestToTsv:
    def test_tab_delimiter(self):
        out = to_tsv(RECORDS)
        assert "\t" in out.splitlines()[0]

    def test_row_count(self):
        out = to_tsv(RECORDS)
        assert len(out.splitlines()) == 3

    def test_empty_returns_empty_string(self):
        assert to_tsv([]) == ""


class TestWriteExport:
    def _buf(self):
        return io.StringIO()

    def test_jsonl_format(self):
        buf = self._buf()
        write_export(RECORDS, "jsonl", buf)
        assert buf.getvalue().strip() != ""

    def test_csv_format(self):
        buf = self._buf()
        write_export(RECORDS, "csv", buf)
        assert "level" in buf.getvalue()

    def test_tsv_format(self):
        buf = self._buf()
        write_export(RECORDS, "tsv", buf)
        assert "\t" in buf.getvalue()

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown export format"):
            write_export(RECORDS, "xml", self._buf())

    def test_write_export_matches_direct_call(self):
        """write_export output should match the corresponding to_* function."""
        for fmt, fn in (("jsonl", to_jsonl), ("csv", to_csv), ("tsv", to_tsv)):
            buf = self._buf()
            write_export(RECORDS, fmt, buf)
            assert buf.getvalue() == fn(RECORDS)
