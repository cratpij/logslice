"""Pattern-based filtering: match records by regex against field values."""

import re
from typing import Iterable, Iterator, Optional, Pattern


def compile_pattern(pattern: str, ignore_case: bool = False) -> Pattern:
    """Compile a regex pattern with optional case-insensitivity."""
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def match_field(
    record: dict,
    field: str,
    pattern: Pattern,
) -> bool:
    """Return True if the field value in record matches the pattern."""
    value = record.get(field)
    if value is None:
        return False
    return bool(pattern.search(str(value)))


def filter_by_pattern(
    records: Iterable[dict],
    field: str,
    pattern: Pattern,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield records where field matches (or does not match) the pattern."""
    for record in records:
        matched = match_field(record, field, pattern)
        if invert:
            if not matched:
                yield record
        else:
            if matched:
                yield record


def filter_any_field(
    records: Iterable[dict],
    pattern: Pattern,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield records where *any* field value matches the pattern."""
    for record in records:
        matched = any(
            bool(pattern.search(str(v)))
            for v in record.values()
            if v is not None
        )
        if invert:
            if not matched:
                yield record
        else:
            if matched:
                yield record


def extract_matches(
    records: Iterable[dict],
    field: str,
    pattern: Pattern,
    dest_field: str = "_match",
) -> Iterator[dict]:
    """Yield records with the first regex match stored in dest_field."""
    for record in records:
        value = record.get(field)
        if value is None:
            yield record
            continue
        m = pattern.search(str(value))
        if m:
            yield {**record, dest_field: m.group(0)}
        else:
            yield record
