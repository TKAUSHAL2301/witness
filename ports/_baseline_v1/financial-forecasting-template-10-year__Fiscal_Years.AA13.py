"""Port of Fiscal Years!AA13 — EDATE(B13, 12) chained 25 times (columns B→AA)."""

import calendar
import datetime


def _excel_serial_to_date(serial):
    """Convert an Excel date serial number to a datetime.datetime (1900 system)."""
    if serial < 1:
        return None
    epoch = datetime.date(1899, 12, 30)
    return datetime.datetime.combine(epoch + datetime.timedelta(days=int(serial)),
                                     datetime.time())


def _edate(dt, months):
    """Excel EDATE: add *months* calendar months, clamping day to end-of-month."""
    if dt is None:
        return None
    total_months = (dt.year * 12 + dt.month - 1) + months
    y, m = divmod(total_months, 12)
    m += 1
    max_day = calendar.monthrange(y, m)[1]
    d = min(dt.day, max_day)
    return datetime.datetime(y, m, d, dt.hour, dt.minute, dt.second)


def compute(inputs: dict):
    raw = inputs.get("Fiscal Years!B13")

    # Coerce input to datetime
    if raw is None:
        return None
    if isinstance(raw, datetime.datetime):
        dt = raw
    elif isinstance(raw, datetime.date):
        dt = datetime.datetime.combine(raw, datetime.time())
    elif isinstance(raw, (int, float)):
        dt = _excel_serial_to_date(raw)
        if dt is None:
            return None
    else:
        # Non-numeric text → Excel EDATE returns #VALUE!; we return None.
        return None

    # 25 successive EDATE(…, 12) calls (columns B through AA = 25 steps)
    for _ in range(25):
        dt = _edate(dt, 12)

    return dt