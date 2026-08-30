def compute(inputs: dict):
    """
    Recap Page 2!L22 = SUM(L18:L21) + L4
      L18 = SUM(K7:K16)
      L4  = TOTAPPROP (named range, not an input — defaults to 0)
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

    # L19 is blank-typed, L20 and L21 are number-typed
    l19 = _num(inputs.get("Recap Page 2!L19"))
    l20 = _num(inputs.get("Recap Page 2!L20"))
    l21 = _num(inputs.get("Recap Page 2!L21"))

    # L4 = TOTAPPROP — named range not among inputs, treat as 0
    l4 = 0

    # L22 = SUM(L18:L21) + L4
    return (l18 + l19 + l20 + l21) + l4