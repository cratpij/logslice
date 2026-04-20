"""Truncate long field values in log records."""

from typing import Any, Dict, List, Optional

Record = Dict[str, Any]


def truncate_field(
    record: Record,
    field: str,
    max_length: int,
    suffix: str = "...",
) -> Record:
    """Return a new record with the given field truncated to max_length characters.

    If the field value is not a string or is shorter than max_length, the record
    is returned unchanged (still a shallow copy).
    """
    result = dict(record)
    value = result.get(field)
    if isinstance(value, str) and len(value) > max_length:
        cut = max(0, max_length - len(suffix))
        result[field] = value[:cut] + suffix
    return result


def truncate_fields(
    record: Record,
    fields: List[str],
    max_length: int,
    suffix: str = "...",
) -> Record:
    """Truncate multiple fields in a single record."""
    result = dict(record)
    for field in fields:
        result = truncate_field(result, field, max_length, suffix)
    return result


def truncate_all(
    record: Record,
    max_length: int,
    suffix: str = "...",
    skip: Optional[List[str]] = None,
) -> Record:
    """Truncate every string field in the record, optionally skipping some fields."""
    skip_set = set(skip or [])
    result = dict(record)
    for key, value in result.items():
        if key in skip_set:
            continue
        if isinstance(value, str) and len(value) > max_length:
            cut = max(0, max_length - len(suffix))
            result[key] = value[:cut] + suffix
    return result


def truncate_records(
    records: List[Record],
    field: str,
    max_length: int,
    suffix: str = "...",
) -> List[Record]:
    """Apply truncate_field to a list of records."""
    return [truncate_field(r, field, max_length, suffix) for r in records]
