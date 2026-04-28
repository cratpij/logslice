"""Clamp numeric field values to a specified [min, max] range."""

from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

Record = Dict[str, Any]
Numeric = Union[int, float]


def clamp_field(
    record: Record,
    field: str,
    min_val: Optional[Numeric] = None,
    max_val: Optional[Numeric] = None,
) -> Record:
    """Return a new record with *field* clamped to [min_val, max_val].

    Non-numeric values and missing fields are passed through unchanged.
    """
    if field not in record:
        return record
    value = record[field]
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return record
    if min_val is not None and numeric < min_val:
        numeric = min_val
    if max_val is not None and numeric > max_val:
        numeric = max_val
    # Preserve int type when both original value and result are integral.
    if isinstance(value, int) and numeric == int(numeric):
        numeric = int(numeric)
    return {**record, field: numeric}


def clamp_fields(
    record: Record,
    fields: List[str],
    min_val: Optional[Numeric] = None,
    max_val: Optional[Numeric] = None,
) -> Record:
    """Clamp multiple fields in a single pass."""
    result = record
    for field in fields:
        result = clamp_field(result, field, min_val=min_val, max_val=max_val)
    return result


def clamp_records(
    records: Iterable[Record],
    fields: List[str],
    min_val: Optional[Numeric] = None,
    max_val: Optional[Numeric] = None,
) -> Iterator[Record]:
    """Lazily clamp *fields* across all *records*."""
    for record in records:
        yield clamp_fields(record, fields, min_val=min_val, max_val=max_val)
