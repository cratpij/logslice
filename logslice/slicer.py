"""High-level Slicer: load, filter, transform, and deduplicate log records."""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional

from logslice.filter import filter_by_field, filter_by_field_contains, filter_by_time
from logslice.parser import parse_lines
from logslice.dedupe import dedupe_by_field, dedupe_exact


class Slicer:
    def __init__(self, records: List[Dict[str, Any]]) -> None:
        self._records: List[Dict[str, Any]] = records

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> "Slicer":
        return cls(list(parse_lines(lines)))

    @classmethod
    def from_file(cls, path: str) -> "Slicer":
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_lines(fh)

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def time_range(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        field: str = "timestamp",
    ) -> "Slicer":
        return Slicer(list(filter_by_time(self._records, start=start, end=end, field=field)))

    def where(self, field: str, value: Any) -> "Slicer":
        return Slicer(list(filter_by_field(self._records, field, value)))

    def where_contains(self, field: str, substring: str) -> "Slicer":
        return Slicer(list(filter_by_field_contains(self._records, field, substring)))

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    def dedupe(self, field: Optional[str] = None) -> "Slicer":
        """Remove duplicate records.

        If *field* is given, deduplicate by that field's value; otherwise
        perform exact (whole-record) deduplication.
        """
        if field is not None:
            return Slicer(list(dedupe_by_field(self._records, field)))
        return Slicer(list(dedupe_exact(self._records)))

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def records(self) -> List[Dict[str, Any]]:
        return list(self._records)

    def apply(self, fn: Callable[[Dict[str, Any]], Dict[str, Any]]) -> "Slicer":
        return Slicer([fn(r) for r in self._records])

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self):
        return iter(self._records)
