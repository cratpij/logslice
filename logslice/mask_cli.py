"""CLI integration for field masking."""

import argparse
import sys
from typing import List, Optional

from logslice.mask import mask_fields, mask_pattern, mask_records
from logslice.parser import parse_lines
from logslice.output import write_records


def parse_mask_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice mask",
        description="Partially mask field values in log records.",
    )
    parser.add_argument("input", nargs="?", help="Input file (default: stdin)")
    parser.add_argument(
        "-f", "--fields",
        nargs="+",
        metavar="FIELD",
        default=[],
        help="Fields to mask",
    )
    parser.add_argument(
        "--visible-start",
        type=int,
        default=0,
        metavar="N",
        help="Number of characters to leave visible at the start (default: 0)",
    )
    parser.add_argument(
        "--visible-end",
        type=int,
        default=0,
        metavar="N",
        help="Number of characters to leave visible at the end (default: 0)",
    )
    parser.add_argument(
        "--char",
        default="*",
        help="Mask character (default: *)",
    )
    parser.add_argument(
        "--pattern",
        metavar="REGEX",
        help="Regex pattern to mask within field value",
    )
    parser.add_argument(
        "--pattern-field",
        metavar="FIELD",
        help="Field to apply --pattern to",
    )
    parser.add_argument(
        "--pattern-replacement",
        default="***",
        metavar="TEXT",
        help="Replacement text for pattern matches (default: ***)",
    )
    parser.add_argument(
        "-o", "--output-format",
        choices=["json", "kv", "pretty"],
        default="json",
        help="Output format (default: json)",
    )
    return parser.parse_args(argv)


def run_mask(argv: Optional[List[str]] = None) -> None:
    args = parse_mask_args(argv)

    if args.input:
        with open(args.input) as fh:
            lines = fh.readlines()
    else:
        lines = sys.stdin.readlines()

    records = list(parse_lines(lines))

    if args.fields:
        records = mask_records(
            records,
            args.fields,
            visible_start=args.visible_start,
            visible_end=args.visible_end,
            char=args.char,
        )

    if args.pattern and args.pattern_field:
        records = [
            mask_pattern(r, args.pattern_field, args.pattern, args.pattern_replacement)
            for r in records
        ]

    write_records(records, fmt=args.output_format)
