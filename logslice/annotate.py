"""Annotate log records with computed or static labels."""

from typing import Any, Callable, Dict, Iterable, List, Optional


def annotate_with_label(
    records: Iterable[Dict[str, Any]],
    field: str,
    label: str,
) -> List[Dict[str, Any]]:
    """Add a static label field to every record."""
    result = []
    for record in records:
        r = dict(record)
        r[field] = label
        result.append(r)
    return result


def annotate_with_fn(
    records: Iterable[Dict[str, Any]],
    field: str,
    fn: Callable[[Dict[str, Any]], Any],
) -> List[Dict[str, Any]]:
    """Add a field derived by applying fn to each record."""
    result = []
    for record in records:
        r = dict(record)
        r[field] = fn(r)
        result.append(r)
    return result


def annotate_with_index(
    records: Iterable[Dict[str, Any]],
    field: str = "_index",
    start: int = 0,
) -> List[Dict[str, Any]]:
    """Add a sequential index field to every record."""
    result = []
    for i, record in enumerate(records, start=start):
        r = dict(record)
        r[field] = i
        result.append(r)
    return result


def annotate_conditional(
    records: Iterable[Dict[str, Any]],
    field: str,
    condition: Callable[[Dict[str, Any]], bool],
    true_value: Any,
    false_value: Any = None,
) -> List[Dict[str, Any]]:
    """Annotate field with true_value or false_value based on a condition."""
    result = []
    for record in records:
        r = dict(record)
        r[field] = true_value if condition(r) else false_value
        result.append(r)
    return result
