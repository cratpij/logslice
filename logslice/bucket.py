"""Bucket records into fixed-size numeric ranges based on a field value."""

from typing import Any, Dict, Iterator, List, Optional, Tuple
import math

Record = Dict[str, Any]


def _get_numeric(record: Record, field: str) -> Optional[float]:
    """Return float value of field, or None if missing/non-numeric."""
    val = record.get(field)
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def bucket_label(value: float, bucket_size: float) -> str:
    """Return a string label like '[10, 20)' for the bucket containing value."""
    low = math.floor(value / bucket_size) * bucket_size
    high = low + bucket_size
    # Format as int when possible for cleaner labels
    if low == int(low) and high == int(high):
        return f"[{int(low)}, {int(high)})"
    return f"[{low}, {high})"


def bucket_records(
    records: List[Record],
    field: str,
    bucket_size: float,
) -> Dict[str, List[Record]]:
    """Group records into buckets of bucket_size based on a numeric field.

    Records with missing or non-numeric field values are placed under '__missing__'.
    Buckets are returned as an ordered dict sorted by lower bound.
    """
    buckets: Dict[str, List[Record]] = {}
    missing_key = "__missing__"

    for record in records:
        val = _get_numeric(record, field)
        if val is None:
            buckets.setdefault(missing_key, []).append(record)
        else:
            label = bucket_label(val, bucket_size)
            buckets.setdefault(label, []).append(record)

    # Sort by lower bound numerically, keep __missing__ at end
    def sort_key(k: str) -> Tuple[float, str]:
        if k == missing_key:
            return (math.inf, k)
        try:
            low = float(k.lstrip("[").split(",")[0])
            return (low, k)
        except (ValueError, IndexError):
            return (math.inf, k)

    return dict(sorted(buckets.items(), key=lambda item: sort_key(item[0])))


def bucket_counts(
    records: List[Record],
    field: str,
    bucket_size: float,
) -> Dict[str, int]:
    """Return a dict mapping bucket label to count of records in that bucket."""
    grouped = bucket_records(records, field, bucket_size)
    return {label: len(recs) for label, recs in grouped.items()}


def iter_buckets(
    records: List[Record],
    field: str,
    bucket_size: float,
) -> Iterator[Tuple[str, List[Record]]]:
    """Yield (label, records) tuples for each bucket in sorted order."""
    grouped = bucket_records(records, field, bucket_size)
    yield from grouped.items()
