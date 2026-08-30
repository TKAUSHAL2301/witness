from datetime import datetime, date, timedelta
import calendar


def _to_date(v):
    if v is None:
        return None
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
    if isinstance(v, (int, float)):
        serial = int(v)
        if serial < 0:
            return None
        if serial == 0:
            # Excel serial 0 = "Jan 0, 1900" treated as 1899-12-31 for EDATE
            return datetime(1899, 12, 31)
        if serial >= 61:
            serial -= 1  # skip Excel's phantom 1900-02-29
        serial -= 1
        base = datetime(1900, 1, 1)
        return base + timedelta(days=serial)
    return None


def _edate(start, months):
    if start is None:
        return None
    year = start.year
    month = start.month + months
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = start.day
    max_day = calendar.monthrange(year, month)[1]
    if day > max_day:
        day = max_day
    return datetime(year, month, day)


def _to_serial(dt):
    if dt is None:
        return None
    base = datetime(1900, 1, 1)
    delta = (dt - base).days + 1  # serial 1 = 1900-01-01
    if delta >= 60:
        delta += 1  # account for Excel's phantom 1900-02-29
    return delta


def compute(inputs: dict):
    b13 = _to_date(inputs.get("Fiscal Years!B13"))
    val = b13
    for _ in range(11):
        val = _edate(val, 12)
    return _to_serial(val)