def _num(v):
    """Convert a cell value to a number the way Excel SUM does:
    None/blank → 0, bool → int, str → 0 (SUM ignores strings), number → number."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, str):
        # SUM silently skips text cells
        return 0
    return v


def compute(inputs: dict):
    # Annual!E29 = SUM(Annual!E5:E28)
    annual_sum = 0
    for row in range(5, 29):
        annual_sum += _num(inputs.get(f"Annual!E{row}"))

    # Special!E29 = SUM(Special!E5:E28)
    special_sum = 0
    for row in range(5, 29):
        special_sum += _num(inputs.get(f"Special!E{row}"))

    # Annual!E30 = Special!E29
    # Annual!E31 = E29 + E30
    return annual_sum + special_sum