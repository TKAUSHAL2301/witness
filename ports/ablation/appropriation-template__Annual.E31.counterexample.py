def compute(inputs: dict):
    def num(v):
        if v is None or v == '' or v == '':
            return 0
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, (int, float)):
            return v
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    annual_sum = 0
    for r in range(5, 29):
        annual_sum += num(inputs.get(f"Annual!E{r}"))

    special_sum = 0
    for r in range(5, 29):
        special_sum += num(inputs.get(f"Special!E{r}"))

    return annual_sum + special_sum