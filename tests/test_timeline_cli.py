"""Tests for logslice.timeline_cli."""

from __future__ import annotations

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.timeline_cli import _parse_interval, parse_timeline_args, run_timeline


class TestParseInterval:
    def test_plain_integer(self):
        assert _parse_interval("60") == 60

    def test_seconds_suffix(self):
        assert _parse_interval("30s") == 30

    def test_minutes_suffix(self):
        assert _parse_interval("5m") == 300

    def test_hours_suffix(self):
        assert _parse_interval("2h") == 7200


class TestParseTimelineArgs:
    def test_defaults(self):
        args = parse_timeline_args([])
        assert args.file == "-"
        assert args.interval == "60"
        assert args.ts_field == "timestamp"
        assert args.counts is False
        assert args.bar_char == "#"
        assert args.max_width == 40

    def test_counts_flag(self):
        args = parse_timeline_args(["--counts"])
        assert args.counts is True

    def test_custom_interval(self):
        args = parse_timeline_args(["--interval", "5m"])
        assert args.interval == "5m"

    def test_custom_ts_field(self):
        args = parse_timeline_args(["--ts-field", "time"])
        assert args.ts_field == "time"

    def test_custom_bar_char(self):
        args = parse_timeline_args(["--bar-char", "="])
        assert args.bar_char == "="

    def test_file_positional(self):
        args = parse_timeline_args(["myfile.log"])
        assert args.file == "myfile.log"


LINES = [
    '{"timestamp": "2024-01-01T10:00:05Z", "msg": "a"}\n',
    '{"timestamp": "2024-01-01T10:00:45Z", "msg": "b"}\n',
    '{"timestamp": "2024-01-01T10:01:10Z", "msg": "c"}\n',
]


class TestRunTimeline:
    def _run(self, argv, stdin_lines=None):
        stdin_data = "".join(stdin_lines or LINES)
        with patch("sys.stdin", StringIO(stdin_data)):
            buf = StringIO()
            with patch("sys.stdout", buf):
                run_timeline(argv)
        return buf.getvalue()

    def test_ascii_output_contains_bucket(self):
        out = self._run([])
        assert "2024-01-01" in out

    def test_counts_mode_outputs_jsonl(self):
        out = self._run(["--counts"])
        lines = [l for l in out.strip().splitlines() if l]
        assert len(lines) == 2
        first = json.loads(lines[0])
        assert "bucket" in first
        assert "count" in first

    def test_counts_sum_matches_input(self):
        out = self._run(["--counts"])
        lines = [l for l in out.strip().splitlines() if l]
        total = sum(json.loads(l)["count"] for l in lines)
        assert total == 3
