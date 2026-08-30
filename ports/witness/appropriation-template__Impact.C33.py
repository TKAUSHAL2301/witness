def _num(v):
    """Convert a value to a number the way Excel does in SUM."""
    if v is None or v == '':
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0


def compute(inputs: dict):
    def cell(ref):
        return inputs.get(ref)

    # C18 = SUM(C8:C17)
    sum_c8_c17 = sum(_num(cell(f"Impact!C{r}")) for r in range(8, 18))

    # C29 = SUM(C22:C28)
    sum_c22_c28 = sum(_num(cell(f"Impact!C{r}")) for r in range(22, 29))

    # C31 = C18 + C29
    c31 = sum_c8_c17 + sum_c22_c28

    # C33 = C4 + C31
    c4 = _num(cell("Impact!C4"))
    return c4 + c31