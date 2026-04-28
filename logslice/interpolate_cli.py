"""CLI integration for the interpolate module."""

import argparse
import sys
from typing import List

from logslice.interpolate import fill_constant, fill_forward, fill_backward, fill_linear
from logslice.parser import parse_lines
from logslice.output import write_records


def parse_interpolate_args(argv: List[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice interpolate",
        description="Fill missing field values in log records.",
    )
    parser.add_argument("field", help="Field name to interpolate.")
    parser.add_argument(
        "--mode",
        choices=["forward", "backward", "constant", "linear"],
        default="forward",
        help="Interpolation strategy (default: forward).",
    )
    parser.add_argument(
        "--value",
        default=None,
        help="Constant value to use with --mode=constant.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "kv", "pretty"],
        default="json",
        dest="output_format",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input file (default: stdin).",
    )
    return parser.parse_args(argv)


def run_interpolate(argv: List[str] = None) -> None:
    args = parse_interpolate_args(argv)

    if args.input == "-":
        lines = sys.stdin
    else:
        lines = open(args.input)

    try:
        records = list(parse_lines(lines))
    finally:
        if args.input != "-":
            lines.close()

    mode = args.mode
    field = args.field

    if mode == "forward":
        result = fill_forward(records, field)
    elif mode == "backward":
        result = fill_backward(records, field)
    elif mode == "constant":
        if args.value is None:
            print("error: --value is required for --mode=constant", file=sys.stderr)
            sys.exit(1)
        result = list(fill_constant(records, field, args.value))
    elif mode == "linear":
        result = fill_linear(records, field)
    else:
        result = records

    write_records(result, fmt=args.output_format)
