def compute(inputs: dict):
    """Compute Amortization!A48 from Amortization!A22.

    In the workbook, A22 holds a year number (10).  Rows A23:A48 each add 1
    to the previous row (=A_prev + 1), so A48 = A22 + 26.

    Excel behaviour for edge cases:
    - None (blank) is treated as 0 by the + operator.
    - A non-numeric value (string) would cause #VALUE! in Excel;
      we return the same as Excel by propagating the error.
    """
    a22 = inputs.get("Amortization!A22")

    # Excel treats blank cells as 0 in arithmetic.
    if a22 is None:
        a22 = 0

    # If the value isn't numeric, Excel's "=A22+1" returns #VALUE!.
    # We mirror that by returning the string "#VALUE!".
    if not isinstance(a22, (int, float)):
        return "#VALUE!"

    return a22 + 26
