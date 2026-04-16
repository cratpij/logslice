"""High-level Slicer API for chaining filters and exporting results."""
from __future__ import annotations

from typing import Iterable, Iterator

from logslice.filter import (
    filter_by_field,
    filter_by_field_contains,
    filter_by_time,
)
from logslice.parser import parse_lines


class Slicer:
    """Fluent interface for filtering parsed log records."""

    def __init__(self, records: Iterable[dict]) -> None:
        self._records: list[dict] = list(records)

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> "Slicer":
        """Parse raw log lines and return a Slicer over the results."""
        return cls(parse_lines(lines))

    @classmethod
    def from_file(cls, path: str) -> "Slicer":
        """Open *path*, parse every line, and return a Slicer."""
        with open(path, encoding="utf-8") as fh:
            return cls.from_lines(fh)

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    def time_range(
        self,
        start: str | None = None,
        end: str | None = None,
        field: str = "timestamp",
    ) -> "Slicer":
        """Keep records whose *field* falls within [start, end]."""
        return Slicer(filter_by_time(self._records, start=start, end=end, field=field))

    def where(self, field: str, value: str) -> "Slicer":
        """Keep records where *field* equals *value* (case-sensitive)."""
        return Slicer(filter_by_field(self._records, field=field, value=value))

    def where_contains(self, field: str, substring: str) -> "Slicer":
        """Keep records where *field* contains *substring*."""
        return Slicer(
            filter_by_field_contains(self._records, field=field, substring=substring)
        )

    # ------------------------------------------------------------------
    # Terminal operations
    # ------------------------------------------------------------------

    def records(self) -> list[dict]:
        """Return the current filtered record list."""
        return list(self._records)

    def __iter__(self) -> Iterator[dict]:
        return iter(self._records)

    def __len__(self) -> int:
        return len(self._records)

    def export(self, fmt: str, dest) -> None:
        """Write records to *dest* in *fmt* via :mod:`logslice.export`."""
        from logslice.export import write_export

        write_export(self._records, fmt, dest)
