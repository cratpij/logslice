"""CLI integration for the annotate feature."""

import argparse
import sys
from typing import List, Optional

from logslice.annotate import (
    annotate_conditional,
    annotate_with_fn,
    annotate_with_index,
    annotate_with_label,
)
from logslice.parser import parse_lines
from logslice.output import write_records


def parse_annotate_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="logslice annotate",
        description="Annotate log records with labels or computed fields.",
    )
    p.add_argument("input", nargs="?", default="-", help="Input file (default: stdin)")
    p.add_argument("--field", required=True, help="Field name to add/overwrite")

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--label", metavar="VALUE", help="Static label value")
    mode.add_argument(
        "--index", action="store_true", help="Annotate with sequential index"
    )
    mode.add_argument(
        "--condition",
        metavar="EXPR",
        help="Python expression (record as 'r') for conditional annotation",
    )

    p.add_argument("--true-value", default="true", help="Value when condition is true")
    p.add_argument("--false-value", default="false", help="Value when condition is false")
    p.add_argument("--start", type=int, default=0, help="Start index (with --index)")
    p.add_argument(
        "--format",
        choices=["json", "kv", "pretty"],
        default="json",
        dest="fmt",
    )
    return p.parse_args(argv)


def run_annotate(argv: Optional[List[str]] = None) -> None:
    args = parse_annotate_args(argv)

    if args.input == "-":
        lines = sys.stdin
    else:
        lines = open(args.input)

    records = list(parse_lines(lines))

    if args.label is not None:
        out = annotate_with_label(records, args.field, args.label)
    elif args.index:
        out = annotate_with_index(records, field=args.field, start=args.start)
    else:
        expr = args.condition
        condition = lambda r, _e=expr: bool(eval(_e, {"r": r}))  # noqa: E731
        out = annotate_conditional(
            records, args.field, condition, args.true_value, args.false_value
        )

    write_records(out, fmt=args.fmt)
