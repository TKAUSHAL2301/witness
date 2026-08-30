"""Port of Available Funds!N48 from financial-forecasting-template-5-year.xlsx.

Target: Available Funds!N48 = 'Fiscal Years'!M13
Chain:  M13 = EDATE(L13,12), L13 = EDATE(K13,12), ... C13 = EDATE(B13,12)
        i.e. EDATE applied 11 times with months=12 each  =>  B13 + 11 years.

EDATE(start_date, months) returns a date that is `months` months after
start_date, preserving the day-of-month (clamped to month-end if needed).

Excel stores dates as serial numbers (days since 1899-12-30).  The result
of the formula chain is a date serial number.
"""

import calendar
import datetime


# Excel epoch (serial 1 == 1900-01-01, but Excel wrongly treats 1900 as a
# leap year, so the effective epoch for serial-to-date conversion is
# 1899-12-30).
_EXCEL_EPOCH = datetime.date(1899, 12, 30)


def _to_serial(d: datetime.date) -> int:
    """Convert a Python date to an Excel serial number."""
    serial = (d - _EXCEL_EPOCH).days
    # Excel erroneously considers 1900-02-29 valid (serial 60).
    # Dates on or after 1900-03-01 (serial 61) are shifted by +1 in Excel.
    if serial >= 60:
        serial += 1  # skip the phantom 1900-02-29
    # Actually, we only need to account for the bug if serial >= 61 (real
    # 1900-03-01).  Serial 60 would be 1900-02-28 which is fine.  But the
    # standard convention is: serials >= 60 get +1.  Let's match that.
    return serial


def _edate(start: datetime.date, months: int) -> datetime.date:
    """Pure-Python EDATE: advance `start` by `months` calendar months."""
    total_months = start.year * 12 + (start.month - 1) + months
    y, m = divmod(total_months, 12)
    m += 1
    # Clamp day to the last day of the target month.
    max_day = calendar.monthrange(y, m)[1]
    d = min(start.day, max_day)
    return datetime.date(y, m, d)


def _parse_date_input(val):
    """Convert an input value to a datetime.date, or return None."""
    if val is None:
        return None
    if isinstance(val, datetime.datetime):
        return val.date()
    if isinstance(val, datetime.date):
        return val
    if isinstance(val, (int, float)):
        # Interpret as Excel serial number.
        serial = int(val)
        if serial < 1:
            return None
        # Undo the Excel 1900 leap-year bug adjustment.
        if serial >= 61:
            serial -= 1
        return _EXCEL_EPOCH + datetime.timedelta(days=serial)
    return None


def compute(inputs: dict):
    """Compute Available Funds!N48.

    Parameters
    ----------
    inputs : dict
        Must contain key ``"Fiscal Years!B13"`` with a value that is either:
        - a ``datetime.datetime`` / ``datetime.date``
        - an Excel serial number (int / float)
        - ``None`` (blank cell) → returns ``None``

    Returns
    -------
    int
        Excel date serial number (what Excel stores in the cell).
    """
    raw = inputs.get("Fiscal Years!B13")
    base = _parse_date_input(raw)
    if base is None:
        return None

    # Apply EDATE(_, 12) eleven times  (B13 → C13 → … → M13).
    date = base
    for _ in range(11):
        date = _edate(date, 12)

    return _to_serial(date)
