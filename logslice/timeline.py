"""Timeline: group records into time buckets and produce a textual timeline summary."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple

from logslice.filter import parse_timestamp


def _floor_timestamp(ts: datetime, bucket_seconds: int) -> datetime:
    """Floor a datetime to the nearest bucket boundary."""
    epoch = int(ts.replace(tzinfo=timezone.utc).timestamp()) if ts.tzinfo else int(ts.timestamp())
    floored = (epoch // bucket_seconds) * bucket_seconds
    return datetime.utcfromtimestamp(floored)


def build_timeline(
    records: Iterable[dict],
    bucket_seconds: int = 60,
    ts_field: str = "timestamp",
) -> List[Tuple[datetime, List[dict]]]:
    """Group records into time buckets of *bucket_seconds* width.

    Returns a list of (bucket_start, [records]) tuples sorted by bucket_start.
    Records missing a parseable timestamp are silently skipped.
    """
    buckets: Dict[datetime, List[dict]] = defaultdict(list)
    for record in records:
        raw = record.get(ts_field)
        if raw is None:
            continue
        ts = parse_timestamp(str(raw))
        if ts is None:
            continue
        key = _floor_timestamp(ts, bucket_seconds)
        buckets[key].append(record)
    return sorted(buckets.items())


def timeline_counts(
    records: Iterable[dict],
    bucket_seconds: int = 60,
    ts_field: str = "timestamp",
) -> List[dict]:
    """Return a list of dicts with 'bucket', 'count' keys."""
    tl = build_timeline(records, bucket_seconds=bucket_seconds, ts_field=ts_field)
    return [
        {"bucket": bucket.isoformat(), "count": len(recs)}
        for bucket, recs in tl
    ]


def render_timeline(
    timeline: List[Tuple[datetime, List[dict]]],
    bar_char: str = "#",
    max_width: int = 40,
) -> str:
    """Render a timeline as a simple ASCII bar chart string."""
    if not timeline:
        return ""
    max_count = max(len(recs) for _, recs in timeline)
    lines = []
    for bucket, recs in timeline:
        count = len(recs)
        bar_len = int((count / max_count) * max_width) if max_count else 0
        bar = bar_char * bar_len
        lines.append(f"{bucket.isoformat()} | {bar} {count}")
    return "\n".join(lines)
