"""Field transformation utilities for log records."""
from typing import Any, Dict, List, Optional

Record = Dict[str, Any]


def rename_field(records: List[Record], old_key: str, new_key: str) -> List[Record]:
    """Return records with old_key renamed to new_key."""
    result = []
    for rec in records:
        r = dict(rec)
        if old_key in r:
            r[new_key] = r.pop(old_key)
        result.append(r)
    return result


def drop_fields(records: List[Record], fields: List[str]) -> List[Record]:
    """Return records with specified fields removed."""
    return [
        {k: v for k, v in rec.items() if k not in fields}
        for rec in records
    ]


def keep_fields(records: List[Record], fields: List[str]) -> List[Record]:
    """Return records containing only the specified fields."""
    return [
        {k: v for k, v in rec.items() if k in fields}
        for rec in records
    ]


def add_field(records: List[Record], key: str, value: Any, overwrite: bool = False) -> List[Record]:
    """Return records with a new field added."""
    result = []
    for rec in records:
        r = dict(rec)
        if overwrite or key not in r:
            r[key] = value
        result.append(r)
    return result


def cast_field(records: List[Record], key: str, cast_type: type) -> List[Record]:
    """Return records with a field cast to the given type. Skips on error."""
    result = []
    for rec in records:
        r = dict(rec)
        if key in r:
            try:
                r[key] = cast_type(r[key])
            except (ValueError, TypeError):
                pass
        result.append(r)
    return result
