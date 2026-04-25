"""coalesce.py — pick the first non-None / non-empty value across candidate fields."""

from typing import Any, Dict, Iterable, List, Optional


def coalesce_fields(
    record: Dict[str, Any],
    fields: List[str],
    target: str,
    *,
    skip_empty: bool = True,
) -> Dict[str, Any]:
    """Return a copy of *record* with *target* set to the first non-absent value
    found by scanning *fields* in order.

    Parameters
    ----------
    record:      source log record.
    fields:      candidate field names to inspect, in priority order.
    target:      destination field name to write the resolved value into.
    skip_empty:  when True (default) treat empty-string values as absent.
    """
    result = dict(record)
    for field in fields:
        value = record.get(field)
        if value is None:
            continue
        if skip_empty and value == "":
            continue
        result[target] = value
        return result
    # no candidate found — leave target absent (don't overwrite with None)
    return result


def coalesce_records(
    records: Iterable[Dict[str, Any]],
    fields: List[str],
    target: str,
    *,
    skip_empty: bool = True,
) -> List[Dict[str, Any]]:
    """Apply :func:`coalesce_fields` to every record in *records*."""
    return [
        coalesce_fields(r, fields, target, skip_empty=skip_empty)
        for r in records
    ]


def coalesce_value(
    record: Dict[str, Any],
    fields: List[str],
    default: Optional[Any] = None,
    *,
    skip_empty: bool = True,
) -> Any:
    """Return the first non-absent value across *fields*, or *default*."""
    for field in fields:
        value = record.get(field)
        if value is None:
            continue
        if skip_empty and value == "":
            continue
        return value
    return default
