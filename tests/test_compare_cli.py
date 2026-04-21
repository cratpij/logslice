"""Tests for logslice.compare_cli."""

import io
import json
import os
import tempfile
import pytest

from logslice.compare_cli import parse_compare_args, run_compare


def _write_jsonl(records):
    """Write records to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for r in records:
        f.write(json.dumps(r) + "\n")
    f.close()
    return f.name


class TestParseMergeArgs:
    def test_defaults(self):
        args = parse_compare_args(["a.jsonl", "b.jsonl"])
        assert args.left == "a.jsonl"
        assert args.right == "b.jsonl"
        assert args.key == "id"
        assert args.fields is None
        assert args.changed_only is False
        assert args.format == "json"

    def test_custom_key(self):
        args = parse_compare_args(["a.jsonl", "b.jsonl", "--key", "trace_id"])
        assert args.key == "trace_id"

    def test_fields_flag(self):
        args = parse_compare_args(["a.jsonl", "b.jsonl", "--fields", "level", "msg"])
        assert args.fields == ["level", "msg"]

    def test_changed_only_flag(self):
        args = parse_compare_args(["a.jsonl", "b.jsonl", "--changed-only"])
        assert args.changed_only is True

    def test_format_summary(self):
        args = parse_compare_args(["a.jsonl", "b.jsonl", "--format", "summary"])
        assert args.format == "summary"


class TestRunCompare:
    def _run(self, left_records, right_records, extra_args=None):
        lp = _write_jsonl(left_records)
        rp = _write_jsonl(right_records)
        try:
            argv = [lp, rp] + (extra_args or [])
            out = io.StringIO()
            run_compare(argv, out=out)
            return out.getvalue()
        finally:
            os.unlink(lp)
            os.unlink(rp)

    def test_equal_record_in_output(self):
        records = [{"id": "1", "level": "info"}]
        output = self._run(records, records)
        data = json.loads(output.strip())
        assert data["status"] == "equal"

    def test_changed_record_in_output(self):
        left = [{"id": "1", "level": "info"}]
        right = [{"id": "1", "level": "error"}]
        output = self._run(left, right)
        data = json.loads(output.strip())
        assert data["status"] == "changed"
        assert "level" in data["diffs"]

    def test_changed_only_suppresses_equal(self):
        left = [{"id": "1", "level": "info"}, {"id": "2", "level": "warn"}]
        right = [{"id": "1", "level": "info"}, {"id": "2", "level": "error"}]
        output = self._run(left, right, ["--changed-only"])
        lines = [l for l in output.strip().splitlines() if l]
        assert len(lines) == 1
        assert json.loads(lines[0])["key"] == "2"

    def test_summary_format(self):
        left = [{"id": "1", "level": "info"}]
        right = [{"id": "1", "level": "error"}]
        output = self._run(left, right, ["--format", "summary"])
        assert "CHANGED" in output
        assert "key=1" in output
