"""CLI helpers for the diff feature."""
import argparse
import json
import sys
from logslice.parser import parse_lines
from logslice.diff import diff_by_field, diff_field_values, count_diff


def parse_diff_args(argv=None):
    p = argparse.ArgumentParser(prog="logslice diff", description="Diff two log files")
    p.add_argument("left", help="First log file")
    p.add_argument("right", help="Second log file")
    p.add_argument("--key", required=True, help="Field to match records on")
    p.add_argument(
        "--mode",
        choices=["summary", "only-left", "only-right", "changes"],
        default="summary",
    )
    return p.parse_args(argv)


def _load(path: str) -> list[dict]:
    with open(path) as f:
        return list(parse_lines(f))


def run_diff(argv=None):
    args = parse_diff_args(argv)
    try:
        left = _load(args.left)
        right = _load(args.right)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    key = args.key

    if args.mode == "summary":
        c = count_diff(left, right, key)
        print(json.dumps(c))
    elif args.mode == "only-left":
        result = diff_by_field(left, right, key)["only_left"]
        for r in result:
            print(json.dumps(r))
    elif args.mode == "only-right":
        result = diff_by_field(left, right, key)["only_right"]
        for r in result:
            print(json.dumps(r))
    elif args.mode == "changes":
        result = diff_field_values(left, right, key)
        for r in result:
            print(json.dumps(r))
