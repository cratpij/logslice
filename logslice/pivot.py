"""Pivot helpers that build summary tables from aggregated data."""
from typing import Any, Dict, List, Tuple
from logslice.aggregate import count_by, sum_by, avg_by


def pivot_count(records: List[Dict], field: str) -> List[Dict]:
    """Return a list of {field, count} dicts sorted by count descending."""
    counts = count_by(records, field)
    return sorted(
        [{field: k, "count": v} for k, v in counts.items()],
        key=lambda r: r["count"],
        reverse=True,
    )


def pivot_sum(records: List[Dict], group_field: str, value_field: str) -> List[Dict]:
    """Return a list of {group_field, sum} dicts sorted by sum descending."""
    totals = sum_by(records, group_field, value_field)
    return sorted(
        [{group_field: k, "sum": v} for k, v in totals.items()],
        key=lambda r: r["sum"],
        reverse=True,
    )


def pivot_avg(records: List[Dict], group_field: str, value_field: str) -> List[Dict]:
    """Return a list of {group_field, avg} dicts sorted by avg descending."""
    avgs = avg_by(records, group_field, value_field)
    return sorted(
        [{group_field: k, "avg": round(v, 4)} for k, v in avgs.items()],
        key=lambda r: r["avg"],
        reverse=True,
    )
