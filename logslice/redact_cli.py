"""CLI integration for redact feature."""

import argparse
import sys
from typing import List, Optional

from logslice.redact import redact_all, redact_pattern
from logslice.parser import parse_lines
from logslice.output import write_records


def parse_redact_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="logslice redact", description="Redact fields from log records")
    parser.add_argument("file", nargs="?", help="Input log file (default: stdin)")
    parser.add_argument("-f", "--field", action="append", dest="fields", default=[], metavar="FIELD",
                        help="Field to redact (repeatable)")
    parser.add_argument("--pattern", metavar="FIELD:REGEX",
                        help="Redact regex match in field, e.g. msg:token=\\w+")
    parser.add_argument("--mask", default="***", help="Replacement mask string (default: ***)")
    parser.add_argument("--format", choices=["json", "kv", "pretty"], default="json",
                        dest="fmt", help="Output format")
    return parser.parse_args(argv)


def run_redact(argv: Optional[List[str]] = None) -> None:
    args = parse_redact_args(argv)

    if args.file:
        with open(args.file) as fh:
            lines = fh.readlines()
    else:
        lines = sys.stdin.readlines()

    records = list(parse_lines(lines))

    if args.fields:
        records = list(redact_all(records, args.fields, mask=args.mask))

    if args.pattern:
        if ":" not in args.pattern:
            print("--pattern must be in FIELD:REGEX format", file=sys.stderr)
            sys.exit(1)
        field, _, pattern = args.pattern.partition(":")
        records = [redact_pattern(r, field, pattern, mask=args.mask) for r in records]

    write_records(records, fmt=args.fmt)
