import math


def _num(v):
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0
    return 0


def _excel_round(x, d=0):
    """ROUND using Excel's round-half-away-from-zero (not Python's banker's rounding)."""
    if d == 0:
        return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1) if x != 0 else 0
    factor = 10 ** d
    return math.floor(abs(x) * factor + 0.5) / factor * (1 if x >= 0 else -1) if x != 0 else 0.0


def _sum_cells(inputs, keys):
    return sum(_num(inputs.get(k)) for k in keys)


def compute(inputs: dict):
    G17 = _sum_cells(inputs, [f"Debt!G{i}" for i in range(11, 17)])

    G20 = 6500 * 2
    G21 = 4305 * 2

    g19 = _num(inputs.get("Debt!G19"))
    g22 = _num(inputs.get("Debt!G22"))
    g23 = _num(inputs.get("Debt!G23"))
    g24 = _num(inputs.get("Debt!G24"))
    G25 = g19 + G20 + G21 + g22 + g23 + g24

    G26 = _excel_round(G17 + G25, 0)
    G6 = G26

    G39 = _sum_cells(inputs, [f"Debt!G{i}" for i in range(31, 39)])

    G41 = 4843.75 + 3293.75
    G42 = 3075 + 2400
    G44 = 101638.75 * 2
    G45 = 25731.25 * 2
    G46 = 4500 * 2

    g43 = _num(inputs.get("Debt!G43"))
    g47 = _num(inputs.get("Debt!G47"))
    g48 = _num(inputs.get("Debt!G48"))
    G49 = G41 + G42 + g43 + G44 + G45 + G46 + g47 + g48

    G50 = _excel_round(G39 + G49, 0)
    G7 = G50

    G8 = G6 + G7
    return G8