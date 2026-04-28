"""Fill missing field values in records using interpolation strategies."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

Record = Dict[str, Any]


def fill_forward(records: List[Record], field: str) -> List[Record]:
    """Fill missing values by carrying the last seen value forward."""
    result = []
    last_value: Optional[Any] = None
    for record in records:
        r = dict(record)
        if field in r and r[field] is not None:
            last_value = r[field]
        elif last_value is not None:
            r[field] = last_value
        result.append(r)
    return result


def fill_backward(records: List[Record], field: str) -> List[Record]:
    """Fill missing values by propagating the next seen value backward."""
    result = list(records)
    next_value: Optional[Any] = None
    for i in range(len(result) - 1, -1, -1):
        r = dict(result[i])
        if field in r and r[field] is not None:
            next_value = r[field]
        elif next_value is not None:
            r[field] = next_value
        result[i] = r
    return result


def fill_constant(records: Iterable[Record], field: str, value: Any) -> Iterator[Record]:
    """Fill missing or None values with a constant."""
    for record in records:
        r = dict(record)
        if r.get(field) is None:
            r[field] = value
        yield r


def fill_linear(
    records: List[Record], field: str, key: str = "index"
) -> List[Record]:
    """Linearly interpolate numeric gaps between known values.

    Records without the field (or with None) between two records that have
    numeric values will receive interpolated values.  Non-numeric endpoints
    are left untouched.
    """
    result = [dict(r) for r in records]
    n = len(result)
    i = 0
    while i < n:
        if result[i].get(field) is None:
            # find the start of the gap
            start = i - 1
            # find the end of the gap
            j = i
            while j < n and result[j].get(field) is None:
                j += 1
            end = j
            if start >= 0 and end < n:
                try:
                    v_start = float(result[start][field])
                    v_end = float(result[end][field])
                    span = end - start
                    for k in range(start + 1, end):
                        frac = (k - start) / span
                        result[k][field] = v_start + frac * (v_end - v_start)
                except (TypeError, ValueError, KeyError):
                    pass
            i = j
        else:
            i += 1
    return result
