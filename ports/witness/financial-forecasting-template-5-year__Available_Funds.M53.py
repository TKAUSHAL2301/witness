from datetime import date, datetime, timedelta


def _serial_to_date(serial):
    """Convert an Excel serial number to a date (1900 date system)."""
    # Excel serial 0 is treated as 1900-01-00, effectively 1899-12-31
    if serial < 0:
        return None
    if serial == 0:
        return date(1899, 12, 31)
    if serial >= 60:
        serial -= 1  # adjust for Excel's fake 1900-02-29
    epoch = date(1899, 12, 31)
    return epoch + timedelta(days=int(serial))


def _to_date(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, (int, float)):
        return _serial_to_date(val)
    if isinstance(val, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
        try:
            return _serial_to_date(float(val))
        except (ValueError, TypeError):
            pass
    return None


def _edate(start_date, months):
    if start_date is None:
        return None
    import calendar
    year = start_date.year
    month = start_date.month + months
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    max_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, max_day)
    return date(year, month, day)


def _date_to_serial(d):
    """Convert a date to an Excel serial number (1900 date system)."""
    epoch = date(1899, 12, 30)
    delta = (d - epoch).days
    # Adjust for Excel's fake 1900-02-29: serials >= 60 need +1
    if delta >= 60:
        delta += 1
    return delta


def compute(inputs: dict):
    b16 = _to_date(inputs.get("Fiscal Years!B16"))
    if b16 is None:
        return 0

    result = b16
    for _ in range(10):
        result = _edate(result, 12)

    return _date_to_serial(result)