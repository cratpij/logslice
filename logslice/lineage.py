"""Track transformation lineage for records passing through a pipeline."""

from typing import Any, Dict, List, Optional

Record = Dict[str, Any]
LineageEntry = Dict[str, Any]


def start_lineage(record: Record, source: str = "input") -> Record:
    """Attach an initial lineage entry to a record."""
    r = dict(record)
    r["_lineage"] = [{"step": source, "action": "read"}]
    return r


def add_lineage_step(record: Record, step: str, action: str, **meta: Any) -> Record:
    """Append a lineage step to a record's lineage log."""
    r = dict(record)
    entry: LineageEntry = {"step": step, "action": action}
    entry.update(meta)
    existing = list(r.get("_lineage", []))
    existing.append(entry)
    r["_lineage"] = existing
    return r


def get_lineage(record: Record) -> List[LineageEntry]:
    """Return the lineage log for a record, or empty list if absent."""
    return list(record.get("_lineage", []))


def strip_lineage(record: Record) -> Record:
    """Return a copy of the record without the _lineage field."""
    return {k: v for k, v in record.items() if k != "_lineage"}


def lineage_steps(record: Record) -> List[str]:
    """Return just the step names from the lineage log."""
    return [e["step"] for e in get_lineage(record)]


def tag_records(
    records: List[Record],
    step: str,
    action: str,
    source: Optional[str] = None,
    **meta: Any,
) -> List[Record]:
    """Apply a lineage step to every record in a list.

    If *source* is provided and a record has no existing lineage, it is
    initialised with ``start_lineage`` first.
    """
    result = []
    for r in records:
        if source and "_lineage" not in r:
            r = start_lineage(r, source)
        r = add_lineage_step(r, step, action, **meta)
        result.append(r)
    return result
