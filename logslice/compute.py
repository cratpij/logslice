"""Field computation: derive new fields using arithmetic or string expressions."""

from typing import Any, Callable, Dict, Iterable, List, Optional


def compute_field(
    record: Dict[str, Any],
    dest: str,
    fn: Callable[[Dict[str, Any]], Any],
    overwrite: bool = True,
) -> Dict[str, Any]:
    """Return a copy of *record* with *dest* set to the result of fn(record).

    If *overwrite* is False and *dest* already exists the record is returned
    unchanged.
    """
    if not overwrite and dest in record:
        return record
    result = dict(record)
    try:
        result[dest] = fn(record)
    except (KeyError, TypeError, ZeroDivisionError, ValueError):
        result[dest] = None
    return result


def compute_sum(
    record: Dict[str, Any],
    dest: str,
    fields: List[str],
) -> Dict[str, Any]:
    """Store the numeric sum of *fields* into *dest*."""
    def _fn(r: Dict[str, Any]) -> Optional[float]:
        values = [float(r[f]) for f in fields if f in r]
        return sum(values) if values else None

    return compute_field(record, dest, _fn)


def compute_ratio(
    record: Dict[str, Any],
    dest: str,
    numerator: str,
    denominator: str,
) -> Dict[str, Any]:
    """Store numerator / denominator into *dest*; None on missing or zero denom."""
    def _fn(r: Dict[str, Any]) -> Optional[float]:
        num = float(r[numerator])
        den = float(r[denominator])
        if den == 0:
            raise ZeroDivisionError
        return num / den

    return compute_field(record, dest, _fn)


def compute_concat(
    record: Dict[str, Any],
    dest: str,
    fields: List[str],
    sep: str = " ",
) -> Dict[str, Any]:
    """Concatenate string values of *fields* with *sep* and store in *dest*."""
    def _fn(r: Dict[str, Any]) -> str:
        return sep.join(str(r[f]) for f in fields if f in r)

    return compute_field(record, dest, _fn)


def compute_records(
    records: Iterable[Dict[str, Any]],
    dest: str,
    fn: Callable[[Dict[str, Any]], Any],
    overwrite: bool = True,
) -> List[Dict[str, Any]]:
    """Apply :func:`compute_field` to every record in *records*."""
    return [compute_field(r, dest, fn, overwrite=overwrite) for r in records]
