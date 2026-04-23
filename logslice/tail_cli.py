"""CLI interface for head/tail/skip operations."""
import argparse
import sys
from typing import Sequence

from logslice.parser import parse_lines
from logslice.output import write_records
from logslice.tail import head_records, tail_records, skip_records


def parse_tail_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice tail",
        description="Select records from the start or end of a log stream.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--head",
        metavar="N",
        type=int,
        default=None,
        help="Keep the first N records.",
    )
    mode.add_argument(
        "--tail",
        metavar="N",
        type=int,
        default=None,
        help="Keep the last N records.",
    )
    parser.add_argument(
        "--skip",
        metavar="N",
        type=int,
        default=0,
        help="Skip the first N records before applying head/tail (default: 0).",
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
        default="-",
        help="Input file (default: stdin).",
    )
    return parser.parse_args(argv)


def run_tail(argv: Sequence[str] | None = None) -> None:
    args = parse_tail_args(argv)

    if args.file == "-":
        lines = sys.stdin
    else:
        lines = open(args.file)  # noqa: SIM115

    records = list(parse_lines(lines))

    if args.skip:
        records = list(skip_records(records, args.skip))

    if args.head is not None:
        records = head_records(records, args.head)
    elif args.tail is not None:
        records = tail_records(records, args.tail)

    write_records(records, fmt=args.format)
