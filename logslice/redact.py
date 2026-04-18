"""Field redaction utilities for logslice."""

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional


def redact_field(record: Dict[str, Any], field: str, mask: str = "***") -> Dict[str, Any]:
    """Return a copy of record with the given field value replaced by mask."""
    if field not in record:
        return dict(record)
    result = dict(record)
    result[field] = mask
    return result


def redact_fields(record: Dict[str, Any], fields: List[str], mask: str = "***") -> Dict[str, Any]:
    """Return a copy of record with all listed fields replaced by mask."""
    result = dict(record)
    for field in fields:
        if field in result:
            result[field] = mask
    return result


def redact_pattern(record: Dict[str, Any], field: str, pattern: str, mask: str = "***") -> Dict[str, Any]:
    """Return a copy of record with regex pattern matches in field replaced by mask."""
    if field not in record:
        return dict(record)
    result = dict(record)
    value = str(result[field])
    result[field] = re.sub(pattern, mask, value)
    return result


def redact_all(records: Iterable[Dict[str, Any]], fields: List[str], mask: str = "***") -> Iterator[Dict[str, Any]]:
    """Yield records with all listed fields redacted."""
    for record in records:
        yield redact_fields(record, fields, mask)
