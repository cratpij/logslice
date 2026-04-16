"""Basic statistics over parsed log records."""
from collections import Counter
from typing import Iterable, Any


def count_by_field(records: Iterable[dict], field: str) -> Counter:
    """Count occurrences of each unique value for *field*."""
    c: Counter = Counter()
    for rec in records:
        if field in rec:
            c[rec[field]] += 1
    return c


def field_values(records: Iterable[dict], field: str) -> list[Any]:
    """Return list of values for *field* across all records (None if missing)."""
    return [rec.get(field) for rec in records]


def summary(records: Iterable[dict]) -> dict:
    """Return a high-level summary dict for a collection of records.

    Keys
    ----
    total       : total number of records
    fields      : set of all field names seen
    level_counts: Counter of 'level' field values (if present)
    """
    records = list(records)
    total = len(records)
    fields: set = set()
    level_counter: Counter = Counter()

    for rec in records:
        fields.update(rec.keys())
        if "level" in rec:
            level_counter[rec["level"]] += 1

    return {
        "total": total,
        "fields": fields,
        "level_counts": level_counter,
    }
