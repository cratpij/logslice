"""Tests for logslice.window_cli."""

import json
from io import StringIO
from unittest.mock import patch, MagicMock

from logslice.window_cli import parse_window_args, run_window


LINES = [
    '{"timestamp": "2024-01-01T00:00:00Z", "level": "info", "msg": "a"}',
    '{"timestamp": "2024-01-01T00:00:30Z", "level": "warn", "msg": "b"}',
    '{"timestamp": "2024-01-01T00:01:10Z", "level": "error", "msg": "c"}',
]


class TestParseWindowArgs:
    def test_defaults(self):
        args = parse_window_args([])
        assert args.mode == "tumbling"
        assert args.window == 60.0
        assert args.step is None
        assert args.ts_field == "timestamp"
        assert args.count_only is False
        assert args.file == "-"

    def test_mode_sliding(self):
        args = parse_window_args(["--mode", "sliding", "--step", "30"])
        assert args.mode == "sliding"
        assert args.step == 30.0

    def test_count_only_flag(self):
        args = parse_window_args(["--count-only"])
        assert args.count_only is True

    def test_custom_ts_field(self):
        args = parse_window_args(["--ts-field", "ts"])
        assert args.ts_field == "ts"

    def test_window_size(self):
        args = parse_window_args(["--window", "120"])
        assert args.window == 120.0


class TestRunWindowCli:
    def _run(self, argv, stdin_lines):
        captured = []
        stdin = StringIO("\n".join(stdin_lines))
        with patch("sys.stdin", stdin), patch("builtins.print", side_effect=captured.append):
            run_window(argv)
        return [json.loads(line) for line in captured]

    def test_tumbling_emits_windows(self):
        result = self._run(["--window", "60"], LINES)
        assert len(result) >= 1
        for w in result:
            assert "start" in w
            assert "end" in w
            assert "count" in w

    def test_count_only_omits_records(self):
        result = self._run(["--count-only", "--window", "60"], LINES)
        for w in result:
            assert "records" not in w

    def test_count_only_has_correct_count(self):
        result = self._run(["--count-only", "--window", "60"], LINES)
        total = sum(w["count"] for w in result)
        assert total == len(LINES)

    def test_records_included_by_default(self):
        result = self._run(["--window", "60"], LINES)
        for w in result:
            assert "records" in w

    def test_sliding_mode(self):
        result = self._run(["--mode", "sliding", "--window", "90", "--step", "30"], LINES)
        assert len(result) >= 1
