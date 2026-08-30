from datetime import date, timedelta
import calendar


def _serial_to_date(serial):
    serial = int(serial)
    if serial < 1:
        return None
    if serial >= 61:
        serial -= 1  # skip phantom Feb 29 1900
    return date(1899, 12, 31) + timedelta(days=serial)


def _parse_date(v):
    if v is None:
        return None
    if isinstance(v, date):
        return v
    if isinstance(v, (int, float)):
        return _serial_to_date(v)
    if isinstance(v, str):
        from datetime import datetime
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(v, fmt).date()
            except ValueError:
                continue
        try:
            return _serial_to_date(float(v))
        except (ValueError, TypeError):
            pass
    return None


def _edate(start, months):
    if start is None:
        return None
    y = start.year
    m = start.month + months
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    d = min(start.day, calendar.monthrange(y, m)[1])
    return date(y, m, d)


def _date_to_serial(d):
    delta = (d - date(1899, 12, 31)).days
    if delta > 59:
        delta += 1  # re-add Lotus bug offset
    return delta


def compute(inputs: dict):
    b16 = _parse_date(inputs.get("Fiscal Years!B16"))
    current = b16
    for _ in range(25):
        current = _edate(current, 12)
    if current is None:
        return None
    return _date_to_serial(current)