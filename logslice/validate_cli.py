"""CLI helpers for validate command integration."""
import json
import sys
from typing import List, Optional

from logslice.validate import validate_schema, partition_valid


def parse_type_map(type_args: Optional[List[str]]) -> dict:
    """Parse list of 'field:type' strings into {field: type} dict.

    Supported type names: str, int, float, bool.
    """
    type_map = {}
    type_lookup = {"str": str, "int": int, "float": float, "bool": bool}
    for arg in (type_args or []):
        if ":" not in arg:
            raise ValueError(f"Invalid type spec '{arg}', expected field:type")
        field, type_name = arg.split(":", 1)
        if type_name not in type_lookup:
            raise ValueError(f"Unknown type '{type_name}', choose from {list(type_lookup)}")
        type_map[field] = type_lookup[type_name]
    return type_map


def run_validate(
    records: List[dict],
    required: Optional[List[str]] = None,
    type_args: Optional[List[str]] = None,
    show_errors: bool = False,
    out=None,
    err=None,
) -> int:
    """Validate records and write results. Returns exit code (0=all valid, 1=some invalid)."""
    if out is None:
        out = sys.stdout
    if err is None:
        err = sys.stderr

    try:
        types = parse_type_map(type_args)
    except ValueError as e:
        err.write(f"error: {e}\n")
        return 2

    valid, invalid = partition_valid(records, required=required, types=types or None)

    if show_errors:
        for record in invalid:
            errors = validate_schema(record, required=required, types=types or None)
            out.write(json.dumps({"record": record, "errors": errors}) + "\n")
    else:
        for record in valid:
            out.write(json.dumps(record) + "\n")

    if invalid:
        err.write(f"{len(invalid)} invalid record(s) found\n")
        return 1
    return 0
