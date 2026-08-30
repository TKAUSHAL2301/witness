def compute(inputs: dict):
    def num(cell):
        v = inputs.get(cell)
        if v is None:
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        # text in a numeric cell → 0 (Excel SUM / + ignores text or treats as 0)
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # C18 = SUM(C8:C17)
    c18 = sum(num(f"Impact!C{r}") for r in range(8, 18))

    # C29 = SUM(C22:C28)
    c29 = sum(num(f"Impact!C{r}") for r in range(22, 29))

    # C31 = C18 + C29
    c31 = c18 + c29

    # C33 = C4 + C31
    c33 = num("Impact!C4") + c31

    return c33
