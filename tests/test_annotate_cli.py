"""Tests for logslice.annotate_cli."""

import json
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.annotate_cli import parse_annotate_args, run_annotate


class TestParseAnnotateArgs:
    def test_label_mode(self):
        args = parse_annotate_args(["--field", "env", "--label", "prod"])
        assert args.field == "env"
        assert args.label == "prod"

    def test_index_mode(self):
        args = parse_annotate_args(["--field", "_i", "--index"])
        assert args.index is True
        assert args.start == 0

    def test_custom_start(self):
        args = parse_annotate_args(["--field", "_i", "--index", "--start", "5"])
        assert args.start == 5

    def test_condition_mode(self):
        args = parse_annotate_args(
            ["--field", "flag", "--condition", "r['level']=='error'"]
        )
        assert args.condition == "r['level']=='error'"

    def test_defaults(self):
        args = parse_annotate_args(["--field", "x", "--label", "v"])
        assert args.fmt == "json"
        assert args.input == "-"

    def test_mutually_exclusive_raises(self):
        with pytest.raises(SystemExit):
            parse_annotate_args(["--field", "x", "--label", "v", "--index"])


class TestRunAnnotate:
    def _run(self, lines, extra_args):
        captured = []
        with patch("sys.stdin", StringIO(lines)), patch(
            "builtins.print", side_effect=lambda x: captured.append(x)
        ):
            run_annotate(["--field", "env"] + extra_args)
        return captured

    def test_label_applied(self):
        lines = '{"msg": "hi"}\n'
        out = self._run(lines, ["--label", "staging"])
        record = json.loads(out[0])
        assert record["env"] == "staging"

    def test_index_applied(self):
        lines = '{"msg": "a"}\n{"msg": "b"}\n'
        out = self._run(lines, ["--index"])
        assert json.loads(out[0])["env"] == 0
        assert json.loads(out[1])["env"] == 1

    def test_condition_applied(self):
        lines = '{"level": "error"}\n{"level": "info"}\n'
        out = self._run(
            lines,
            ["--condition", "r.get('level')=='error'", "--true-value", "yes", "--false-value", "no"],
        )
        assert json.loads(out[0])["env"] == "yes"
        assert json.loads(out[1])["env"] == "no"
