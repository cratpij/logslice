"""CLI helpers for enrich subcommand."""

import argparse
import sys
from typing import List

from logslice.parser import parse_lines
from logslice.enrich import enrich_with_constant, enrich_with_hour, enrich_with_date
from logslice.output import write_records


def parse_enrich_args(argv: List[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice enrich",
        description="Enrich log records with derived fields.",
    )
    parser.add_argument("input", nargs="?", help="Input file (default: stdin)")
    parser.add_argument("--add-hour", action="store_true", help="Add 'hour' field from timestamp")
    parser.add_argument("--add-date", action="store_true", help="Add 'date' field from timestamp")
    parser.add_argument(
        "--constant",
        metavar="FIELD=VALUE",
        action="append",
        default=[],
        help="Add constant field if absent (repeatable)",
    )
    parser.add_argument(
        "--ts-field",
        default="timestamp",
        help="Timestamp field name (default: timestamp)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "kv", "pretty"],
        default="json",
        help="Output format",
    )
    return parser.parse_args(argv)


def run_enrich(argv: List[str] = None) -> None:
    args = parse_enrich_args(argv)

    if args.input:
        with open(args.input) as fh:
            lines = fh.readlines()
    else:
        lines = sys.stdin.readlines()

    records = list(parse_lines(lines))

    for pair in args.constant:
        if "=" not in pair:
            print(f"Invalid --constant value: {pair!r}", file=sys.stderr)
            sys.exit(1)
        field, value = pair.split("=", 1)
        records = enrich_with_constant(records, field.strip(), value.strip())

    if args.add_hour:
        records = enrich_with_hour(records, ts_field=args.ts_field)

    if args.add_date:
        records = enrich_with_date(records, ts_field=args.ts_field)

    write_records(records, fmt=args.format, out=sys.stdout)
