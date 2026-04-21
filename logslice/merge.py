"""Merge multiple streams of log records, optionally sorted by timestamp."""

from typing import Iterable, Iterator, List, Optional
import heapq

from logslice.filter import parse_timestamp


def merge_records(
    *streams: Iterable[dict],
) -> List[dict]:
    """Concatenate multiple record iterables into a single list."""
    result = []
    for stream in streams:
        result.extend(stream)
    return result


def merge_sorted(
    *streams: Iterable[dict],
    timestamp_field: str = "timestamp",
) -> List[dict]:
    """Merge multiple record streams into one list sorted by timestamp.

    Records missing the timestamp field are appended at the end.
    """
    timestamped: List[tuple] = []
    no_ts: List[dict] = []

    for stream in streams:
        for record in stream:
            raw = record.get(timestamp_field)
            if raw is None:
                no_ts.append(record)
                continue
            ts = parse_timestamp(str(raw))
            if ts is None:
                no_ts.append(record)
            else:
                timestamped.append((ts, record))

    timestamped.sort(key=lambda t: t[0])
    return [r for _, r in timestamped] + no_ts


def merge_dedupe(
    *streams: Iterable[dict],
    key_field: str,
) -> List[dict]:
    """Merge streams and remove duplicate records sharing the same key_field value.

    The first occurrence of each key is kept.
    """
    seen = set()
    result = []
    for stream in streams:
        for record in stream:
            key = record.get(key_field)
            if key is None or key not in seen:
                result.append(record)
                if key is not None:
                    seen.add(key)
    return result
