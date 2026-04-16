"""High-level slicer: combines parsing and filtering into a single pipeline."""

from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional

from logslice.parser import parse_lines
from logslice.filter import filter_by_time, filter_by_field, filter_by_field_contains

LogEntry = Dict[str, Any]


class Slicer:
    """Chain multiple filters over a stream of raw log lines."""

    def __init__(
        self,
        lines: Iterable[str],
        timestamp_field: str = "timestamp",
    ):
        self._lines = lines
        self._timestamp_field = timestamp_field
        self._time_start: Optional[datetime] = None
        self._time_end: Optional[datetime] = None
        self._field_filters: List[tuple] = []
        self._contains_filters: List[tuple] = []

    def time_range(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> "Slicer":
        self._time_start = start
        self._time_end = end
        return self

    def where(
        self,
        field: str,
        value: Any,
    ) -> "Slicer":
        self._field_filters.append((field, value))
        return self

    def where_contains(
        self,
        field: str,
        substring: str,
    ) -> "Slicer":
        self._contains_filters.append((field, substring))
        return self

    def run(self) -> Iterator[LogEntry]:
        """Execute the pipeline and yield matching log entries."""
        entries: Iterator[LogEntry] = (
            e for e in parse_lines(self._lines) if e is not None
        )

        if self._time_start or self._time_end:
            entries = filter_by_time(
                entries,
                timestamp_field=self._timestamp_field,
                start=self._time_start,
                end=self._time_end,
            )

        for field, value in self._field_filters:
            entries = filter_by_field(entries, field, value)

        for field, substring in self._contains_filters:
            entries = filter_by_field_contains(entries, field, substring)

        yield from entries
