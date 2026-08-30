def compute(inputs: dict):
    """Compute Annual!F31 — grand total of 'Other Available Funds' column.

    F31 = SUM(Annual!F5:F28) + SUM(Special!F5:F28)
    """
    total = 0.0
    for key, val in inputs.items():
        if val is None or isinstance(val, (str, bool)):
            # Excel SUM ignores blanks, text, and booleans in cell references
            continue
        total += float(val)
    return total
