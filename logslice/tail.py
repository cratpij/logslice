"""Tail and head utilities for log records."""
from typing import Iterable, Iterator
from collections import deque


def head_records(
    records: Iterable[dict],
    n: int,
) -> list[dict]:
    """Return the first *n* records from *records*."""
    result = []
    for record in records:
        if len(result) >= n:
            break
        result.append(record)
    return result


def tail_records(
    records: Iterable[dict],
    n: int,
) -> list[dict]:
    """Return the last *n* records from *records* using a circular buffer."""
    if n <= 0:
        return []
    buf: deque[dict] = deque(maxlen=n)
    for record in records:
        buf.append(record)
    return list(buf)


def skip_records(
    records: Iterable[dict],
    n: int,
) -> Iterator[dict]:
    """Skip the first *n* records and yield the rest."""
    skipped = 0
    for record in records:
        if skipped < n:
            skipped += 1
            continue
        yield record


def take_while(
    records: Iterable[dict],
    field: str,
    value: str,
) -> Iterator[dict]:
    """Yield records while *field* equals *value*; stop at the first mismatch."""
    for record in records:
        if str(record.get(field, "")) != value:
            break
        yield record


def drop_while(
    records: Iterable[dict],
    field: str,
    value: str,
) -> Iterator[dict]:
    """Skip records while *field* equals *value*, then yield the rest."""
    dropping = True
    for record in records:
        if dropping and str(record.get(field, "")) == value:
            continue
        dropping = False
        yield record
