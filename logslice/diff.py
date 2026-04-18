"""Compare two sets of log records and report differences."""
from typing import Any


def diff_by_field(
    left: list[dict], right: list[dict], key: str
) -> dict[str, list[dict]]:
    """Return records only in left, only in right, and in both (by key value)."""
    left_index = {r[key]: r for r in left if key in r}
    right_index = {r[key]: r for r in right if key in r}

    left_keys = set(left_index)
    right_keys = set(right_index)

    return {
        "only_left": [left_index[k] for k in sorted(left_keys - right_keys)],
        "only_right": [right_index[k] for k in sorted(right_keys - left_keys)],
        "in_both": [left_index[k] for k in sorted(left_keys & right_keys)],
    }


def diff_field_values(
    left: list[dict], right: list[dict], key: str
) -> list[dict[str, Any]]:
    """For records sharing a key, report fields that changed value."""
    left_index = {r[key]: r for r in left if key in r}
    right_index = {r[key]: r for r in right if key in r}

    changes = []
    for k in sorted(set(left_index) & set(right_index)):
        lr, rr = left_index[k], right_index[k]
        all_fields = set(lr) | set(rr)
        diffs = {}
        for f in all_fields:
            lv = lr.get(f)
            rv = rr.get(f)
            if lv != rv:
                diffs[f] = {"left": lv, "right": rv}
        if diffs:
            changes.append({key: k, "changes": diffs})
    return changes


def count_diff(left: list[dict], right: list[dict], key: str) -> dict[str, int]:
    """Return counts of records only_left, only_right, and in_both."""
    result = diff_by_field(left, right, key)
    return {
        "only_left": len(result["only_left"]),
        "only_right": len(result["only_right"]),
        "in_both": len(result["in_both"]),
    }
