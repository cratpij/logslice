"""Split a stream of records into multiple buckets based on a field value."""

from typing import Dict, Iterable, List, Optional


def split_by_field(
    records: Iterable[dict],
    field: str,
    missing_key: str = "__missing__",
) -> Dict[str, List[dict]]:
    """Partition records into buckets keyed by the value of *field*.

    Records that do not contain *field* are placed under *missing_key*.
    """
    buckets: Dict[str, List[dict]] = {}
    for record in records:
        key = str(record[field]) if field in record else missing_key
        buckets.setdefault(key, []).append(record)
    return buckets


def split_by_predicate(
    records: Iterable[dict],
    predicate,
    true_key: str = "match",
    false_key: str = "no_match",
) -> Dict[str, List[dict]]:
    """Split records into two buckets based on a boolean predicate function."""
    buckets: Dict[str, List[dict]] = {true_key: [], false_key: []}
    for record in records:
        if predicate(record):
            buckets[true_key].append(record)
        else:
            buckets[false_key].append(record)
    return buckets


def split_by_value_set(
    records: Iterable[dict],
    field: str,
    values: Iterable[str],
    other_key: Optional[str] = "__other__",
) -> Dict[str, List[dict]]:
    """Split records into buckets for each value in *values*.

    Records whose field value is not in *values* go to *other_key*.  If
    *other_key* is ``None`` those records are discarded.
    """
    allowed = set(values)
    buckets: Dict[str, List[dict]] = {v: [] for v in allowed}
    if other_key is not None:
        buckets[other_key] = []
    for record in records:
        val = str(record.get(field, ""))
        if val in allowed:
            buckets[val].append(record)
        elif other_key is not None:
            buckets[other_key].append(record)
    return buckets


def split_into_chunks(
    records: Iterable[dict],
    chunk_size: int,
) -> List[List[dict]]:
    """Divide *records* into sequential chunks of at most *chunk_size* items."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    chunks: List[List[dict]] = []
    current: List[dict] = []
    for record in records:
        current.append(record)
        if len(current) == chunk_size:
            chunks.append(current)
            current = []
    if current:
        chunks.append(current)
    return chunks
