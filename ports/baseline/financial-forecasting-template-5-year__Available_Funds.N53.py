import datetime
import calendar


def compute(inputs: dict):
    """
    Computes Available Funds!N53.

    Formula chain
    -------------
    Available Funds!N53  =  'Fiscal Years'!M16
    Fiscal Years!M16     =  EDATE(L16, 12)
    ...chained back through C16..L16...
    Fiscal Years!C16     =  EDATE(B16, 12)

    So M16 = B16 with EDATE(+12) applied 11 times  (= +132 months = +11 years).
    """
    val = inputs.get("Fiscal Years!B16")

    # Blank → blank (Excel propagates blanks through EDATE as 0 / 1900-01-00,
    # but the actual EDATE spec returns a #VALUE! for non-numeric input;
    # for blank Excel treats it as 0).
    if val is None:
        val = 0

    # Boolean → int, matching Excel coercion
    if isinstance(val, bool):
        val = int(val)

    # Must be numeric for EDATE
    if not isinstance(val, (int, float)):
        # EDATE returns #VALUE! for text; we mirror that as None.
        return None

    serial = int(val)  # EDATE truncates to integer serial

    # --- helpers -----------------------------------------------------------
    def _serial_to_date(s):
        """Excel serial number → datetime.date (1900 date system, Lotus bug)."""
        if s < 1:
            return datetime.date(1900, 1, 1)  # serial 0 → Jan 0 1900; clamp
        if s <= 60:
            return datetime.date(1900, 1, 1) + datetime.timedelta(days=s - 1)
        # s > 60: subtract 1 for the phantom Feb 29 1900
        return datetime.date(1900, 1, 1) + datetime.timedelta(days=s - 2)

    def _date_to_serial(d):
        """datetime.date → Excel serial number (1900 system, Lotus bug)."""
        delta = (d - datetime.date(1900, 1, 1)).days
        if d >= datetime.date(1900, 3, 1):
            return delta + 2          # +1 one-based, +1 Lotus bug
        return delta + 1              # +1 one-based, no bug offset

    def _edate(s, months):
        """Reimplementation of Excel EDATE(serial, months)."""
        d = _serial_to_date(s)
        total_months = (d.year * 12 + d.month - 1) + months
        y = total_months // 12
        m = total_months % 12 + 1
        max_day = calendar.monthrange(y, m)[1]
        day = min(d.day, max_day)
        return _date_to_serial(datetime.date(y, m, day))
    # ----------------------------------------------------------------------

    # Apply EDATE(+12) eleven times  (B→C→D→E→F→G→H→I→J→K→L→M)
    for _ in range(11):
        serial = _edate(serial, 12)

    return serial
