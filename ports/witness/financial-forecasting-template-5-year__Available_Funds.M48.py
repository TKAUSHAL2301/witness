from datetime import datetime, date
import calendar


def _parse_date(val):
    """Returns (year, month, day) tuple where day can be 0 for serial 0."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return (val.year, val.month, val.day)
    if isinstance(val, date):
        return (val.year, val.month, val.day)
    if isinstance(val, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(val, fmt)
                return (dt.year, dt.month, dt.day)
            except ValueError:
                pass
    if isinstance(val, (int, float)):
        serial = int(val)
        if serial < 0:
            return None
        if serial == 0:
            return (1900, 1, 0)
        if serial == 60:
            return (1900, 2, 28)
        if serial > 60:
            serial -= 1
        from datetime import timedelta
        base = datetime(1899, 12, 31)
        dt = base + timedelta(days=serial)
        return (dt.year, dt.month, dt.day)
    return None


def _edate(ymd, months):
    if ymd is None:
        return None
    year, month, day = ymd
    month += months
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    if day == 0:
        return (year, month, 0)
    day = min(day, calendar.monthrange(year, month)[1])
    return (year, month, day)


def _to_serial(ymd):
    if ymd is None:
        return 0
    year, month, day = ymd
    if day == 0:
        # serial of (year, month, 1) minus 1
        dt = datetime(year, month, 1)
        from datetime import timedelta
        base = datetime(1899, 12, 31)
        delta = (dt - base).days
        if delta >= 60:
            delta += 1
        return delta - 1
    dt = datetime(year, month, day)
    from datetime import timedelta
    base = datetime(1899, 12, 31)
    delta = (dt - base).days
    if delta >= 60:
        delta += 1
    return delta


def compute(inputs: dict):
    b13 = _parse_date(inputs.get("Fiscal Years!B13"))
    if b13 is None:
        return 0

    val = b13
    for _ in range(10):
        val = _edate(val, 12)

    return _to_serial(val)