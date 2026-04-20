import json
import io
from unittest.mock import patch
from logslice.mask_cli import parse_mask_args, run_mask


class TestParseMaskArgs:
    def test_defaults(self):
        args = parse_mask_args([])
        assert args.fields == []
        assert args.visible_start == 0
        assert args.visible_end == 0
        assert args.char == "*"
        assert args.output_format == "json"
        assert args.pattern is None
        assert args.pattern_field is None
        assert args.pattern_replacement == "***"

    def test_fields_parsed(self):
        args = parse_mask_args(["-f", "token", "email"])
        assert args.fields == ["token", "email"]

    def test_visible_start_end(self):
        args = parse_mask_args(["--visible-start", "2", "--visible-end", "4"])
        assert args.visible_start == 2
        assert args.visible_end == 4

    def test_custom_char(self):
        args = parse_mask_args(["--char", "#"])
        assert args.char == "#"

    def test_pattern_args(self):
        args = parse_mask_args(
            ["--pattern", r"\d+", "--pattern-field", "msg", "--pattern-replacement", "[NUM]"]
        )
        assert args.pattern == r"\d+"
        assert args.pattern_field == "msg"
        assert args.pattern_replacement == "[NUM]"


class TestRunMask:
    def _run(self, lines, argv):
        stdin_data = "".join(lines)
        with patch("sys.stdin", io.StringIO(stdin_data)), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            run_mask(argv)
            return mock_out.getvalue()

    def test_masks_field_from_stdin(self):
        lines = ['{"token": "abcdef"}\n']
        output = self._run(lines, ["-f", "token"])
        record = json.loads(output.strip())
        assert record["token"] == "******"

    def test_visible_start_end(self):
        lines = ['{"card": "1234567890"}\n']
        output = self._run(lines, ["-f", "card", "--visible-start", "2", "--visible-end", "2"])
        record = json.loads(output.strip())
        assert record["card"].startswith("12")
        assert record["card"].endswith("90")

    def test_pattern_masking(self):
        lines = ['{"msg": "call 555-1234 now"}\n']
        output = self._run(
            lines,
            ["--pattern", r"\d{3}-\d{4}", "--pattern-field", "msg",
             "--pattern-replacement", "[REDACTED]"]
        )
        record = json.loads(output.strip())
        assert "[REDACTED]" in record["msg"]
        assert "555-1234" not in record["msg"]

    def test_no_fields_passthrough(self):
        lines = ['{"level": "info", "msg": "ok"}\n']
        output = self._run(lines, [])
        record = json.loads(output.strip())
        assert record["level"] == "info"

    def test_multiple_records(self):
        lines = ['{"token": "aaa"}\n', '{"token": "bbb"}\n']
        output = self._run(lines, ["-f", "token"])
        records = [json.loads(l) for l in output.strip().splitlines()]
        assert len(records) == 2
        assert all(r["token"] == "***" for r in records)
