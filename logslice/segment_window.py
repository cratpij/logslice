"""Combine windowing and segmentation: count segments per time window."""

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from logslice.segment import segment_by_field, split_segments
from logslice.window import tumbling_windows


def segment_window_counts(
    records: Iterable[Dict],
    field: str,
    boundaries: List[Tuple[Any, str]],
    ts_field: str = "timestamp",
    window_seconds: int = 60,
    default: str = "other",
) -> Iterator[Dict]:
    """Yield one summary record per tumbling window with per-segment counts.

    Each output record has:
      - ``window_start``: ISO timestamp of the window start
      - ``window_end``: ISO timestamp of the window end
      - one key per segment label containing the count of records in that segment
    """
    for window in tumbling_windows(records, ts_field=ts_field, seconds=window_seconds):
        window_records = window["records"]
        tagged = list(segment_by_field(window_records, field, boundaries, default=default))
        partitions = split_segments(tagged)
        summary: Dict[str, Any] = {
            "window_start": window["start"],
            "window_end": window["end"],
        }
        # Collect all known labels from boundaries plus default
        all_labels = [label for _, label in boundaries] + [default]
        for label in all_labels:
            summary[label] = len(partitions.get(label, []))
        yield summary


def top_segment_per_window(
    records: Iterable[Dict],
    field: str,
    boundaries: List[Tuple[Any, str]],
    ts_field: str = "timestamp",
    window_seconds: int = 60,
    default: str = "other",
) -> Iterator[Dict]:
    """Yield one record per window identifying the dominant segment."""
    for summary in segment_window_counts(
        records, field, boundaries, ts_field, window_seconds, default
    ):
        all_labels = [label for _, label in boundaries] + [default]
        top = max(all_labels, key=lambda lbl: summary.get(lbl, 0))
        yield {
            "window_start": summary["window_start"],
            "window_end": summary["window_end"],
            "top_segment": top,
            "count": summary.get(top, 0),
        }
