"""Compare two sets of log records field-by-field and report differences."""

from typing import Any, Dict, Iterator, List, Optional, Tuple

Record = Dict[str, Any]


def compare_records(
    left: Record,
    right: Record,
    fields: Optional[List[str]] = None,
) -> Dict[str, Tuple[Any, Any]]:
    """Return a dict of fields where left and right differ.

    If *fields* is given, only those keys are compared.
    Returns mapping: field -> (left_value, right_value).
    Missing keys are represented as the sentinel ``MISSING``.
    """
    MISSING = object.__new__(object)
    keys = fields if fields is not None else sorted(set(left) | set(right))
    diffs: Dict[str, Tuple[Any, Any]] = {}
    for key in keys:
        lv = left.get(key, MISSING)
        rv = right.get(key, MISSING)
        lv_norm = None if lv is MISSING else lv
        rv_norm = None if rv is MISSING else rv
        l_present = key in left
        r_present = key in right
        if not l_present and not r_present:
            continue
        if lv_norm != rv_norm or l_present != r_present:
            diffs[key] = (lv_norm if l_present else "<missing>", rv_norm if r_present else "<missing>")
    return diffs


def compare_streams(
    left: List[Record],
    right: List[Record],
    key_field: str,
    fields: Optional[List[str]] = None,
) -> Iterator[Dict[str, Any]]:
    """Pair records from left and right by *key_field* and yield diff reports."""
    left_index = {str(r.get(key_field)): r for r in left}
    right_index = {str(r.get(key_field)): r for r in right}
    all_keys = sorted(set(left_index) | set(right_index))
    for k in all_keys:
        l_rec = left_index.get(k)
        r_rec = right_index.get(k)
        if l_rec is None:
            yield {"key": k, "status": "right_only", "record": r_rec, "diffs": {}}
        elif r_rec is None:
            yield {"key": k, "status": "left_only", "record": l_rec, "diffs": {}}
        else:
            diffs = compare_records(l_rec, r_rec, fields)
            status = "changed" if diffs else "equal"
            yield {"key": k, "status": status, "left": l_rec, "right": r_rec, "diffs": diffs}


def changed_only(reports: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    """Filter compare_streams output to only changed / one-sided records."""
    for report in reports:
        if report["status"] != "equal":
            yield report
