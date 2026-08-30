def _num(v):
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
    annual_sum = sum(_num(inputs.get(f"Annual!E{r}")) for r in range(5, 29))
    special_sum = sum(_num(inputs.get(f"Special!E{r}")) for r in range(5, 29))
    return annual_sum + special_sum