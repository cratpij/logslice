"""Count and frequency utilities for log records."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Iterator


def count_records(records: Iterable[dict]) -> int:
    """Return the total number of records."""
    return sum(1 for _ in records)


def frequency_by_field(
    records: Iterable[dict],
    field: str,
    *,
    missing: str = "<missing>",
) -> dict[str, int]:
    """Return a frequency map of values for *field* across all records.

    Records that lack *field* are counted under *missing*.
    Results are sorted descending by count.
    """
    counter: Counter[str] = Counter()
    for record in records:
        value = record.get(field)
        key = str(value) if value is not None else missing
        counter[key] += 1
    return dict(counter.most_common())


def top_n(
    records: Iterable[dict],
    field: str,
    n: int,
    *,
    missing: str = "<missing>",
) -> list[tuple[str, int]]:
    """Return the top *n* (value, count) pairs for *field*."""
    freq = frequency_by_field(records, field, missing=missing)
    return list(freq.items())[:n]


def count_where(
    records: Iterable[dict],
    field: str,
    value: str,
) -> int:
    """Count records where *field* equals *value* (string comparison)."""
    return sum(1 for r in records if str(r.get(field, "")) == value)


def running_count(
    records: Iterable[dict],
) -> Iterator[tuple[dict, int]]:
    """Yield (record, running_total) pairs as records are consumed."""
    total = 0
    for record in records:
        total += 1
        yield record, total
