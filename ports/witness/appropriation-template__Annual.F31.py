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

    def excel_sum(keys):
        total = 0
        for k in keys:
            v = inputs.get(k)
            if v is None or isinstance(v, str):
                continue
            total += num(v)
        return total

    annual_keys = [f"Annual!F{r}" for r in range(5, 29)]
    special_keys = [f"Special!F{r}" for r in range(5, 29)]

    f29 = excel_sum(annual_keys)
    f30 = excel_sum(special_keys)
    return f29 + f30