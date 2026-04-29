"""CLI interface for the rollup command."""

import argparse
import json
import sys
from typing import List, Optional

from logslice.parser import parse_lines
from logslice.rollup import rollup, rollup_count_only, rollup_multi
from logslice.output import write_records


def parse_rollup_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice rollup",
        description="Aggregate records grouped by a field with summary statistics.",
    )
    parser.add_argument("file", nargs="?", default="-", help="Input file (default: stdin)")
    parser.add_argument(
        "--group", required=True, metavar="FIELD",
        help="Field to group by",
    )
    parser.add_argument(
        "--value", metavar="FIELD", action="append", dest="value_fields",
        help="Numeric field(s) to aggregate (may be repeated)",
    )
    parser.add_argument(
        "--count-only", action="store_true",
        help="Only output counts, no numeric aggregation",
    )
    parser.add_argument(
        "--format", choices=["json", "kv", "pretty"], default="json",
        help="Output format (default: json)",
    )
    return parser.parse_args(argv)


def run_rollup(argv: Optional[List[str]] = None) -> None:
    args = parse_rollup_args(argv)

    if args.file == "-":
        lines = sys.stdin
    else:
        lines = open(args.file, "r", encoding="utf-8")

    try:
        records = list(parse_lines(lines))
    finally:
        if args.file != "-":
            lines.close()

    if args.count_only:
        results = rollup_count_only(records, group_field=args.group)
    elif args.value_fields and len(args.value_fields) > 1:
        results = rollup_multi(
            records,
            group_field=args.group,
            value_fields=args.value_fields,
        )
    elif args.value_fields:
        results = rollup(
            records,
            group_field=args.group,
            value_field=args.value_fields[0],
        )
    else:
        results = rollup_count_only(records, group_field=args.group)

    write_records(results, fmt=args.format, out=sys.stdout)


if __name__ == "__main__":
    run_rollup()
