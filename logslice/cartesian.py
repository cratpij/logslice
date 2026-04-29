"""Cross-join (cartesian product) utilities for log records."""

from typing import Dict, Any, List, Iterable, Optional


def cartesian_product(
    left: Iterable[Dict[str, Any]],
    right: Iterable[Dict[str, Any]],
    prefix_left: Optional[str] = None,
    prefix_right: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return the cartesian product of two record streams.

    Optionally prefix keys from each side to avoid collisions.
    """
    left_list = list(left)
    right_list = list(right)
    results = []
    for l in left_list:
        for r in right_list:
            merged: Dict[str, Any] = {}
            for k, v in l.items():
                key = f"{prefix_left}_{k}" if prefix_left else k
                merged[key] = v
            for k, v in r.items():
                key = f"{prefix_right}_{k}" if prefix_right else k
                merged[key] = v
            results.append(merged)
    return results


def cartesian_with_lookup(
    records: Iterable[Dict[str, Any]],
    lookup: List[Dict[str, Any]],
    join_field: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Cross-join records with a lookup list, optionally filtering to rows
    where record[join_field] == lookup_row[join_field].
    """
    results = []
    for record in records:
        for row in lookup:
            if join_field is not None:
                if record.get(join_field) != row.get(join_field):
                    continue
            merged = {**record, **row}
            results.append(merged)
    return results


def dedup_cartesian(
    pairs: Iterable[Dict[str, Any]],
    key_fields: List[str],
) -> List[Dict[str, Any]]:
    """Remove duplicate rows from a cartesian result based on a composite key."""
    seen = set()
    out = []
    for record in pairs:
        key = tuple(record.get(f) for f in key_fields)
        if key not in seen:
            seen.add(key)
            out.append(record)
    return out
