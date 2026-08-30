def _num(v):
    """Coerce a cell value to a number the way Excel SUM does: None and '' → 0, strings → 0 (ignored by SUM), bools → int."""
    if v is None or v == "" or v == '':
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    # SUM ignores text cells
    return 0


def compute(inputs: dict):
    annual_sum = 0
    for row in range(5, 29):
        annual_sum += _num(inputs.get(f"Annual!I{row}"))

    special_sum = 0
    for row in range(5, 29):
        special_sum += _num(inputs.get(f"Special!I{row}"))

    return annual_sum + special_sum