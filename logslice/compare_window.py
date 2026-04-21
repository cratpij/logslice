"""Helpers for comparing records within adjacent time windows."""

from typing import Any, Dict, Iterator, List, Optional, Tuple

from logslice.compare import compare_records
from logslice.window import tumbling_windows

Record = Dict[str, Any]
WindowPair = Tuple[List[Record], List[Record]]


def adjacent_window_pairs(
    records: List[Record],
    window_seconds: int,
    ts_field: str = "timestamp",
) -> Iterator[WindowPair]:
    """Yield (prev_window, curr_window) pairs of consecutive tumbling windows."""
    windows = list(tumbling_windows(records, window_seconds, ts_field=ts_field))
    for i in range(1, len(windows)):
        yield windows[i - 1], windows[i]


def window_field_diff(
    prev: List[Record],
    curr: List[Record],
    aggregate_field: str,
    key_field: str,
) -> List[Dict[str, Any]]:
    """Compare *aggregate_field* across two windows, keyed by *key_field*.

    Returns a list of diff reports with keys: key, prev_value, curr_value, delta.
    """
    def _index(window: List[Record]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for rec in window:
            k = str(rec.get(key_field, "<unknown>"))
            try:
                result[k] = float(rec.get(aggregate_field, 0) or 0)
            except (TypeError, ValueError):
                result[k] = 0.0
        return result

    prev_idx = _index(prev)
    curr_idx = _index(curr)
    all_keys = sorted(set(prev_idx) | set(curr_idx))
    reports = []
    for k in all_keys:
        pv = prev_idx.get(k, 0.0)
        cv = curr_idx.get(k, 0.0)
        reports.append({
            "key": k,
            "prev_value": pv,
            "curr_value": cv,
            "delta": round(cv - pv, 6),
        })
    return reports


def summarise_window_changes(
    pairs: Iterator[WindowPair],
    key_field: str,
    fields: Optional[List[str]] = None,
) -> Iterator[Dict[str, Any]]:
    """For each window pair yield a summary of how records changed."""
    for idx, (prev, curr) in enumerate(pairs):
        prev_map = {str(r.get(key_field)): r for r in prev}
        curr_map = {str(r.get(key_field)): r for r in curr}
        all_keys = sorted(set(prev_map) | set(curr_map))
        diffs = []
        for k in all_keys:
            pr = prev_map.get(k, {})
            cr = curr_map.get(k, {})
            d = compare_records(pr, cr, fields)
            if d:
                diffs.append({"key": k, "diffs": d})
        yield {"window_pair": idx, "changed": len(diffs), "details": diffs}
