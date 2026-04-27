"""CLI integration for the timeline feature."""

from __future__ import annotations

import argparse
import sys
from typing import List

from logslice.parser import parse_lines
from logslice.timeline import build_timeline, render_timeline, timeline_counts
from logslice.output import write_records


def _parse_interval(value: str) -> int:
    """Parse an interval string like '60', '5m', '1h' into seconds."""
    value = value.strip()
    if value.endswith("h"):
        return int(value[:-1]) * 3600
    if value.endswith("m"):
        return int(value[:-1]) * 60
    if value.endswith("s"):
        return int(value[:-1])
    return int(value)


def parse_timeline_args(argv: List[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="logslice timeline",
        description="Produce a timeline summary of log records grouped by time bucket.",
    )
    p.add_argument("file", nargs="?", default="-", help="Input file (default: stdin)")
    p.add_argument(
        "--interval", default="60",
        help="Bucket size: integer seconds or suffix 'm'/'h' (default: 60)",
    )
    p.add_argument(
        "--ts-field", default="timestamp",
        help="Field containing the timestamp (default: timestamp)",
    )
    p.add_argument(
        "--counts", action="store_true",
        help="Output JSONL count records instead of ASCII chart",
    )
    p.add_argument(
        "--bar-char", default="#",
        help="Character used for bar chart bars (default: #)",
    )
    p.add_argument(
        "--max-width", type=int, default=40,
        help="Maximum bar width in characters (default: 40)",
    )
    return p.parse_args(argv)


def run_timeline(argv: List[str] | None = None) -> None:
    args = parse_timeline_args(argv)
    bucket_seconds = _parse_interval(args.interval)

    if args.file == "-":
        lines = sys.stdin
    else:
        lines = open(args.file)

    try:
        records = list(parse_lines(lines))
    finally:
        if args.file != "-":
            lines.close()

    if args.counts:
        results = timeline_counts(records, bucket_seconds=bucket_seconds, ts_field=args.ts_field)
        write_records(results, sys.stdout, fmt="json")
    else:
        tl = build_timeline(records, bucket_seconds=bucket_seconds, ts_field=args.ts_field)
        print(render_timeline(tl, bar_char=args.bar_char, max_width=args.max_width))
