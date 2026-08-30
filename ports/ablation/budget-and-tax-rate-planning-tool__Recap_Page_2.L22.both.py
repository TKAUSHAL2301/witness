def _num(v):
    """Coerce a value to a number the way Excel does in SUM."""
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
    # L18 = SUM(K7:K16)
    k_cells = [f"Recap Page 2!K{i}" for i in range(7, 17)]
    l18 = sum(_num(inputs.get(c)) for c in k_cells)

    # L19, L20, L21
    l19 = _num(inputs.get("Recap Page 2!L19"))
    l20 = _num(inputs.get("Recap Page 2!L20"))
    l21 = _num(inputs.get("Recap Page 2!L21"))

    # L4 = TOTAPPROP — a named range not among our inputs,
    # so it is externally determined and defaults to 0.
    l4 = 0

    # L22 = SUM(L18:L21) + L4
    l22 = (l18 + l19 + l20 + l21) + l4

    return l22