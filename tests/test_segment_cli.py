"""Tests for logslice/segment_cli.py."""

import json
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.segment_cli import parse_segment_args, run_segment, _parse_boundaries


class TestParseSegmentArgs:
    def test_field_required(self):
        with pytest.raises(SystemExit):
            parse_segment_args([])

    def test_field_parsed(self):
        args = parse_segment_args(["--field", "level"])
        assert args.field == "level"

    def test_default_label(self):
        args = parse_segment_args(["--field", "x"])
        assert args.default == "other"

    def test_custom_default(self):
        args = parse_segment_args(["--field", "x", "--default", "unknown"])
        assert args.default == "unknown"

    def test_boundaries_parsed(self):
        args = parse_segment_args(["--field", "x", "--boundary", "100:low"])
        assert args.boundaries == ["100:low"]

    def test_multiple_boundaries(self):
        args = parse_segment_args(
            ["--field", "x", "--boundary", "100:low", "--boundary", "500:high"]
        )
        assert len(args.boundaries) == 2

    def test_counts_flag_default_false(self):
        args = parse_segment_args(["--field", "x"])
        assert args.counts is False

    def test_counts_flag_set(self):
        args = parse_segment_args(["--field", "x", "--counts"])
        assert args.counts is True

    def test_custom_segment_field(self):
        args = parse_segment_args(["--field", "x", "--segment-field", "tier"])
        assert args.segment_field == "tier"


class TestParseBoundaries:
    def test_parses_single(self):
        result = _parse_boundaries(["100:low"])
        assert result == [("100", "low")]

    def test_sorted_ascending(self):
        result = _parse_boundaries(["500:mid", "100:low"])
        assert result[0][0] == "100"

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            _parse_boundaries(["nocolon"])


class TestRunSegment:
    def _run(self, stdin_text, argv):
        out_lines = []
        with patch("sys.stdin", StringIO(stdin_text)):
            with patch("builtins.print", side_effect=lambda x: out_lines.append(x)):
                run_segment(argv)
        return out_lines

    def test_tags_records(self):
        lines = json.dumps({"val": "600"}) + "\n"
        out = self._run(lines, ["--field", "val", "--boundary", "100:low", "--boundary", "500:mid"])
        record = json.loads(out[0])
        assert record["_segment"] == "mid"

    def test_counts_mode(self):
        data = "\n".join(
            [json.dumps({"val": "600"}), json.dumps({"val": "50"})]
        ) + "\n"
        out = self._run(
            data,
            ["--field", "val", "--boundary", "100:low", "--boundary", "500:mid", "--counts"],
        )
        parsed = [json.loads(l) for l in out]
        labels = {r["segment"]: r["count"] for r in parsed}
        assert labels["mid"] == 1
        assert labels["other"] == 1

    def test_custom_segment_field(self):
        lines = json.dumps({"val": "200"}) + "\n"
        out = self._run(
            lines,
            ["--field", "val", "--boundary", "100:low", "--segment-field", "tier"],
        )
        record = json.loads(out[0])
        assert "tier" in record
        assert "_segment" not in record
