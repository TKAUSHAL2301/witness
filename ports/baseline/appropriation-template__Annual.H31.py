def compute(inputs: dict):
    """Compute Annual!H31: grand total of Offset Receipts (Annual + Special)."""

    def _num(val):
        """Convert a cell value to a number the way Excel does."""
        if val is None:
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, bool):
            return 1.0 if val else 0.0
        if isinstance(val, str):
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    total = 0.0
    for sheet in ("Annual", "Special"):
        for row in range(5, 29):  # rows 5..28 inclusive
            total += _num(inputs.get(f"{sheet}!H{row}"))
    return total
