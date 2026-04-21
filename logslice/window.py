"""Sliding and tumbling window aggregations over time-stamped log records."""

from datetime import datetime, timedelta
from typing import Dict, Generator, List, Optional

from logslice.filter import parse_timestamp


def _get_ts(record: dict, ts_field: str) -> Optional[datetime]:
    raw = record.get(ts_field)
    if raw is None:
        return None
    return parse_timestamp(str(raw))


def tumbling_windows(
    records: List[dict],
    window_seconds: float,
    ts_field: str = "timestamp",
) -> Generator[Dict, None, None]:
    """Group records into non-overlapping tumbling windows.

    Yields dicts with keys: ``start``, ``end``, ``records``.
    Records without a parseable timestamp are skipped.
    """
    if not records:
        return

    delta = timedelta(seconds=window_seconds)
    bucket_start: Optional[datetime] = None
    bucket: List[dict] = []

    for record in records:
        ts = _get_ts(record, ts_field)
        if ts is None:
            continue
        if bucket_start is None:
            bucket_start = ts
        if ts < bucket_start + delta:
            bucket.append(record)
        else:
            yield {"start": bucket_start, "end": bucket_start + delta, "records": bucket}
            # advance window until ts fits
            while ts >= bucket_start + delta:
                bucket_start = bucket_start + delta
            bucket = [record]

    if bucket and bucket_start is not None:
        yield {"start": bucket_start, "end": bucket_start + delta, "records": bucket}


def sliding_windows(
    records: List[dict],
    window_seconds: float,
    step_seconds: float,
    ts_field: str = "timestamp",
) -> Generator[Dict, None, None]:
    """Yield overlapping sliding windows advancing by *step_seconds*."""
    timestamped = [
        (r, _get_ts(r, ts_field))
        for r in records
    ]
    timestamped = [(r, ts) for r, ts in timestamped if ts is not None]
    if not timestamped:
        return

    first_ts = timestamped[0][1]
    last_ts = timestamped[-1][1]
    delta = timedelta(seconds=window_seconds)
    step = timedelta(seconds=step_seconds)

    current = first_ts
    while current <= last_ts:
        end = current + delta
        window_records = [r for r, ts in timestamped if current <= ts < end]
        yield {"start": current, "end": end, "records": window_records}
        current += step
