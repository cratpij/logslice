"""CLI integration for window aggregations."""

import argparse
import json
import sys
from typing import List

from logslice.parser import parse_lines
from logslice.window import tumbling_windows, sliding_windows


def parse_window_args(argv: List[str] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="logslice window",
        description="Aggregate log records into time windows.",
    )
    p.add_argument("file", nargs="?", default="-", help="Input file (default: stdin)")
    p.add_argument(
        "--mode",
        choices=["tumbling", "sliding"],
        default="tumbling",
        help="Window mode (default: tumbling)",
    )
    p.add_argument(
        "--window", type=float, default=60.0, metavar="SECONDS",
        help="Window size in seconds (default: 60)",
    )
    p.add_argument(
        "--step", type=float, default=None, metavar="SECONDS",
        help="Step size for sliding windows (default: same as --window)",
    )
    p.add_argument(
        "--ts-field", default="timestamp", metavar="FIELD",
        help="Timestamp field name (default: timestamp)",
    )
    p.add_argument(
        "--count-only", action="store_true",
        help="Emit only window start, end, and record count",
    )
    return p.parse_args(argv)


def run_window(argv: List[str] = None) -> None:
    args = parse_window_args(argv)

    if args.file == "-":
        lines = sys.stdin
    else:
        lines = open(args.file)

    records = list(parse_lines(lines))

    if args.mode == "tumbling":
        windows = tumbling_windows(records, args.window, ts_field=args.ts_field)
    else:
        step = args.step if args.step is not None else args.window
        windows = sliding_windows(records, args.window, step, ts_field=args.ts_field)

    for w in windows:
        if args.count_only:
            out = {
                "start": w["start"].isoformat(),
                "end": w["end"].isoformat(),
                "count": len(w["records"]),
            }
        else:
            out = {
                "start": w["start"].isoformat(),
                "end": w["end"].isoformat(),
                "count": len(w["records"]),
                "records": w["records"],
            }
        print(json.dumps(out))
