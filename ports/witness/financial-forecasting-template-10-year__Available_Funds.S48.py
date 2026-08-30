from datetime import date, datetime, timedelta
import calendar


def _to_date(val):
    """Convert input to a date, handling Excel serial numbers and strings."""
    if val is None:
        return date(1899, 12, 31)  # Excel serial 0 = "Jan 0, 1900" = Dec 31, 1899
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
        return date(1899, 12, 31)
    # Assume Excel serial number
    try:
        serial = int(val)
        if serial <= 0:
            return date(1899, 12, 31) + timedelta(days=serial)
        elif serial <= 59:
            return date(1899, 12, 31) + timedelta(days=serial)
        elif serial == 60:
            # Fake Feb 29, 1900; treat as Feb 28 for calculation purposes
            return date(1900, 2, 28)
        else:
            # serial >= 61: account for the phantom 1900 leap day
            return date(1899, 12, 30) + timedelta(days=serial)
    except (ValueError, TypeError, OverflowError):
        return date(1899, 12, 31)


def _edate(start: date, months: int) -> date:
    """Excel EDATE: add months to a date, clamping day to month end."""
    total_months = start.year * 12 + (start.month - 1) + months
    y, m = divmod(total_months, 12)
    m += 1
    max_day = calendar.monthrange(y, m)[1]
    d = min(start.day, max_day)
    return date(y, m, d)


def _date_to_serial(d: date) -> int:
    """Convert a Python date back to an Excel serial number."""
    cutoff = date(1900, 2, 28)
    if d <= cutoff:
        return (d - date(1899, 12, 31)).days
    else:
        # Add 1 for the phantom Feb 29, 1900 leap day
        return (d - date(1899, 12, 30)).days


def compute(inputs: dict):
    b13 = _to_date(inputs.get("Fiscal Years!B13"))
    # R13 = EDATE applied 16 times (columns B→R), each +12 months = +16 years
    r13 = _edate(b13, 12 * 16)
    # S48 = R13; Excel stores dates as serial numbers
    return _date_to_serial(r13)