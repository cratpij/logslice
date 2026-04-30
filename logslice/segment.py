"""Segment records into named groups based on ordered boundary conditions."""

from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Tuple


def _evaluate(record: Dict, field: str, value: Any) -> bool:
    """Return True if record[field] >= value (string-safe comparison)."""
    return str(record.get(field, "")) >= str(value)


def segment_by_field(
    records: Iterable[Dict],
    field: str,
    boundaries: List[Tuple[Any, str]],
    default: str = "other",
) -> Iterator[Dict]:
    """Tag each record with a segment label based on ordered field boundaries.

    boundaries: list of (threshold, label) pairs, sorted ascending by threshold.
    Each record is assigned the label of the highest threshold it meets.
    """
    for record in records:
        label = default
        val = record.get(field)
        if val is not None:
            for threshold, seg_label in boundaries:
                if str(val) >= str(threshold):
                    label = seg_label
        yield {**record, "_segment": label}


def segment_by_predicate(
    records: Iterable[Dict],
    predicates: List[Tuple[Callable[[Dict], bool], str]],
    default: str = "other",
) -> Iterator[Dict]:
    """Tag each record with the label of the first matching predicate."""
    for record in records:
        label = default
        for predicate, seg_label in predicates:
            if predicate(record):
                label = seg_label
                break
        yield {**record, "_segment": label}


def segment_counts(records: Iterable[Dict], segment_field: str = "_segment") -> Dict[str, int]:
    """Count how many records fall into each segment."""
    counts: Dict[str, int] = {}
    for record in records:
        key = record.get(segment_field, "__missing__")
        counts[key] = counts.get(key, 0) + 1
    return counts


def split_segments(
    records: Iterable[Dict], segment_field: str = "_segment"
) -> Dict[str, List[Dict]]:
    """Partition records into a dict keyed by segment label."""
    result: Dict[str, List[Dict]] = {}
    for record in records:
        key = record.get(segment_field, "__missing__")
        result.setdefault(key, []).append(record)
    return result
