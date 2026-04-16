"""Export records to various file formats."""
from __future__ import annotations

import csv
import io
import json
from typing import Iterable


def to_jsonl(records: Iterable[dict]) -> str:
    """Serialize records as newline-delimited JSON."""
    lines = [json.dumps(r, default=str) for r in records]
    return "\n".join(lines) + ("\n" if lines else "")


def to_csv(records: Iterable[dict], fieldnames: list[str] | None = None) -> str:
    """Serialize records as CSV. Infers columns from first record if not given."""
    rows = list(records)
    if not rows:
        return ""
    if fieldnames is None:
        seen: list[str] = []
        for row in rows:
            for k in row:
                if k not in seen:
                    seen.append(k)
        fieldnames = seen
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def to_tsv(records: Iterable[dict], fieldnames: list[str] | None = None) -> str:
    """Serialize records as TSV."""
    rows = list(records)
    if not rows:
        return ""
    if fieldnames is None:
        seen: list[str] = []
        for row in rows:
            for k in row:
                if k not in seen:
                    seen.append(k)
        fieldnames = seen
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fieldnames,
        extrasaction="ignore",
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def write_export(records: Iterable[dict], fmt: str, dest: io.TextIOBase) -> None:
    """Write exported content in *fmt* ('jsonl', 'csv', 'tsv') to *dest*."""
    rows = list(records)
    if fmt == "jsonl":
        dest.write(to_jsonl(rows))
    elif fmt == "csv":
        dest.write(to_csv(rows))
    elif fmt == "tsv":
        dest.write(to_tsv(rows))
    else:
        raise ValueError(f"Unknown export format: {fmt!r}")
