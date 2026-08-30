"""Port of Fiscal Years!AA16 from financial-forecasting-template-10-year.xlsx.

AA16 is the result of applying EDATE(_, 12) twenty-five times starting from B16.
Each step adds 12 months (1 year), clamping the day to the last day of the
target month (standard Excel EDATE behaviour).
"""

from datetime import datetime
from calendar import monthrange


def _edate(dt: datetime, months: int) -> datetime:
    """Excel EDATE: shift *dt* by *months*, clamping day to month-end."""
    total = dt.month - 1 + months
    year = dt.year + total // 12
    month = total % 12 + 1
    day = min(dt.day, monthrange(year, month)[1])
    return datetime(year, month, day)


def compute(inputs: dict):
    """Return the value of Fiscal Years!AA16.

    Parameters
    ----------
    inputs : dict
        Must contain ``"Fiscal Years!B16"`` mapped to a datetime (or an
        Excel serial-date number, or None).
    """
    raw = inputs.get("Fiscal Years!B16")

    # Handle blank / non-date inputs the way Excel does: EDATE returns #VALUE!
    # on non-numeric / non-date input.  We mirror that by returning None.
    if raw is None:
        return None

    if isinstance(raw, datetime):
        dt = raw
    elif isinstance(raw, (int, float)):
        # Interpret as an Excel serial date number (1900 date system).
        try:
            serial = int(raw)
            if serial < 1:
                return None
            base = datetime(1899, 12, 30)
            from datetime import timedelta
            dt = base + timedelta(days=serial)
        except (ValueError, OverflowError):
            return None
    else:
        return None

    # Apply EDATE(_, 12) twenty-five times (columns C through AA).
    result = dt
    for _ in range(25):
        result = _edate(result, 12)

    return result
