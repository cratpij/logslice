"""Output formatting for logslice results."""
import json
from typing import Any, Dict, Iterable, TextIO
import sys


def format_json(record: Dict[str, Any]) -> str:
    """Serialize a record back to a compact JSON string."""
    return json.dumps(record, default=str)


def format_kv(record: Dict[str, Any]) -> str:
    """Serialize a record as key=value pairs."""
    parts = []
    for key, value in record.items():
        if isinstance(value, str) and " " in value:
            parts.append(f'{key}="{value}"')
        else:
            parts.append(f"{key}={value}")
    return " ".join(parts)


def format_pretty(record: Dict[str, Any]) -> str:
    """Serialize a record as indented JSON."""
    return json.dumps(record, indent=2, default=str)


FORMATTERS = {
    "json": format_json,
    "kv": format_kv,
    "pretty": format_pretty,
}


def write_records(
    records: Iterable[Dict[str, Any]],
    fmt: str = "json",
    out: TextIO = sys.stdout,
) -> int:
    """Write records to *out* using the given format. Returns count written."""
    formatter = FORMATTERS.get(fmt)
    if formatter is None:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {list(FORMATTERS)}.")

    count = 0
    for record in records:
        out.write(formatter(record) + "\n")
        count += 1
    return count
