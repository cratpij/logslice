"""High-level Slicer: chains parser + filters + optional stats."""
from typing import Iterable, Iterator, Optional
from logslice.parser import parse_lines
from logslice.filter import filter_by_time, filter_by_field, filter_by_field_contains
from logslice.stats import summary as compute_summary


class Slicer:
    """Fluent interface for filtering log lines."""

    def __init__(self, lines: Iterable[str]) -> None:
        self._records: list[dict] = list(parse_lines(lines))

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    def time_range(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        field: str = "timestamp",
    ) -> "Slicer":
        """Keep records whose *field* falls within [start, end]."""
        self._records = list(
            filter_by_time(self._records, start=start, end=end, field=field)
        )
        return self

    def where(self, field: str, value: str) -> "Slicer":
        """Keep records where *field* equals *value* (string comparison)."""
        self._records = list(filter_by_field(self._records, field, value))
        return self

    def where_contains(self, field: str, substring: str) -> "Slicer":
        """Keep records where *field* contains *substring*."""
        self._records = list(
            filter_by_field_contains(self._records, field, substring)
        )
        return self

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def records(self) -> list[dict]:
        """Return the current filtered records."""
        return list(self._records)

    def __iter__(self) -> Iterator[dict]:
        return iter(self._records)

    def __len__(self) -> int:
        return len(self._records)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return a summary dict for the current set of records."""
        return compute_summary(self._records)

    def count_by(self, field: str):
        """Delegate to stats.count_by_field for the current records."""
        from logslice.stats import count_by_field
        return count_by_field(self._records, field)
