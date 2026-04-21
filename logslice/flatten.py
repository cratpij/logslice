"""Flatten nested dicts in log records into dot-notation keys."""
from typing import Any, Dict, Iterator, List


def flatten_record(
    record: Dict[str, Any],
    sep: str = ".",
    prefix: str = "",
    max_depth: int = 0,
    _depth: int = 0,
) -> Dict[str, Any]:
    """Return a new record with nested dicts flattened into dot-notation keys.

    Args:
        record: The source log record.
        sep: Separator used between key segments (default ".").
        prefix: Key prefix applied to all output keys (usually used internally).
        max_depth: Maximum nesting depth to flatten; 0 means unlimited.
        _depth: Internal recursion depth counter.

    Returns:
        A new flat dict.  Non-dict values are kept as-is.
    """
    result: Dict[str, Any] = {}
    for key, value in record.items():
        full_key = f"{prefix}{sep}{key}" if prefix else key
        if (
            isinstance(value, dict)
            and value
            and (max_depth == 0 or _depth < max_depth)
        ):
            nested = flatten_record(
                value,
                sep=sep,
                prefix=full_key,
                max_depth=max_depth,
                _depth=_depth + 1,
            )
            result.update(nested)
        else:
            result[full_key] = value
    return result


def flatten_records(
    records: Iterator[Dict[str, Any]],
    sep: str = ".",
    max_depth: int = 0,
) -> List[Dict[str, Any]]:
    """Apply :func:`flatten_record` to every record in *records*."""
    return [
        flatten_record(r, sep=sep, max_depth=max_depth) for r in records
    ]


def unflatten_record(
    record: Dict[str, Any], sep: str = "."
) -> Dict[str, Any]:
    """Reconstruct a nested dict from a flat dot-notation record.

    Only string keys that contain *sep* are expanded; others are kept.
    """
    result: Dict[str, Any] = {}
    for key, value in record.items():
        parts = key.split(sep)
        node = result
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
    return result
