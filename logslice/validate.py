"""Field validation and schema checking for log records."""
from typing import Any, Dict, List, Optional


def require_fields(record: Dict[str, Any], fields: List[str]) -> List[str]:
    """Return list of required fields missing from record."""
    return [f for f in fields if f not in record]


def validate_type(record: Dict[str, Any], field: str, expected_type: type) -> bool:
    """Return True if field exists and matches expected type."""
    if field not in record:
        return False
    return isinstance(record[field], expected_type)


def validate_schema(
    record: Dict[str, Any],
    required: Optional[List[str]] = None,
    types: Optional[Dict[str, type]] = None,
) -> List[str]:
    """Validate a record against required fields and type constraints.

    Returns a list of error strings; empty list means valid.
    """
    errors: List[str] = []

    if required:
        missing = require_fields(record, required)
        for f in missing:
            errors.append(f"missing required field: '{f}'")

    if types:
        for field, expected in types.items():
            if field in record and not isinstance(record[field], expected):
                actual = type(record[field]).__name__
                errors.append(
                    f"field '{field}' expected {expected.__name__}, got {actual}"
                )

    return errors


def filter_valid(
    records: List[Dict[str, Any]],
    required: Optional[List[str]] = None,
    types: Optional[Dict[str, type]] = None,
) -> List[Dict[str, Any]]:
    """Return only records that pass schema validation."""
    return [
        r for r in records
        if not validate_schema(r, required=required, types=types)
    ]


def partition_valid(
    records: List[Dict[str, Any]],
    required: Optional[List[str]] = None,
    types: Optional[Dict[str, type]] = None,
) -> tuple:
    """Split records into (valid, invalid) based on schema validation."""
    valid, invalid = [], []
    for r in records:
        if validate_schema(r, required=required, types=types):
            invalid.append(r)
        else:
            valid.append(r)
    return valid, invalid
