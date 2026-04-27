"""CLI integration for the score module."""

import argparse
import json
import sys
from typing import List, Optional

from logslice.parser import parse_lines
from logslice.score import filter_min_score, score_records, top_scored
from logslice.output import write_records


def parse_score_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="logslice score",
        description="Score records by field-value matches.",
    )
    p.add_argument(
        "criteria",
        nargs="+",
        metavar="FIELD=VALUE",
        help="Criteria to match, e.g. level=error service=auth",
    )
    p.add_argument(
        "--weight",
        type=float,
        default=1.0,
        help="Score weight per matching criterion (default: 1.0)",
    )
    p.add_argument(
        "--min-score",
        type=float,
        default=None,
        metavar="N",
        help="Exclude records with score below N",
    )
    p.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="Return only the top N highest-scoring records",
    )
    p.add_argument(
        "--fmt",
        choices=["json", "kv", "pretty"],
        default="json",
        help="Output format (default: json)",
    )
    return p.parse_args(argv)


def _parse_criteria(raw: List[str]) -> dict:
    result = {}
    for item in raw:
        if "=" not in item:
            raise ValueError(f"Invalid criterion {item!r}: expected FIELD=VALUE")
        field, _, value = item.partition("=")
        result[field.strip()] = value.strip()
    return result


def run_score(argv: Optional[List[str]] = None) -> None:
    args = parse_score_args(argv)
    criteria = _parse_criteria(args.criteria)
    records = list(parse_lines(sys.stdin))
    scored = score_records(records, criteria, weight=args.weight)
    if args.min_score is not None:
        scored = filter_min_score(scored, args.min_score)
    if args.top is not None:
        scored = top_scored(scored, args.top)
    write_records(scored, fmt=args.fmt, out=sys.stdout)
