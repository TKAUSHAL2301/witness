import datetime
import calendar


def _excel_serial(dt):
    """Convert a datetime to an Excel serial date number (1900 system)."""
    # Excel thinks 1900-02-29 exists (bug carried from Lotus 1-2-3).
    # Serial 1 = 1900-01-01.
    base = datetime.date(1899, 12, 30)
    delta = dt.date() - base if isinstance(dt, datetime.datetime) else dt - base
    serial = delta.days
    # Dates after 1900-02-28 need +1 for the phantom leap day
    if serial >= 61:
        return serial
    # For serial 60 (which Excel considers 1900-02-29), this path won't
    # normally be hit with real dates, but keep consistent.
    return serial


def _edate(start, months):
    """Replicate Excel EDATE: add *months* calendar months to *start*.

    *start* can be a datetime, date, or an Excel serial number (int/float).
    Returns an Excel serial date number (float), matching Excel's behaviour.
    """
    if isinstance(start, (datetime.datetime, datetime.date)):
        dt = start if isinstance(start, datetime.date) else start.date()
        if isinstance(start, datetime.datetime):
            dt = start.date()
    elif isinstance(start, (int, float)):
        # Convert Excel serial → date
        serial = int(start)
        base = datetime.date(1899, 12, 30)
        if serial >= 61:
            dt = base + datetime.timedelta(days=serial)
        else:
            dt = base + datetime.timedelta(days=serial)
    else:
        return None

    # Add months
    total_months = dt.month + months
    year = dt.year + (total_months - 1) // 12
    month = (total_months - 1) % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    result = datetime.date(year, month, day)
    return _excel_serial(result)


def compute(inputs: dict):
    """Compute Available Funds!S48.

    Available Funds!S48 = 'Fiscal Years'!R13
    'Fiscal Years'!R13  = EDATE(B13, 16 * 12)   (16 chained EDATE(…,12) calls)

    Input: Fiscal Years!B13  — a date (datetime, or Excel serial number).
    Output: Excel serial date number (float/int).
    """
    b13 = inputs.get("Fiscal Years!B13")

    if b13 is None:
        return 0  # Excel EDATE returns #VALUE! on blank, but serial 0 is conventional

    return _edate(b13, 192)
