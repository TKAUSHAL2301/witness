def compute(inputs: dict):
    """Compute Annual!E31 = SUM(Annual!E5:E28) + SUM(Special!E5:E28)."""

    def _num(v):
        """Coerce a cell value to a number the way Excel does in SUM.

        SUM ignores blanks (None), booleans, strings, and errors.
        True/False are ignored by SUM (unlike arithmetic operators).
        """
        if v is None:
            return 0.0
        if isinstance(v, bool):
            # Excel SUM skips booleans in cell references
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        # strings are ignored by SUM
        return 0.0

    total = 0.0
    for row in range(5, 29):  # rows 5..28 inclusive
        total += _num(inputs.get(f"Annual!E{row}"))
        total += _num(inputs.get(f"Special!E{row}"))
    return total
