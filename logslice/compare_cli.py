"""CLI entry-point for the compare sub-command."""

import argparse
import json
import sys
from typing import List

from logslice.compare import changed_only, compare_streams
from logslice.parser import parse_lines


def parse_compare_args(argv: List[str] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="logslice compare",
        description="Compare two JSONL log files field-by-field.",
    )
    p.add_argument("left", help="First (baseline) log file")
    p.add_argument("right", help="Second (new) log file")
    p.add_argument(
        "--key",
        default="id",
        metavar="FIELD",
        help="Field used to pair records across files (default: id)",
    )
    p.add_argument(
        "--fields",
        nargs="+",
        metavar="FIELD",
        help="Restrict comparison to these fields",
    )
    p.add_argument(
        "--changed-only",
        action="store_true",
        help="Suppress equal records from output",
    )
    p.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json)",
    )
    return p.parse_args(argv)


def _load(path: str) -> list:
    with open(path) as fh:
        return list(parse_lines(fh))


def run_compare(argv: List[str] = None, out=None) -> None:
    if out is None:
        out = sys.stdout
    args = parse_compare_args(argv)
    left_records = _load(args.left)
    right_records = _load(args.right)
    reports = compare_streams(
        left_records, right_records, key_field=args.key, fields=args.fields
    )
    if args.changed_only:
        reports = changed_only(reports)
    for report in reports:
        if args.format == "json":
            out.write(json.dumps(report) + "\n")
        else:
            status = report["status"]
            key = report["key"]
            if status == "changed":
                fields_changed = ", ".join(report.get("diffs", {}).keys())
                out.write(f"CHANGED key={key} fields=[{fields_changed}]\n")
            else:
                out.write(f"{status.upper()} key={key}\n")
