"""Field enrichment: derive or inject new fields into log records."""

from typing import Any, Callable, Dict, Iterable, List, Optional
from logslice.filter import parse_timestamp


def enrich_with_derived(
    records: Iterable[Dict[str, Any]],
    field: str,
    func: Callable[[Dict[str, Any]], Any],
) -> List[Dict[str, Any]]:
    """Add a new field derived by calling func(record) on each record."""
    result = []
    for record in records:
        enriched = dict(record)
        enriched[field] = func(enriched)
        result.append(enriched)
    return result


def enrich_with_constant(
    records: Iterable[Dict[str, Any]],
    field: str,
    value: Any,
) -> List[Dict[str, Any]]:
    """Set a constant value on all records (only if field is absent)."""
    result = []
    for record in records:
        enriched = dict(record)
        if field not in enriched:
            enriched[field] = value
        result.append(enriched)
    return result


def enrich_with_hour(
    records: Iterable[Dict[str, Any]],
    ts_field: str = "timestamp",
    out_field: str = "hour",
) -> List[Dict[str, Any]]:
    """Derive an 'hour' field (0-23) from a timestamp field."""
    result = []
    for record in records:
        enriched = dict(record)
        raw = enriched.get(ts_field)
        if raw:
            dt = parse_timestamp(str(raw))
            if dt is not None:
                enriched[out_field] = dt.hour
        result.append(enriched)
    return result


def enrich_with_date(
    records: Iterable[Dict[str, Any]],
    ts_field: str = "timestamp",
    out_field: str = "date",
) -> List[Dict[str, Any]]:
    """Derive a 'date' string (YYYY-MM-DD) from a timestamp field."""
    result = []
    for record in records:
        enriched = dict(record)
        raw = enriched.get(ts_field)
        if raw:
            dt = parse_timestamp(str(raw))
            if dt is not None:
                enriched[out_field] = dt.strftime("%Y-%m-%d")
        result.append(enriched)
    return result
