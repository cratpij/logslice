"""CLI entry point for cartesian cross-join of two JSONL files."""

import argparse
import sys
from typing import List

from logslice.parser import parse_lines
from logslice.cartesian import cartesian_product, cartesian_with_lookup, dedup_cartesian
from logslice.output import write_records


def parse_cartesian_args(argv: List[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice cartesian",
        description="Cross-join two JSONL files (cartesian product).",
    )
    parser.add_argument("left", help="Path to left JSONL file")
    parser.add_argument("right", help="Path to right JSONL file")
    parser.add_argument(
        "--join-field",
        dest="join_field",
        default=None,
        help="If set, only pair rows where both sides share this field value",
    )
    parser.add_argument(
        "--prefix-left",
        dest="prefix_left",
        default=None,
        help="Prefix to add to all keys from the left file",
    )
    parser.add_argument(
        "--prefix-right",
        dest="prefix_right",
        default=None,
        help="Prefix to add to all keys from the right file",
    )
    parser.add_argument(
        "--dedup-fields",
        dest="dedup_fields",
        default=None,
        help="Comma-separated fields to deduplicate the result on",
    )
    parser.add_argument(
        "--format",
        choices=["json", "kv", "pretty"],
        default="json",
        help="Output format (default: json)",
    )
    return parser.parse_args(argv)


def _load(path: str):
    with open(path) as fh:
        return list(parse_lines(fh))


def run_cartesian(argv: List[str] = None) -> None:
    args = parse_cartesian_args(argv)

    left_records = _load(args.left)
    right_records = _load(args.right)

    if args.join_field:
        results = cartesian_with_lookup(
            left_records, right_records, join_field=args.join_field
        )
    else:
        results = cartesian_product(
            left_records,
            right_records,
            prefix_left=args.prefix_left,
            prefix_right=args.prefix_right,
        )

    if args.dedup_fields:
        fields = [f.strip() for f in args.dedup_fields.split(",")]
        results = dedup_cartesian(results, key_fields=fields)

    write_records(results, fmt=args.format, out=sys.stdout)
