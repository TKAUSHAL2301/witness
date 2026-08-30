import datetime as _dt
import math as _math


def _excel_serial_to_date(serial):
    """Convert an Excel serial date number to (year, month, day)."""
    # Excel epoch: 1899-12-30, but Excel incorrectly treats 1900 as a leap year.
    # Serial 1 = 1900-01-01, serial 60 = 1900-02-29 (fictitious), serial 61 = 1900-03-01.
    if serial < 1:
        return (1900, 1, 1)
    if serial <= 60:
        base = _dt.date(1899, 12, 31)  # serial 1 = 1900-01-01
        d = base + _dt.timedelta(days=int(serial))
        return (d.year, d.month, d.day)
    # serial > 60: subtract 1 to account for the phantom Feb 29 1900
    base = _dt.date(1899, 12, 30)
    d = base + _dt.timedelta(days=int(serial))
    return (d.year, d.month, d.day)


def _date_to_excel_serial(year, month, day):
    """Convert (year, month, day) to an Excel serial date number."""
    d = _dt.date(year, month, day)
    base = _dt.date(1899, 12, 30)
    serial = (d - base).days
    if serial > 59:
        return serial
    # For dates <= 1900-02-28 (serial 59), no adjustment needed
    return serial


def _edate(serial, months):
    """Excel EDATE: add `months` months to an Excel serial date."""
    y, m, d = _excel_serial_to_date(serial)
    # Add months
    total_months = (y * 12 + (m - 1)) + months
    new_y = total_months // 12
    new_m = total_months % 12 + 1
    # Clamp day to last day of new month
    import calendar
    max_day = calendar.monthrange(new_y, new_m)[1]
    new_d = min(d, max_day)
    return _date_to_excel_serial(new_y, new_m, new_d)


def _to_serial(val):
    """Convert an input value to an Excel serial date number."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, _dt.datetime):
        return _date_to_excel_serial(val.year, val.month, val.day)
    if isinstance(val, _dt.date):
        return _date_to_excel_serial(val.year, val.month, val.day)
    # Try parsing string as a number (Excel serial)
    try:
        return float(val)
    except (ValueError, TypeError):
        return val  # return as-is; will likely error upstream


def compute(inputs: dict):
    """
    Available Funds!T53 = 'Fiscal Years'!S16
    'Fiscal Years'!S16 = EDATE(EDATE(...EDATE(B16, 12)..., 12), 12)
                        (17 successive EDATE(x, 12) from B16, columns C..S)
    """
    b16 = inputs.get("Fiscal Years!B16")
    serial = _to_serial(b16)

    # Apply EDATE(x, 12) seventeen times (columns C through S)
    for _ in range(17):
        serial = _edate(serial, 12)

    return serial
