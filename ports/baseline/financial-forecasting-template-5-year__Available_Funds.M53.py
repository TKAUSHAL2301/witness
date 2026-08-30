"""Port of Available Funds!M53 from financial-forecasting-template-5-year.xlsx.

Available Funds!M53 = 'Fiscal Years'!L16
'Fiscal Years'!L16 = EDATE(K16, 12), K16 = EDATE(J16, 12), ... back to B16.
That is 10 successive EDATE(_, 12) calls starting from B16, i.e. B16 + 10 years.

EDATE adds calendar months, keeping the same day-of-month (clamped to month end).
Excel stores dates as serial numbers (days since 1899-12-30).  We replicate that
so the return value matches what Excel would show in the cell.
"""

import datetime as _dt


def _to_serial(d: _dt.date) -> int:
    """Convert a Python date to an Excel serial number (1900 date system)."""
    # Excel serial 1 = 1900-01-01.  It also has the Lotus 1-2-3 bug that
    # treats 1900 as a leap year, so serials >= 60 are off by one day.
    delta = d - _dt.date(1899, 12, 30)
    serial = delta.days
    if serial >= 60:          # after the phantom 1900-02-29
        serial += 1
    return serial


def _edate(serial, months):
    """Replicate Excel EDATE: add *months* calendar months to *serial*."""
    # Convert serial to date
    # Undo the Lotus bug adjustment
    if serial >= 60:
        serial -= 1
    base = _dt.date(1899, 12, 30) + _dt.timedelta(days=serial)

    # Add months
    total_months = (base.year * 12 + base.month - 1) + months
    y, m = divmod(total_months, 12)
    m += 1
    # Clamp day to month end
    import calendar
    max_day = calendar.monthrange(y, m)[1]
    day = min(base.day, max_day)
    result = _dt.date(y, m, day)
    return _to_serial(result)


def _parse_date_input(val):
    """Turn the input value into an Excel serial number, the way Excel would."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, _dt.datetime):
        return _to_serial(val.date())
    if isinstance(val, _dt.date):
        return _to_serial(val)
    if isinstance(val, str):
        # Try ISO-ish parse
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return _to_serial(_dt.datetime.strptime(val, fmt).date())
            except ValueError:
                continue
        # If it's a plain number string, treat as serial
        try:
            return int(float(val))
        except ValueError:
            return 0  # Excel #VALUE! — we return 0 as a safe fallback
    return 0


def compute(inputs: dict):
    """Compute Available Funds!M53 given Fiscal Years!B16."""
    b16 = inputs.get("Fiscal Years!B16")
    serial = _parse_date_input(b16)

    # Apply EDATE(_, 12) ten times (B16 → C16 → … → L16)
    current = serial
    for _ in range(10):
        current = _edate(current, 12)

    return current
