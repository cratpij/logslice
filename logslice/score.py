"""Score records by how many fields match a set of criteria."""

from typing import Any, Callable, Dict, Iterable, List, Optional


def score_record(
    record: Dict[str, Any],
    criteria: Dict[str, Any],
    weight: float = 1.0,
) -> Dict[str, Any]:
    """Add a '_score' field counting how many criteria fields match.

    Each matching field contributes *weight* to the score.
    """
    record = dict(record)
    hits = sum(
        1 for field, value in criteria.items()
        if record.get(field) == value
    )
    record["_score"] = hits * weight
    return record


def score_records(
    records: Iterable[Dict[str, Any]],
    criteria: Dict[str, Any],
    weight: float = 1.0,
) -> List[Dict[str, Any]]:
    """Score every record in *records*."""
    return [score_record(r, criteria, weight) for r in records]


def score_by_fn(
    record: Dict[str, Any],
    fn: Callable[[Dict[str, Any]], float],
    field: str = "_score",
) -> Dict[str, Any]:
    """Compute a score via an arbitrary callable and store it in *field*."""
    record = dict(record)
    record[field] = fn(record)
    return record


def top_scored(
    records: Iterable[Dict[str, Any]],
    n: int,
    field: str = "_score",
    reverse: bool = True,
) -> List[Dict[str, Any]]:
    """Return the top *n* records sorted by *field* (descending by default)."""
    scored = list(records)
    scored.sort(key=lambda r: r.get(field, 0), reverse=reverse)
    return scored[:n]


def filter_min_score(
    records: Iterable[Dict[str, Any]],
    min_score: float,
    field: str = "_score",
) -> List[Dict[str, Any]]:
    """Keep only records whose score is at least *min_score*."""
    return [r for r in records if r.get(field, 0) >= min_score]
