from datetime import datetime, date


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
        return None
    if isinstance(v, (int, float)):
        serial = int(v)
        if serial < 0:
            return None
        from datetime import timedelta
        if serial == 0:
            return datetime(1899, 12, 31)
        if serial <= 60:
            base = datetime(1899, 12, 31)
        else:
            base = datetime(1899, 12, 30)
        return base + timedelta(days=serial)
    return None


def _edate(start, months):
    if start is None:
        return None
    y = start.year
    m = start.month + months
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    d = start.day
    import calendar
    max_d = calendar.monthrange(y, m)[1]
    if d > max_d:
        d = max_d
    return datetime(y, m, d, start.hour, start.minute, start.second)


def _to_serial(dt):
    if dt is None:
        return None
    from datetime import timedelta
    base = datetime(1899, 12, 30)
    delta = dt - base
    serial = delta.days
    if serial <= 60:
        serial -= 1
    return serial


def compute(inputs: dict):
    b16 = _to_date(inputs.get("Fiscal Years!B16"))
    current = b16
    for _ in range(25):
        current = _edate(current, 12)
    return _to_serial(current)