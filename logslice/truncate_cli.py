"""CLI integration for truncating long field values in log records."""

import argparse
import sys
import json

from logslice.parser import parse_lines
from logslice.truncate import truncate_fields, truncate_all
from logslice.output import write_records


def parse_truncate_args(argv=None):
    """Build and parse CLI arguments for the truncate subcommand.

    Args:
        argv: Argument list (defaults to sys.argv if None).

    Returns:
        Parsed namespace with truncate options.
    """
    parser = argparse.ArgumentParser(
        prog="logslice truncate",
        description="Truncate long string field values in structured log records.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input file path (default: stdin).",
    )
    parser.add_argument(
        "--fields",
        nargs="+",
        metavar="FIELD",
        help="Specific fields to truncate. If omitted, all string fields are truncated.",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=100,
        metavar="N",
        help="Maximum character length for field values (default: 100).",
    )
    parser.add_argument(
        "--suffix",
        default="...",
        help="Suffix appended to truncated values (default: '...').",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "kv", "pretty"],
        default="json",
        help="Output format (default: json).",
    )
    return parser.parse_args(argv)


def run_truncate(argv=None, stdout=None, stdin=None):
    """Execute the truncate command.

    Reads log records from a file or stdin, truncates string field values
    according to the specified options, and writes the results.

    Args:
        argv: CLI argument list.
        stdout: Output stream (defaults to sys.stdout).
        stdin: Input stream (defaults to sys.stdin).
    """
    if stdout is None:
        stdout = sys.stdout
    if stdin is None:
        stdin = sys.stdin

    args = parse_truncate_args(argv)

    # Read input lines
    if args.input == "-":
        lines = stdin.read().splitlines()
    else:
        try:
            with open(args.input, "r") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)

    records = list(parse_lines(lines))

    if not records:
        return

    # Apply truncation
    if args.fields:
        result = truncate_fields(records, args.fields, args.max_length, args.suffix)
    else:
        result = truncate_all(records, args.max_length, args.suffix)

    write_records(list(result), fmt=args.output_format, out=stdout)
