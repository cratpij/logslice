"""Tests for logslice.cli module."""
import json
from unittest.mock import patch, mock_open
import pytest
from logslice.cli import run, build_parser


LINES = [
    '{"timestamp": "2024-01-01T10:00:00Z", "level": "info", "msg": "start"}',
    '{"timestamp": "2024-01-01T11:00:00Z", "level": "warn", "msg": "slow query"}',
    '{"timestamp": "2024-01-01T12:00:00Z", "level": "error", "msg": "failed"}',
]
LOG_CONTENT = "\n".join(LINES)


class TestBuildParser:
    def test_defaults(self):
        p = build_parser()
        args = p.parse_args([])
        assert args.fmt == "json"
        assert args.ts_field == "timestamp"
        assert args.where == []
        assert args.contains == []


class TestRunCli:
    def _run(self, argv, content=LOG_CONTENT):
        import io
        out = io.StringIO()
        with patch("builtins.open", mock_open(read_data=content)):
            with patch("logslice.output.sys.stdout", out):
                code = run(argv)
        return code, out.getvalue()

    def test_filters_by_start(self):
        code, output = self._run(["fake.log", "--start", "2024-01-01T11:00:00Z"])
        assert code == 0
        records = [json.loads(l) for l in output.strip().splitlines()]
        assert all(r["timestamp"] >= "2024-01-01T11:00:00Z" for r in records)
        assert len(records) == 2

    def test_where_filter(self):
        code, output = self._run(["fake.log", "--where", "level=error"])
        assert code == 0
        records = [json.loads(l) for l in output.strip().splitlines()]
        assert len(records) == 1
        assert records[0]["level"] == "error"

    def test_contains_filter(self):
        code, output = self._run(["fake.log", "--contains", "msg=slow"])
        assert code == 0
        records = [json.loads(l) for l in output.strip().splitlines()]
        assert len(records) == 1
        assert "slow" in records[0]["msg"]

    def test_invalid_where_exits(self):
        with patch("builtins.open", mock_open(read_data=LOG_CONTENT)):
            with pytest.raises(SystemExit) as exc:
                run(["fake.log", "--where", "badvalue"])
        assert exc.value.code == 1

    def test_missing_file_returns_error(self):
        code = run(["nonexistent_file_xyz.log"])
        assert code == 1
