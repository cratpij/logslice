"""Tests for logslice.resample_cli."""

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.resample_cli import parse_resample_args, _parse_interval, run_resample


class TestParseInterval:
    def test_plain_integer(self):
        assert _parse_interval("60") == 60

    def test_seconds_suffix(self):
        assert _parse_interval("30s") == 30

    def test_minutes_suffix(self):
        assert _parse_interval("5m") == 300

    def test_hours_suffix(self):
        assert _parse_interval("2h") == 7200

    def test_days_suffix(self):
        assert _parse_interval("1d") == 86400

    def test_uppercase_suffix(self):
        assert _parse_interval("10M") == 600


class TestParseResampleArgs:
    def test_defaults(self):
        args = parse_resample_args(["--interval", "60"])
        assert args.mode == "count"
        assert args.ts_field == "timestamp"
        assert args.output_format == "json"
        assert args.file == "-"

    def test_mode_sum(self):
        args = parse_resample_args(["--interval", "1m", "--mode", "sum", "--field", "dur"])
        assert args.mode == "sum"
        assert args.field == "dur"

    def test_custom_ts_field(self):
        args = parse_resample_args(["--interval", "60", "--ts-field", "ts"])
        assert args.ts_field == "ts"

    def test_format_kv(self):
        args = parse_resample_args(["--interval", "60", "--format", "kv"])
        assert args.output_format == "kv"


class TestRunResample:
    def _run(self, lines, extra_args=None):
        argv = ["--interval", "60"] + (extra_args or [])
        stdin = StringIO("\n".join(lines))
        out = StringIO()
        with patch("sys.stdin", stdin), patch("sys.stdout", out):
            run_resample(argv)
        return out.getvalue()

    def test_count_mode_produces_output(self):
        lines = [
            '{"timestamp": "2024-01-01T00:00:10Z"}',
            '{"timestamp": "2024-01-01T00:00:50Z"}',
        ]
        output = self._run(lines)
        records = [json.loads(l) for l in output.strip().splitlines()]
        assert len(records) == 1
        assert records[0]["count"] == 2

    def test_sum_mode_aggregates_field(self):
        lines = [
            '{"timestamp": "2024-01-01T00:00:10Z", "dur": 10}',
            '{"timestamp": "2024-01-01T00:00:50Z", "dur": 20}',
        ]
        output = self._run(lines, ["--mode", "sum", "--field", "dur"])
        records = [json.loads(l) for l in output.strip().splitlines()]
        assert records[0]["dur"] == 30.0

    def test_sum_without_field_exits(self):
        lines = ['{"timestamp": "2024-01-01T00:00:10Z", "dur": 5}']
        stdin = StringIO("\n".join(lines))
        with patch("sys.stdin", stdin), pytest.raises(SystemExit) as exc:
            run_resample(["--interval", "60", "--mode", "sum"])
        assert exc.value.code == 1

    def test_avg_mode(self):
        lines = [
            '{"timestamp": "2024-01-01T00:00:10Z", "dur": 10}',
            '{"timestamp": "2024-01-01T00:00:50Z", "dur": 30}',
        ]
        output = self._run(lines, ["--mode", "avg", "--field", "dur"])
        records = [json.loads(l) for l in output.strip().splitlines()]
        assert records[0]["dur"] == pytest.approx(20.0)
