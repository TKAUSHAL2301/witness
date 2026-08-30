import math


def _num(v):
    if v is None:
        return 0.0
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0
    return 0.0


def _excel_round(value, digits):
    """ROUND that matches Excel: half away from zero."""
    if digits == 0:
        if value >= 0:
            return float(math.floor(value + 0.5))
        else:
            return float(-math.floor(-value + 0.5))
    mult = 10 ** digits
    shifted = value * mult
    if shifted >= 0:
        return math.floor(shifted + 0.5) / mult
    else:
        return -math.floor(-shifted + 0.5) / mult


def compute(inputs: dict):
    g = lambda k: _num(inputs.get(k))

    H17 = g("Debt!H11") + g("Debt!H12") + g("Debt!H13") + g("Debt!H14") + g("Debt!H15") + g("Debt!H16")

    H20 = 5375.0 * 2
    H21 = 3880.0 * 2

    H25 = g("Debt!H19") + H20 + H21 + g("Debt!H22") + g("Debt!H23") + g("Debt!H24")

    H26 = _excel_round(H17 + H25, 0)

    H6 = H26

    H39 = (g("Debt!H31") + g("Debt!H32") + g("Debt!H33") + g("Debt!H34")
         + g("Debt!H35") + g("Debt!H36") + g("Debt!H37") + g("Debt!H38"))

    H41 = 3293.75 + 1743.75
    H42 = 2400.0 + 1800.0
    H44 = 93188.75 * 2
    H45 = 23481.25 * 2
    H46 = 2000.0 * 2

    H49 = H41 + H42 + g("Debt!H43") + H44 + H45 + H46 + g("Debt!H47") + g("Debt!H48")

    H50 = _excel_round(H39 + H49, 0)

    H7 = H50

    H8 = H6 + H7

    return H8