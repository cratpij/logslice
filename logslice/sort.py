"""Sorting utilities for log records."""

from typing import Any, Dict, Iterable, List, Optional
from logslice.filter import parse_timestamp


def sort_by_field(
    records: Iterable[Dict[str, Any]],
    field: str,
    reverse: bool = False,
) -> List[Dict[str, Any]]:
    """Sort records by a given field value (lexicographic)."""
    return sorted(
        records,
        key=lambda r: r.get(field, ""),
        reverse=reverse,
    )


def sort_by_timestamp(
    records: Iterable[Dict[str, Any]],
    field: str = "timestamp",
    reverse: bool = False,
) -> List[Dict[str, Any]]:
    """Sort records by a timestamp field, parsing ISO-8601 strings.

    Records missing the field or with unparseable values are placed last.
    """
    def _key(r: Dict[str, Any]):
        raw = r.get(field)
        if raw is None:
            return (1, None)
        ts = parse_timestamp(str(raw))
        if ts is None:
            return (1, None)
        return (0, ts)

    return sorted(records, key=_key, reverse=reverse)


def sort_by_numeric(
    records: Iterable[Dict[str, Any]],
    field: str,
    reverse: bool = False,
) -> List[Dict[str, Any]]:
    """Sort records by a numeric field value.

    Records where the field is missing or non-numeric are placed last.
    """
    def _key(r: Dict[str, Any]):
        val = r.get(field)
        try:
            return (0, float(val))
        except (TypeError, ValueError):
            return (1, 0.0)

    return sorted(records, key=_key, reverse=reverse)
