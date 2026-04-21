"""Statistics helpers for window results."""

from typing import Any, Dict, Iterable, List, Optional


def window_count(window: dict) -> int:
    """Return the number of records in a window."""
    return len(window.get("records", []))


def window_field_avg(window: dict, field: str) -> Optional[float]:
    """Return the average of *field* across records in *window*.

    Returns ``None`` if no numeric values are found.
    """
    values = []
    for r in window.get("records", []):
        v = r.get(field)
        try:
            values.append(float(v))
        except (TypeError, ValueError):
            pass
    return sum(values) / len(values) if values else None


def window_field_sum(window: dict, field: str) -> float:
    """Return the sum of *field* across records in *window*."""
    total = 0.0
    for r in window.get("records", []):
        v = r.get(field)
        try:
            total += float(v)
        except (TypeError, ValueError):
            pass
    return total


def window_summary(windows: Iterable[dict], field: str = None) -> List[Dict[str, Any]]:
    """Summarise a sequence of windows.

    Each summary dict contains ``start``, ``end``, ``count``, and optionally
    ``sum`` and ``avg`` when *field* is given.
    """
    result = []
    for w in windows:
        entry: Dict[str, Any] = {
            "start": w["start"].isoformat() if hasattr(w["start"], "isoformat") else w["start"],
            "end": w["end"].isoformat() if hasattr(w["end"], "isoformat") else w["end"],
            "count": window_count(w),
        }
        if field is not None:
            entry["sum"] = window_field_sum(w, field)
            entry["avg"] = window_field_avg(w, field)
        result.append(entry)
    return result
