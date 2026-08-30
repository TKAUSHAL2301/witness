def compute(inputs: dict):
    def excel_sum(values):
        total = 0
        for v in values:
            if isinstance(v, bool):
                continue  # SUM ignores booleans in cell references
            if isinstance(v, (int, float)):
                total += v
            # None and strings are ignored by SUM
        return total

    annual_vals = [inputs.get(f"Annual!F{r}") for r in range(5, 29)]
    special_vals = [inputs.get(f"Special!F{r}") for r in range(5, 29)]

    f29 = excel_sum(annual_vals)   # Annual!F29
    sf29 = excel_sum(special_vals) # Special!F29
    f30 = sf29                     # Annual!F30
    return f29 + f30               # Annual!F31