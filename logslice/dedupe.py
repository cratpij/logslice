"""Deduplication utilities for log records."""
from typing import Any, Dict, Iterable, Iterator, List, Optional


def dedupe_by_field(
    records: Iterable[Dict[str, Any]],
    field: str,
) -> Iterator[Dict[str, Any]]:
    """Yield records with unique values for *field*.

    The first record with a given field value is kept; subsequent duplicates
    are dropped.  Records missing *field* are always passed through.
    """
    seen: set = set()
    for record in records:
        value = record.get(field)
        if value is None:
            yield record
            continue
        key = (field, value)
        if key not in seen:
            seen.add(key)
            yield record


def dedupe_by_fields(
    records: Iterable[Dict[str, Any]],
    fields: List[str],
) -> Iterator[Dict[str, Any]]:
    """Yield records whose combined values for *fields* are unique.

    Records missing any of the specified fields are always passed through.
    """
    seen: set = set()
    for record in records:
        values: List[Any] = []
        skip = False
        for f in fields:
            if f not in record:
                skip = True
                break
            values.append(record[f])
        if skip:
            yield record
            continue
        key = tuple(values)
        if key not in seen:
            seen.add(key)
            yield record


def dedupe_exact(
    records: Iterable[Dict[str, Any]],
) -> Iterator[Dict[str, Any]]:
    """Yield records that are entirely unique (all fields must match)."""
    seen: set = set()
    for record in records:
        key = tuple(sorted(record.items()))
        if key not in seen:
            seen.add(key)
            yield record
