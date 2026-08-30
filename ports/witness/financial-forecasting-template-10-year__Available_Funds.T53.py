from datetime import datetime, date, timedelta
import calendar


def _to_date(v):
    if v is None:
        return datetime(1899, 12, 31)  # serial 0 -> Jan 0, 1900 -> Dec 31, 1899
    if isinstance(v, datetime):
        return v
    if isinstance(v, date):
        return datetime(v.year, v.month, v.day)
    if isinstance(v, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(v.strip(), fmt)
            except ValueError:
                continue
    try:
        serial = float(v)
        si = int(serial)
        # Excel Lotus bug: serials <= 60 use base 1899-12-31, > 60 use 1899-12-30
        if si <= 60:
            base = datetime(1899, 12, 31)
        else:
            base = datetime(1899, 12, 30)
        return base + timedelta(days=si)
    except (TypeError, ValueError):
        return datetime(1899, 12, 31)


def _date_to_serial(dt: datetime) -> int:
    # For dates after Feb 28, 1900 use base 1899-12-30 (accounts for Lotus bug day 60)
    cutoff = datetime(1900, 2, 28)
    if dt <= cutoff:
        base = datetime(1899, 12, 31)
    else:
        base = datetime(1899, 12, 30)
    delta = dt - base
    return int(delta.days)


def _edate(start: datetime, months: int) -> datetime:
    total_months = start.month + months
    year = start.year + (total_months - 1) // 12
    month = (total_months - 1) % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    day = min(start.day, max_day)
    return datetime(year, month, day, start.hour, start.minute, start.second)


def compute(inputs: dict):
    b16 = _to_date(inputs.get("Fiscal Years!B16"))
    current = b16
    for _ in range(17):
        current = _edate(current, 12)
    return _date_to_serial(current)