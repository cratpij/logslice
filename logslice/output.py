"""Output formatting for logslice records."""

import json
from typing import Any, IO

from logslice.highlight import highlight_record


def format_json(record: dict[str, Any], indent: int | None = None) -> str:
    """Serialize record as JSON. No trailing newline."""
    return json.dumps(record, indent=indent, default=str)


def format_kv(record: dict[str, Any]) -> str:
    """Serialize record as key=value pairs."""
    parts = []
    for k, v in record.items():
        sv = str(v)
        if " " in sv or "=" in sv:
            sv = f'"{sv}"'
        parts.append(f"{k}={sv}")
    return " ".join(parts)


def format_pretty(record: dict[str, Any]) -> str:
    """Return a human-friendly highlighted line for terminal output."""
    return highlight_record(record)


def write_records(
    records: list[dict[str, Any]],
    fmt: str = "json",
    out: IO[str] | None = None,
    indent: int | None = None,
) -> None:
    """Write formatted records to *out* (defaults to stdout)."""
    import sys

    if out is None:
        out = sys.stdout

    formatters = {
        "json": lambda r: format_json(r, indent=indent),
        "kv": format_kv,
        "pretty": format_pretty,
    }

    formatter = formatters.get(fmt)
    if formatter is None:
        raise ValueError(f"Unknown format: {fmt!r}")

    for record in records:
        out.write(formatter(record) + "\n")
