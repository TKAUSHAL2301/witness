from datetime import date, timedelta
import calendar
import math


def _serial_to_date(serial):
    """Convert an Excel serial number to a Python date."""
    if serial <= 0:
        # Excel serial 0 = "January 0, 1900" = Dec 31, 1899
        return date(1899, 12, 31)
    # Excel serial 1 = 1900-01-01
    # Excel wrongly treats 1900 as a leap year (serial 60 = Feb 29 1900)
    if serial <= 60:
        return date(1899, 12, 31) + timedelta(days=int(serial))
    else:
        return date(1899, 12, 30) + timedelta(days=int(serial))


def _date_to_serial(d):
    """Convert a Python date to an Excel serial number (1900 system)."""
    epoch = date(1899, 12, 31)
    delta = (d - epoch).days
    if d >= date(1900, 3, 1):
        delta += 1
    return delta


def _edate(start_date, months):
    """EDATE: add months to a date, clamping to end of month."""
    if start_date is None:
        return None
    if not isinstance(start_date, date):
        return start_date
    year = start_date.year
    month = start_date.month + months
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, max_day)
    return date(year, month, day)


def compute(inputs: dict):
    b16 = inputs.get("Fiscal Years!B16")

    # Convert string to date
    if isinstance(b16, str):
        from datetime import datetime as _dt
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                b16 = _dt.strptime(b16, fmt).date()
                break
            except ValueError:
                continue

    # Convert numeric (Excel serial number) to date
    if isinstance(b16, (int, float)):
        serial = b16
        if isinstance(serial, float):
            serial = math.floor(serial)
        b16 = _serial_to_date(serial)

    val = b16
    for _ in range(11):
        val = _edate(val, 12)

    if isinstance(val, date):
        return _date_to_serial(val)
    return val