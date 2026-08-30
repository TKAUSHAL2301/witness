def compute(inputs: dict):
    def num(v):
        if v is None:
            return 0
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
            if v == '':
                return 0
            try:
                return float(v)
            except (ValueError, TypeError):
                return 0
        return 0

    annual_sum = sum(num(inputs.get(f"Annual!I{r}")) for r in range(5, 29))
    special_sum = sum(num(inputs.get(f"Special!I{r}")) for r in range(5, 29))
    return annual_sum + special_sum