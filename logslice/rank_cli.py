"""CLI integration for the rank feature."""

import argparse
import json
import sys
from typing import List

from logslice.rank import rank_records, rank_within_group, top_ranked


def parse_rank_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="logslice rank",
        description="Rank log records by a numeric field.",
    )
    parser.add_argument("field", help="Numeric field to rank by")
    parser.add_argument(
        "--rank-field", default="rank", help="Output field name for rank (default: rank)"
    )
    parser.add_argument(
        "--group-by", default=None, metavar="FIELD",
        help="Rank within groups defined by this field",
    )
    parser.add_argument(
        "--desc", action="store_true", help="Rank in descending order (highest value = rank 1)"
    )
    parser.add_argument(
        "--dense", action="store_true", help="Use dense ranking (no gaps after ties)"
    )
    parser.add_argument(
        "--top", type=int, default=None, metavar="N",
        help="Only emit records with rank <= N",
    )
    parser.add_argument(
        "--input", "-i", default="-", help="Input file (default: stdin)"
    )
    return parser.parse_args(argv)


def run_rank(argv: List[str]) -> None:
    args = parse_rank_args(argv)

    if args.input == "-":
        lines = sys.stdin
    else:
        lines = open(args.input)  # noqa: WPS515

    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if args.input != "-":
        lines.close()  # type: ignore[union-attr]

    ascending = not args.desc

    if args.group_by:
        ranked = rank_within_group(
            records,
            field=args.field,
            group_field=args.group_by,
            rank_field=args.rank_field,
            ascending=ascending,
            dense=args.dense,
        )
    else:
        ranked = rank_records(
            records,
            field=args.field,
            rank_field=args.rank_field,
            ascending=ascending,
            dense=args.dense,
        )

    output = list(top_ranked(ranked, args.rank_field, args.top)) if args.top else ranked

    for record in output:
        print(json.dumps(record))
