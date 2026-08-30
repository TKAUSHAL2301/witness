def _excel_sum(values):
    total = 0
    for v in values:
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            total += v
    return total


def compute(inputs: dict):
    annual_h5_h28 = [inputs.get(f"Annual!H{r}") for r in range(5, 29)]
    special_h5_h28 = [inputs.get(f"Special!H{r}") for r in range(5, 29)]

    h29 = _excel_sum(annual_h5_h28)
    h30 = _excel_sum(special_h5_h28)
    return h29 + h30