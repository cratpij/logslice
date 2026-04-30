"""CLI interface for the segment module."""

import argparse
import json
import sys
from typing import List, Optional

from logslice.parser import parse_lines
from logslice.segment import segment_by_field, segment_counts, split_segments


def parse_segment_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice segment",
        description="Tag records with a segment label based on field boundaries.",
    )
    parser.add_argument("--field", required=True, help="Field to segment on.")
    parser.add_argument(
        "--boundary",
        dest="boundaries",
        metavar="THRESHOLD:LABEL",
        action="append",
        default=[],
        help="Boundary in THRESHOLD:LABEL format. Repeatable.",
    )
    parser.add_argument(
        "--default", default="other", help="Label for records below all thresholds."
    )
    parser.add_argument(
        "--counts",
        action="store_true",
        help="Output segment counts instead of tagged records.",
    )
    parser.add_argument(
        "--segment-field",
        default="_segment",
        help="Output field name for the segment label (default: _segment).",
    )
    return parser.parse_args(argv)


def _parse_boundaries(raw: List[str]):
    result = []
    for item in raw:
        if ":" not in item:
            raise ValueError(f"Invalid boundary format (expected THRESHOLD:LABEL): {item!r}")
        threshold, label = item.split(":", 1)
        result.append((threshold, label))
    return sorted(result, key=lambda x: x[0])


def run_segment(argv: Optional[List[str]] = None) -> None:
    args = parse_segment_args(argv)
    boundaries = _parse_boundaries(args.boundaries)

    lines = sys.stdin
    records = list(parse_lines(lines))

    tagged = list(
        segment_by_field(records, args.field, boundaries, default=args.default)
    )

    # Rename _segment if a custom field name was requested
    if args.segment_field != "_segment":
        tagged = [
            {**{k: v for k, v in r.items() if k != "_segment"}, args.segment_field: r["_segment"]}
            for r in tagged
        ]

    if args.counts:
        counts = segment_counts(tagged, segment_field=args.segment_field)
        for label, count in sorted(counts.items()):
            print(json.dumps({"segment": label, "count": count}))
    else:
        for record in tagged:
            print(json.dumps(record))
