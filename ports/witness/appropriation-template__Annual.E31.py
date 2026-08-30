def compute(inputs: dict):
    def excel_sum(keys):
        total = 0
        for k in keys:
            v = inputs.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                total += v
        return total

    annual_cells = [f"Annual!E{r}" for r in range(5, 29)]
    special_cells = [f"Special!E{r}" for r in range(5, 29)]

    e29 = excel_sum(annual_cells)
    e30 = excel_sum(special_cells)
    return e29 + e30