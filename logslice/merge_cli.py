"""CLI helpers for the merge subcommand."""

import argparse
import sys
from typing import List

from logslice.parser import parse_lines
from logslice.merge import merge_records, merge_sorted, merge_dedupe
from logslice.output import write_records


def parse_merge_args(argv: List[str] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="logslice merge",
        description="Merge two or more log files into one stream.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Input log files (use '-' for stdin).",
    )
    p.add_argument(
        "--sort",
        action="store_true",
        default=False,
        help="Sort merged output by timestamp.",
    )
    p.add_argument(
        "--timestamp-field",
        default="timestamp",
        metavar="FIELD",
        help="Field name containing the timestamp (default: timestamp).",
    )
    p.add_argument(
        "--dedupe",
        metavar="FIELD",
        default=None,
        help="Remove duplicate records sharing the same value for FIELD.",
    )
    p.add_argument(
        "--format",
        choices=["json", "kv", "pretty"],
        default="json",
        help="Output format (default: json).",
    )
    return p.parse_args(argv)


def _load(path: str) -> List[dict]:
    if path == "-":
        return list(parse_lines(sys.stdin))
    with open(path) as fh:
        return list(parse_lines(fh))


def run_merge(argv: List[str] = None) -> None:
    args = parse_merge_args(argv)
    streams = [_load(f) for f in args.files]

    if args.sort:
        records = merge_sorted(*streams, timestamp_field=args.timestamp_field)
    elif args.dedupe:
        records = merge_dedupe(*streams, key_field=args.dedupe)
    else:
        records = merge_records(*streams)

    write_records(records, fmt=args.format, out=sys.stdout)
