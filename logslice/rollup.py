"""Rollup: aggregate records over a field with multiple summary statistics."""

from typing import Any, Dict, Iterable, List, Optional
from collections import defaultdict


def _get_numeric(record: Dict[str, Any], field: str) -> Optional[float]:
    """Return numeric value of a field, or None if missing/non-numeric."""
    val = record.get(field)
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def rollup(
    records: Iterable[Dict[str, Any]],
    group_field: str,
    value_field: str,
) -> List[Dict[str, Any]]:
    """Group records by group_field and compute count/sum/avg/min/max of value_field."""
    groups: Dict[str, List[float]] = defaultdict(list)

    for record in records:
        key = str(record.get(group_field, "__missing__"))
        val = _get_numeric(record, value_field)
        if val is not None:
            groups[key].append(val)

    results = []
    for group_key in sorted(groups):
        values = groups[group_key]
        n = len(values)
        total = sum(values)
        results.append({
            group_field: group_key,
            "count": n,
            "sum": total,
            "avg": total / n if n > 0 else None,
            "min": min(values),
            "max": max(values),
        })
    return results


def rollup_count_only(
    records: Iterable[Dict[str, Any]],
    group_field: str,
) -> List[Dict[str, Any]]:
    """Group records by group_field and return only counts."""
    counts: Dict[str, int] = defaultdict(int)
    for record in records:
        key = str(record.get(group_field, "__missing__"))
        counts[key] += 1
    return [
        {group_field: k, "count": v}
        for k, v in sorted(counts.items())
    ]


def rollup_multi(
    records: Iterable[Dict[str, Any]],
    group_field: str,
    value_fields: List[str],
) -> List[Dict[str, Any]]:
    """Rollup multiple value fields at once, grouped by group_field."""
    groups: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for record in records:
        key = str(record.get(group_field, "__missing__"))
        for vf in value_fields:
            val = _get_numeric(record, vf)
            if val is not None:
                groups[key][vf].append(val)

    results = []
    for group_key in sorted(groups):
        row: Dict[str, Any] = {group_field: group_key}
        for vf in value_fields:
            values = groups[group_key].get(vf, [])
            n = len(values)
            prefix = vf
            row[f"{prefix}_count"] = n
            row[f"{prefix}_sum"] = sum(values) if n > 0 else None
            row[f"{prefix}_avg"] = sum(values) / n if n > 0 else None
            row[f"{prefix}_min"] = min(values) if n > 0 else None
            row[f"{prefix}_max"] = max(values) if n > 0 else None
        results.append(row)
    return results
