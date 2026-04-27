"""CLI integration for the resample command."""

import argparse
import sys
from typing import List, Optional

from logslice.parser import parse_lines
from logslice.resample import resample_count, resample_sum, resample_avg
from logslice.output import write_records


_INTERVAL_SUFFIXES = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def _parse_interval(value: str) -> int:
    """Parse interval strings like '60', '5m', '1h' into seconds."""
    value = value.strip()
    if value[-1].lower() in _INTERVAL_SUFFIXES:
        multiplier = _INTERVAL_SUFFIXES[value[-1].lower()]
        return int(value[:-1]) * multiplier
    return int(value)


def parse_resample_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice resample",
        description="Resample log records into fixed time buckets.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Input file (default: stdin)",
    )
    parser.add_argument(
        "--interval",
        required=True,
        help="Bucket size, e.g. 60, 5m, 1h",
    )
    parser.add_argument(
        "--mode",
        choices=["count", "sum", "avg"],
        default="count",
        help="Aggregation mode (default: count)",
    )
    parser.add_argument(
        "--field",
        default=None,
        help="Numeric field to aggregate (required for sum/avg)",
    )
    parser.add_argument(
        "--ts-field",
        default="timestamp",
        dest="ts_field",
        help="Timestamp field name (default: timestamp)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "kv", "pretty"],
        default="json",
        dest="output_format",
    )
    return parser.parse_args(argv)


def run_resample(argv: Optional[List[str]] = None) -> None:
    args = parse_resample_args(argv)
    interval = _parse_interval(args.interval)

    if args.mode in ("sum", "avg") and not args.field:
        print(
            f"error: --field is required for --mode {args.mode}", file=sys.stderr
        )
        sys.exit(1)

    fh = open(args.file) if args.file != "-" else sys.stdin
    try:
        records = list(parse_lines(fh))
    finally:
        if args.file != "-":
            fh.close()

    if args.mode == "count":
        results = resample_count(records, interval, ts_field=args.ts_field)
    elif args.mode == "sum":
        results = resample_sum(records, args.field, interval, ts_field=args.ts_field)
    else:
        results = resample_avg(records, args.field, interval, ts_field=args.ts_field)

    write_records(list(results), fmt=args.output_format)
