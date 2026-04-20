"""Aggregate functions for log records."""
from typing import Any, Dict, List, Optional
from collections import defaultdict


def group_by(records: List[Dict], field: str) -> Dict[str, List[Dict]]:
    """Group records by the value of a field."""
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for record in records:
        key = str(record[field]) if field in record else "__missing__"
        groups[key].append(record)
    return dict(groups)


def count_by(records: List[Dict], field: str) -> Dict[str, int]:
    """Count records grouped by field value."""
    counts: Dict[str, int] = defaultdict(int)
    for record in records:
        key = str(record[field]) if field in record else "__missing__"
        counts[key] += 1
    return dict(counts)


def sum_by(records: List[Dict], group_field: str, value_field: str) -> Dict[str, float]:
    """Sum a numeric field grouped by another field."""
    totals: Dict[str, float] = defaultdict(float)
    for record in records:
        key = str(record[group_field]) if group_field in record else "__missing__"
        try:
            totals[key] += float(record[value_field])
        except (KeyError, TypeError, ValueError):
            pass
    return dict(totals)


def avg_by(records: List[Dict], group_field: str, value_field: str) -> Dict[str, Optional[float]]:
    """Average a numeric field grouped by another field."""
    totals: Dict[str, float] = defaultdict(float)
    counts: Dict[str, int] = defaultdict(int)
    for record in records:
        key = str(record[group_field]) if group_field in record else "__missing__"
        try:
            totals[key] += float(record[value_field])
            counts[key] += 1
        except (KeyError, TypeError, ValueError):
            pass
    return {k: totals[k] / counts[k] for k in totals}


def min_max_by(
    records: List[Dict], group_field: str, value_field: str
) -> Dict[str, Dict[str, float]]:
    """Compute the min and max of a numeric field grouped by another field.

    Returns a dict mapping each group key to a dict with 'min' and 'max' keys.
    Groups where no valid numeric values exist are omitted from the result.
    """
    result: Dict[str, Dict[str, float]] = {}
    for record in records:
        key = str(record[group_field]) if group_field in record else "__missing__"
        try:
            value = float(record[value_field])
        except (KeyError, TypeError, ValueError):
            continue
        if key not in result:
            result[key] = {"min": value, "max": value}
        else:
            result[key]["min"] = min(result[key]["min"], value)
            result[key]["max"] = max(result[key]["max"], value)
    return result
