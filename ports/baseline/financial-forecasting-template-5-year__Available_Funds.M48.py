"""Port of Available Funds!M48 from financial-forecasting-template-5-year.xlsx.

Target cell: Available Funds!M48
Formula chain:
    Available Funds!M48 = 'Fiscal Years'!L13
    Fiscal Years!L13   = EDATE(K13, 12)
    ...each column adds 12 months back to B13...
    Fiscal Years!L13   = EDATE(B13, 120)   (10 hops × 12 months)

Input cell: Fiscal Years!B13  (a date)
"""

import calendar
import datetime


def _excel_serial_to_date(serial):
    """Convert an Excel date serial number to a datetime.date.

    Excel's epoch is 1900-01-01 == 1, with the Lotus 1-2-3 leap-year bug
    (it treats 1900 as a leap year, so serial 60 == 1900-02-29 which
    doesn't exist).  We mirror that behaviour.
    """
    serial = int(serial)
    if serial < 1:
        return None
    # Excel serial 1 = 1900-01-01.  But because of the 29-Feb-1900 bug,
    # serials >= 61 are off by one day.
    if serial <= 60:
        base = datetime.date(1899, 12, 31)  # serial 0
        return base + datetime.timedelta(days=serial)
    else:
        base = datetime.date(1899, 12, 30)  # shift by one for the bug
        return base + datetime.timedelta(days=serial)


def _date_to_excel_serial(d):
    """Convert a datetime.date back to an Excel serial number."""
    base = datetime.date(1899, 12, 30)
    delta = (d - base).days
    if delta <= 60:
        delta -= 1  # adjust for the Feb-29 bug region
    return delta


def _edate(start_date, months):
    """Replicates Excel EDATE: add *months* calendar months to *start_date*.

    If the resulting month has fewer days than start_date.day, clip to
    the last day of that month (same as Excel).
    """
    y = start_date.year
    m = start_date.month + months
    # normalise month into 1-12 range
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    max_day = calendar.monthrange(y, m)[1]
    d = min(start_date.day, max_day)
    return datetime.date(y, m, d)


def compute(inputs: dict):
    """Compute Available Funds!M48.

    inputs:
        "Fiscal Years!B13" – date value (datetime, Excel serial int/float,
                             date string, or None)
    Returns: an Excel date serial number (int), matching what Excel stores.
    """
    raw = inputs.get("Fiscal Years!B13")

    # --- coerce input to datetime.date --------------------------------
    if raw is None:
        return 0  # EDATE(blank, ...) returns the serial for 120 months past epoch

    if isinstance(raw, datetime.datetime):
        start = raw.date()
    elif isinstance(raw, datetime.date):
        start = raw
    elif isinstance(raw, (int, float)):
        start = _excel_serial_to_date(raw)
        if start is None:
            return 0
    elif isinstance(raw, str):
        # Try common date formats
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%m-%d-%Y"):
            try:
                start = datetime.datetime.strptime(raw, fmt).date()
                break
            except ValueError:
                continue
        else:
            # Unparseable string – Excel would return #VALUE!; return 0.
            return 0
    else:
        return 0

    # --- apply the formula chain: EDATE(B13, 120) --------------------
    result_date = _edate(start, 120)

    # Return as Excel serial number (int) — same type Excel stores.
    return _date_to_excel_serial(result_date)
