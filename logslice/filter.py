"""Filter parsed log entries by time range or field value."""

from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

LogEntry = Dict[str, Any]


def parse_timestamp(value: str) -> Optional[datetime]:
    """Try to parse a timestamp string into a datetime object."""
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    return None


def filter_by_time(
    entries: Iterator[LogEntry],
    timestamp_field: str = "timestamp",
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Iterator[LogEntry]:
    """Yield entries whose timestamp falls within [start, end]."""
    for entry in entries:
        raw = entry.get(timestamp_field)
        if raw is None:
            continue
        ts = parse_timestamp(str(raw))
        if ts is None:
            continue
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        yield entry


def filter_by_field(
    entries: Iterator[LogEntry],
    field: str,
    value: Any,
) -> Iterator[LogEntry]:
    """Yield entries where entry[field] == value."""
    for entry in entries:
        if entry.get(field) == value:
            yield entry


def filter_by_field_contains(
    entries: Iterator[LogEntry],
    field: str,
    substring: str,
) -> Iterator[LogEntry]:
    """Yield entries where str(entry[field]) contains substring."""
    for entry in entries:
        field_val = entry.get(field)
        if field_val is not None and substring in str(field_val):
            yield entry
