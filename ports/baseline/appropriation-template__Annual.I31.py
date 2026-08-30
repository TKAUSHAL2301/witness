def compute(inputs: dict):
    """Compute Annual!I31 — Grand Total of Enterprise Funds.

    Annual!I31 = Annual!I29 + Annual!I30
    Annual!I29 = SUM(Annual!I5:I28)
    Annual!I30 = Special!I29 = SUM(Special!I5:I28)

    So I31 = sum of all Annual!I5..I28 + all Special!I5..I28.
    """

    def _num(v):
        """Coerce a cell value to a number the way Excel SUM does:
        - None (blank) and booleans are treated as 0 by SUM.
        - Strings are ignored by SUM (not an error).
        - Numbers pass through.
        """
        if v is None or isinstance(v, bool) or isinstance(v, str):
            return 0
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0

    total = 0.0
    for sheet in ("Annual", "Special"):
        for row in range(5, 29):  # rows 5..28 inclusive
            total += _num(inputs.get(f"{sheet}!I{row}"))
    return total
