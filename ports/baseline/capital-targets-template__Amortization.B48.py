def compute(inputs: dict):
    """Compute Amortization!B48 from Amortization!B13.

    The spreadsheet builds a year column: B13 is the start fiscal year,
    and each subsequent row adds 1.  B48 is 35 rows below B13, so
    B48 = B13 + 35.
    """
    b13 = inputs.get("Amortization!B13")

    # Excel behaviour: if the cell is blank, arithmetic treats it as 0.
    if b13 is None:
        b13 = 0

    # If the value is not numeric, Excel would return #VALUE!.
    # Mirror that by returning the error string.
    try:
        return b13 + 35
    except TypeError:
        return "#VALUE!"
