"""Enrich records by joining against an external lookup table (dict or JSONL file)."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Iterator, List, Optional

Record = Dict[str, Any]
LookupTable = Dict[str, Record]


def load_lookup_table(path: str, key_field: str) -> LookupTable:
    """Load a JSONL file and index records by *key_field*."""
    table: LookupTable = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if key_field in record:
                table[str(record[key_field])] = record
    return table


def lookup_join(
    records: Iterable[Record],
    table: LookupTable,
    on: str,
    fields: Optional[List[str]] = None,
    prefix: str = "",
    missing: Optional[Record] = None,
) -> Iterator[Record]:
    """Left-join *records* against *table* on field *on*.

    Args:
        records: Source records to enrich.
        table:   Pre-loaded lookup table keyed by the join value.
        on:      Field name in source records used as the join key.
        fields:  Subset of fields to copy from the lookup row (all if None).
        prefix:  Optional prefix applied to copied field names.
        missing: Fallback dict merged when no match is found (default: skip enrichment).
    """
    for record in records:
        key = str(record.get(on, ""))
        row = table.get(key, missing)
        if row is None:
            yield dict(record)
            continue
        extra = {f: row[f] for f in fields if f in row} if fields else dict(row)
        merged = dict(record)
        for k, v in extra.items():
            merged[f"{prefix}{k}"] = v
        yield merged


def lookup_filter(
    records: Iterable[Record],
    table: LookupTable,
    on: str,
    *,
    invert: bool = False,
) -> Iterator[Record]:
    """Keep (or discard) records whose *on* value exists in *table*."""
    for record in records:
        key = str(record.get(on, ""))
        match = key in table
        if match ^ invert:
            yield dict(record)
