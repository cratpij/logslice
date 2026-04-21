"""Tests for logslice.merge_cli."""

import io
import json
from unittest.mock import patch, mock_open

import pytest

from logslice.merge_cli import parse_merge_args, run_merge


LINES_A = '{"id": 1, "timestamp": "2024-01-01T10:00:00Z"}\n{"id": 2, "timestamp": "2024-01-01T12:00:00Z"}\n'
LINES_B = '{"id": 3, "timestamp": "2024-01-01T11:00:00Z"}\n{"id": 4, "timestamp": "2024-01-01T13:00:00Z"}\n'


class TestParseMergeArgs:
    def test_defaults(self):
        args = parse_merge_args(["a.log", "b.log"])
        assert args.files == ["a.log", "b.log"]
        assert args.sort is False
        assert args.timestamp_field == "timestamp"
        assert args.dedupe is None
        assert args.format == "json"

    def test_sort_flag(self):
        args = parse_merge_args(["a.log", "--sort"])
        assert args.sort is True

    def test_custom_timestamp_field(self):
        args = parse_merge_args(["a.log", "--timestamp-field", "ts"])
        assert args.timestamp_field == "ts"

    def test_dedupe_field(self):
        args = parse_merge_args(["a.log", "--dedupe", "id"])
        assert args.dedupe == "id"

    def test_format_kv(self):
        args = parse_merge_args(["a.log", "--format", "kv"])
        assert args.format == "kv"


def _run(argv, files_content):
    """Helper: run run_merge with mocked file reads and captured stdout."""
    out = io.StringIO()
    open_calls = iter(files_content)

    def fake_open(path, *a, **kw):
        content = next(open_calls)
        return io.StringIO(content)

    with patch("logslice.merge_cli.open", side_effect=fake_open):
        with patch("sys.stdout", out):
            run_merge(argv)
    return out.getvalue()


class TestRunMerge:
    def test_basic_merge_two_files(self):
        output = _run(["a.log", "b.log"], [LINES_A, LINES_B])
        records = [json.loads(l) for l in output.strip().splitlines()]
        assert len(records) == 4

    def test_sorted_merge(self):
        output = _run(["a.log", "b.log", "--sort"], [LINES_A, LINES_B])
        records = [json.loads(l) for l in output.strip().splitlines()]
        ids = [r["id"] for r in records]
        assert ids == [1, 3, 2, 4]

    def test_dedupe_merge(self):
        dup_b = '{"id": 1, "timestamp": "2024-01-01T11:00:00Z"}\n{"id": 5}\n'
        output = _run(["a.log", "b.log", "--dedupe", "id"], [LINES_A, dup_b])
        records = [json.loads(l) for l in output.strip().splitlines()]
        ids = [r["id"] for r in records]
        assert ids.count(1) == 1
        assert 5 in ids
