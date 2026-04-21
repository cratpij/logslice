"""CLI integration for pattern-based record filtering."""

import argparse
import sys
from typing import List, Optional

from logslice.parser import parse_lines
from logslice.pattern import compile_pattern, filter_by_pattern, filter_any_field
from logslice.output import write_records


def parse_pattern_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice pattern",
        description="Filter log records by regex pattern.",
    )
    parser.add_argument(
        "pattern",
        help="Regular expression to match against.",
    )
    parser.add_argument(
        "--field",
        default=None,
        help="Field to match against. If omitted, any field is checked.",
    )
    parser.add_argument(
        "--invert", "-v",
        action="store_true",
        default=False,
        help="Invert the match (exclude matching records).",
    )
    parser.add_argument(
        "--ignore-case", "-i",
        action="store_true",
        default=False,
        help="Case-insensitive matching.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "kv", "pretty"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Input log file. Reads from stdin if omitted.",
    )
    return parser.parse_args(argv)


def run_pattern(argv: Optional[List[str]] = None) -> None:
    args = parse_pattern_args(argv)

    if args.file:
        with open(args.file, "r") as fh:
            lines = fh.readlines()
    else:
        lines = sys.stdin.readlines()

    records = list(parse_lines(lines))
    compiled = compile_pattern(args.pattern, ignore_case=args.ignore_case)

    if args.field:
        filtered = filter_by_pattern(records, args.field, compiled, invert=args.invert)
    else:
        filtered = filter_any_field(records, compiled, invert=args.invert)

    write_records(list(filtered), fmt=args.format)


if __name__ == "__main__":
    run_pattern()
