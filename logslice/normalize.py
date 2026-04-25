"""Field value normalization utilities for logslice."""

from typing import Any, Callable, Dict, Iterable, List, Optional


def normalize_field(record: Dict, field: str, fn: Callable[[Any], Any]) -> Dict:
    """Apply a normalization function to a single field, returning a new record."""
    if field not in record:
        return dict(record)
    result = dict(record)
    result[field] = fn(record[field])
    return result


def normalize_to_lowercase(record: Dict, field: str) -> Dict:
    """Lowercase a string field value."""
    return normalize_field(record, field, lambda v: v.lower() if isinstance(v, str) else v)


def normalize_to_uppercase(record: Dict, field: str) -> Dict:
    """Uppercase a string field value."""
    return normalize_field(record, field, lambda v: v.upper() if isinstance(v, str) else v)


def normalize_strip(record: Dict, field: str) -> Dict:
    """Strip leading/trailing whitespace from a string field value."""
    return normalize_field(record, field, lambda v: v.strip() if isinstance(v, str) else v)


def normalize_replace(record: Dict, field: str, old: str, new: str) -> Dict:
    """Replace occurrences of a substring within a string field value."""
    return normalize_field(
        record, field, lambda v: v.replace(old, new) if isinstance(v, str) else v
    )


def normalize_default(record: Dict, field: str, default: Any) -> Dict:
    """Set a field to a default value if it is missing or None."""
    result = dict(record)
    if result.get(field) is None:
        result[field] = default
    return result


def normalize_records(
    records: Iterable[Dict],
    field: str,
    fn: Callable[[Any], Any],
) -> List[Dict]:
    """Apply a normalization function to a field across all records."""
    return [normalize_field(r, field, fn) for r in records]
