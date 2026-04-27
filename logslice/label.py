"""Assign categorical labels to records based on field value ranges or conditions."""

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


Record = Dict[str, Any]
Condition = Callable[[Record], bool]


def label_by_condition(
    record: Record,
    conditions: List[Tuple[str, Condition]],
    field: str = "label",
    default: Optional[str] = None,
) -> Record:
    """Assign the first matching label from a list of (label, predicate) pairs."""
    for label, predicate in conditions:
        try:
            if predicate(record):
                return {**record, field: label}
        except Exception:
            continue
    if default is not None:
        return {**record, field: default}
    return dict(record)


def label_by_range(
    record: Record,
    source_field: str,
    ranges: List[Tuple[float, float, str]],
    field: str = "label",
    default: Optional[str] = None,
) -> Record:
    """Assign a label based on numeric range buckets: list of (lo, hi, label).

    Ranges are inclusive on lo, exclusive on hi.
    """
    raw = record.get(source_field)
    try:
        value = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return {**record, field: default} if default is not None else dict(record)

    for lo, hi, lbl in ranges:
        if lo <= value < hi:
            return {**record, field: lbl}
    if default is not None:
        return {**record, field: default}
    return dict(record)


def label_by_value(
    record: Record,
    source_field: str,
    mapping: Dict[Any, str],
    field: str = "label",
    default: Optional[str] = None,
) -> Record:
    """Map exact field values to labels using a lookup dict."""
    raw = record.get(source_field)
    lbl = mapping.get(raw, default)
    if lbl is not None:
        return {**record, field: lbl}
    return dict(record)


def label_records(
    records: Iterable[Record],
    conditions: List[Tuple[str, Condition]],
    field: str = "label",
    default: Optional[str] = None,
) -> List[Record]:
    """Apply label_by_condition to every record in an iterable."""
    return [
        label_by_condition(r, conditions, field=field, default=default)
        for r in records
    ]
