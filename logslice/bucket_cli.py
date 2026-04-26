"""CLI support for the bucket command."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from logslice.bucket import bucket_counts, bucket_records
from logslice.parser import parse_lines
from logslice.output import write_records


def parse_bucket_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice bucket",
        description="Bucket records by a numeric field into fixed-size ranges.",
    )
    parser.add_argument("field", help="Numeric field to bucket on")
    parser.add_argument(
        "--size",
        type=float,
        default=10.0,
        metavar="N",
        help="Bucket width (default: 10)",
    )
    parser.add_argument(
        "--count-only",
        action="store_true",
        help="Output bucket label and count only (no records)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "kv", "pretty"],
        default="json",
        help="Output format when emitting records (default: json)",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input file (default: stdin)",
    )
    return parser.parse_args(argv)


def run_bucket(argv: List[str] | None = None) -> None:
    args = parse_bucket_args(argv)

    if args.input == "-":
        lines = sys.stdin
    else:
        lines = open(args.input)  # noqa: WPS515 — caller closes via context

    try:
        records = list(parse_lines(lines))
    finally:
        if args.input != "-":
            lines.close()

    if args.count_only:
        counts = bucket_counts(records, args.field, args.size)
        for label, count in counts.items():
            print(json.dumps({"bucket": label, "count": count}))
        return

    grouped = bucket_records(records, args.field, args.size)
    for label, bucket_recs in grouped.items():
        for rec in bucket_recs:
            annotated = {"__bucket": label, **rec}
            write_records([annotated], fmt=args.format, out=sys.stdout)
