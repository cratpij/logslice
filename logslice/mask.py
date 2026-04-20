"""Field masking utilities: partially obscure field values for privacy."""

import re
from typing import Any, Dict, List, Optional


def mask_field(
    record: Dict[str, Any],
    field: str,
    visible_start: int = 0,
    visible_end: int = 0,
    char: str = "*",
) -> Dict[str, Any]:
    """Partially mask a field value, keeping visible_start and visible_end chars."""
    if field not in record:
        return record
    value = str(record[field])
    length = len(value)
    if length <= visible_start + visible_end:
        masked = char * length
    else:
        start = value[:visible_start] if visible_start else ""
        end = value[length - visible_end:] if visible_end else ""
        middle = char * (length - visible_start - visible_end)
        masked = start + middle + end
    return {**record, field: masked}


def mask_fields(
    record: Dict[str, Any],
    fields: List[str],
    visible_start: int = 0,
    visible_end: int = 0,
    char: str = "*",
) -> Dict[str, Any]:
    """Apply mask_field to multiple fields."""
    for field in fields:
        record = mask_field(record, field, visible_start, visible_end, char)
    return record


def mask_pattern(
    record: Dict[str, Any],
    field: str,
    pattern: str,
    replacement: str = "***",
) -> Dict[str, Any]:
    """Replace regex pattern matches within a field value."""
    if field not in record:
        return record
    value = str(record[field])
    masked = re.sub(pattern, replacement, value)
    return {**record, field: masked}


def mask_records(
    records: List[Dict[str, Any]],
    fields: List[str],
    visible_start: int = 0,
    visible_end: int = 0,
    char: str = "*",
) -> List[Dict[str, Any]]:
    """Apply mask_fields to a list of records."""
    return [
        mask_fields(r, fields, visible_start, visible_end, char)
        for r in records
    ]
