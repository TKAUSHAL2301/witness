def compute(inputs: dict):
    """
    Recap Page 2!L22 = SUM(L18:L21) + L4
    where L18 = SUM(K7:K16) and L4 = TOTAPPROP (not an input, constant 0).
    """

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

    # L18 = SUM(K7:K16)
    l18 = sum(_num(inputs.get(f"Recap Page 2!K{r}")) for r in range(7, 17))

    # L19, L20, L21 are direct inputs
    l19 = _num(inputs.get("Recap Page 2!L19"))
    l20 = _num(inputs.get("Recap Page 2!L20"))
    l21 = _num(inputs.get("Recap Page 2!L21"))

    # L4 = TOTAPPROP — named range not in inputs, defaults to 0
    l4 = 0

    # L22 = SUM(L18:L21) + L4
    return (l18 + l19 + l20 + l21) + l4