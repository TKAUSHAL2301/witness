import datetime as _dt
import calendar as _cal

_EPOCH = _dt.date(1899, 12, 30)


def _serial_to_date(serial):
    """Convert an Excel date serial number to a Python date."""
    serial = int(serial)
    if serial <= 0:
        return None
    # Excel has a phantom Feb 29, 1900 at serial 60.
    # For serial <= 59: date = epoch + serial days
    # For serial == 60: not a real date, treat as Mar 1 1900
    # For serial >= 61: date = epoch + serial days (naturally correct)
    return _EPOCH + _dt.timedelta(days=serial)


def _date_to_serial(d):
    """Convert a Python date to an Excel date serial number."""
    return (d - _EPOCH).days


def _edate(start_serial, months):
    """Replicate Excel's EDATE: add `months` months to a date serial."""
    d = _serial_to_date(start_serial)
    if d is None:
        return None
    total_months = (d.year * 12 + d.month - 1) + months
    new_year = total_months // 12
    new_month = total_months % 12 + 1
    max_day = _cal.monthrange(new_year, new_month)[1]
    new_day = min(d.day, max_day)
    return _date_to_serial(_dt.date(new_year, new_month, new_day))


def compute(inputs: dict):
    raw = inputs.get("Fiscal Years!B13")

    if raw is None:
        return None

    if isinstance(raw, _dt.datetime):
        serial = _date_to_serial(raw.date())
    elif isinstance(raw, _dt.date):
        serial = _date_to_serial(raw)
    elif isinstance(raw, (int, float)):
        serial = raw
    else:
        return None

    # Chain: B13 → C13 → ... → S13 = 17 successive EDATE(prev, 12)
    # Available Funds!T48 = 'Fiscal Years'!S13
    for _ in range(17):
        serial = _edate(serial, 12)
        if serial is None:
            return None

    return serial
