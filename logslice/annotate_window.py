"""Annotate records that fall within a named time window."""

from typing import Any, Dict, Iterable, List, Optional, Tuple

from logslice.filter import parse_timestamp


def annotate_window(
    records: Iterable[Dict[str, Any]],
    windows: List[Tuple[str, str, str]],
    ts_field: str = "timestamp",
    label_field: str = "window",
    default: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Tag each record with the name of the first matching window.

    Args:
        records:     Iterable of log records.
        windows:     List of (name, start_iso, end_iso) tuples.
        ts_field:    Field containing the record timestamp.
        label_field: Field to write the window name into.
        default:     Value to use when no window matches (None omits the field).

    Returns:
        List of annotated records.
    """
    parsed_windows = []
    for name, start, end in windows:
        parsed_windows.append((name, parse_timestamp(start), parse_timestamp(end)))

    result = []
    for record in records:
        r = dict(record)
        raw_ts = r.get(ts_field)
        matched = default

        if raw_ts is not None:
            ts = parse_timestamp(str(raw_ts))
            if ts is not None:
                for name, w_start, w_end in parsed_windows:
                    if w_start <= ts <= w_end:
                        matched = name
                        break

        if matched is not None or default is not None:
            r[label_field] = matched

        result.append(r)
    return result
