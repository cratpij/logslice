"""Resample log records into fixed time buckets, aggregating numeric fields."""

from datetime import datetime, timezone, timedelta
from typing import Iterable, Iterator, Dict, Any, Optional, Callable
from collections import defaultdict

from logslice.filter import parse_timestamp


def _floor_to_bucket(ts: datetime, interval_seconds: int) -> datetime:
    """Floor a datetime to the nearest bucket boundary."""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    total_seconds = int((ts - epoch).total_seconds())
    bucket_start = (total_seconds // interval_seconds) * interval_seconds
    return epoch + timedelta(seconds=bucket_start)


def resample_count(
    records: Iterable[Dict[str, Any]],
    interval_seconds: int,
    ts_field: str = "timestamp",
) -> Iterator[Dict[str, Any]]:
    """Count records per time bucket."""
    buckets: Dict[datetime, int] = defaultdict(int)
    for record in records:
        raw = record.get(ts_field)
        if raw is None:
            continue
        ts = parse_timestamp(str(raw))
        if ts is None:
            continue
        key = _floor_to_bucket(ts, interval_seconds)
        buckets[key] += 1
    for bucket_ts in sorted(buckets):
        yield {"bucket": bucket_ts.isoformat(), "count": buckets[bucket_ts]}


def resample_sum(
    records: Iterable[Dict[str, Any]],
    field: str,
    interval_seconds: int,
    ts_field: str = "timestamp",
) -> Iterator[Dict[str, Any]]:
    """Sum a numeric field per time bucket."""
    buckets: Dict[datetime, float] = defaultdict(float)
    for record in records:
        raw = record.get(ts_field)
        if raw is None:
            continue
        ts = parse_timestamp(str(raw))
        if ts is None:
            continue
        try:
            value = float(record[field])
        except (KeyError, TypeError, ValueError):
            continue
        key = _floor_to_bucket(ts, interval_seconds)
        buckets[key] += value
    for bucket_ts in sorted(buckets):
        yield {"bucket": bucket_ts.isoformat(), field: buckets[bucket_ts]}


def resample_avg(
    records: Iterable[Dict[str, Any]],
    field: str,
    interval_seconds: int,
    ts_field: str = "timestamp",
) -> Iterator[Dict[str, Any]]:
    """Average a numeric field per time bucket."""
    sums: Dict[datetime, float] = defaultdict(float)
    counts: Dict[datetime, int] = defaultdict(int)
    for record in records:
        raw = record.get(ts_field)
        if raw is None:
            continue
        ts = parse_timestamp(str(raw))
        if ts is None:
            continue
        try:
            value = float(record[field])
        except (KeyError, TypeError, ValueError):
            continue
        key = _floor_to_bucket(ts, interval_seconds)
        sums[key] += value
        counts[key] += 1
    for bucket_ts in sorted(sums):
        avg = sums[bucket_ts] / counts[bucket_ts]
        yield {"bucket": bucket_ts.isoformat(), field: round(avg, 6)}
