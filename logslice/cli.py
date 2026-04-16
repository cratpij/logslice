"""Command-line interface for logslice."""
import argparse
import sys
from typing import List, Optional

from logslice.parser import parse_lines
from logslice.slicer import Slicer
from logslice.output import write_records


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Filter and slice structured log files by time range or field value.",
    )
    p.add_argument("file", nargs="?", help="Log file to read (default: stdin)")
    p.add_argument("--start", metavar="TS", help="Include records at or after this timestamp")
    p.add_argument("--end", metavar="TS", help="Include records before or at this timestamp")
    p.add_argument(
        "--where", metavar="FIELD=VALUE", action="append", default=[],
        help="Exact field filter (repeatable)",
    )
    p.add_argument(
        "--contains", metavar="FIELD=SUBSTR", action="append", default=[],
        help="Substring field filter (repeatable)",
    )
    p.add_argument(
        "--fmt", choices=["json", "kv", "pretty"], default="json",
        help="Output format (default: json)",
    )
    p.add_argument("--ts-field", default="timestamp", help="Timestamp field name")
    return p


def _split_kv(items: List[str], flag: str):
    pairs = []
    for item in items:
        if "=" not in item:
            print(f"logslice: error: {flag} value must be FIELD=VALUE, got: {item}", file=sys.stderr)
            sys.exit(1)
        field, _, value = item.partition("=")
        pairs.append((field.strip(), value.strip()))
    return pairs


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.file:
        try:
            fh = open(args.file)
        except OSError as exc:
            print(f"logslice: error: {exc}", file=sys.stderr)
            return 1
    else:
        fh = sys.stdin

    try:
        lines = fh.read().splitlines()
    finally:
        if args.file:
            fh.close()

    records = list(parse_lines(lines))
    slicer = Slicer(records, ts_field=args.ts_field)

    if args.start or args.end:
        slicer = slicer.time_range(args.start, args.end)

    for field, value in _split_kv(args.where, "--where"):
        slicer = slicer.where(field, value)

    for field, substr in _split_kv(args.contains, "--contains"):
        slicer = slicer.where_contains(field, substr)

    count = write_records(slicer.results(), fmt=args.fmt)
    return 0 if count >= 0 else 1


if __name__ == "__main__":
    sys.exit(run())
