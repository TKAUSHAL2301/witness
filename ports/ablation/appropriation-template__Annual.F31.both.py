def _num(v):
    """Coerce a cell value to a number the way Excel SUM does:
    None/blank → 0, bool → 1/0, string → 0 (ignored by SUM), number → number."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    # Strings are ignored inside SUM ranges
    return 0


def compute(inputs: dict):
    # Annual!F29 = SUM(Annual!F5:F28)
    annual_sum = sum(_num(inputs.get(f"Annual!F{r}")) for r in range(5, 29))

    # Special!F29 = SUM(Special!F5:F28)
    special_sum = sum(_num(inputs.get(f"Special!F{r}")) for r in range(5, 29))

    # Annual!F30 = Special!F29
    # Annual!F31 = F29 + F30
    return annual_sum + special_sum