"""Port of Fiscal Years!AA13 — EDATE chain from B13, adding 12 months 25 times."""

import calendar
from datetime import date, datetime


# Excel epoch for serial date numbers (1900 date system, with the
# intentional Lotus-123 leap-year bug for 1900).
_EXCEL_EPOCH = date(1899, 12, 30)


def _to_date(val):
    """Convert an input value to a Python date the way Excel would."""
    if val is None:
        raise _BlankInput
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    # Numeric → Excel serial date number
    if isinstance(val, (int, float)):
        serial = int(val)
        if serial < 1:
            raise _BadDate
        return _EXCEL_EPOCH + __import__("datetime").timedelta(days=serial)
    # String → try ISO parse
    if isinstance(val, str):
        val = val.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
        # Maybe it's a numeric string
        try:
            return _to_date(float(val))
        except (ValueError, _BadDate):
            pass
    raise _BadDate


def _edate(start: date, months: int) -> date:
    """Replicate Excel EDATE: shift by *months*, clamping day."""
    total_months = (start.year * 12 + start.month - 1) + months
    y, m = divmod(total_months, 12)
    m += 1
    max_day = calendar.monthrange(y, m)[1]
    d = min(start.day, max_day)
    return date(y, m, d)


def _date_to_serial(d: date) -> int:
    """Convert a Python date back to an Excel serial number."""
    delta = d - _EXCEL_EPOCH
    serial = delta.days
    # Lotus 1-2-3 bug: Excel thinks 1900-02-29 exists, so serials
    # after 28 Feb 1900 are off by one.
    if serial >= 60:
        serial += 1  # account for phantom 29-Feb-1900 — but only
        # matters for dates before 1 Mar 1900; for modern dates
        # the +1 is already baked into the epoch offset.
    # Actually, the standard approach: epoch is 30-Dec-1899 which
    # already absorbs the bug for dates >= 1-Mar-1900.  Let me just
    # return the raw delta which matches Excel for any modern date.
    return delta.days


class _BlankInput(Exception):
    pass


class _BadDate(Exception):
    pass


def compute(inputs: dict):
    """Return the value of Fiscal Years!AA13.

    AA13 = EDATE(Z13, 12), and the chain goes:
    C13 = EDATE(B13,12), D13 = EDATE(C13,12), ... AA13 = EDATE(Z13,12)
    That is 25 successive applications of EDATE(_, 12) starting from B13.
    Equivalent to EDATE(B13, 300).
    """
    raw = inputs.get("Fiscal Years!B13")

    # Excel EDATE on a blank cell returns a #VALUE! error; we mirror
    # that by returning None (the closest pure-Python analogue).
    try:
        start = _to_date(raw)
    except (_BlankInput, _BadDate):
        return None

    result = _edate(start, 25 * 12)

    # Return as a datetime to match Excel's internal representation.
    return datetime(result.year, result.month, result.day)
