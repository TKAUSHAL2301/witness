import math


def _num(v):
    """Coerce a value to a number the way Excel does."""
    if v is None:
        return 0.0
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def _excel_round(value, digits):
    """Excel ROUND: rounds half away from zero (not banker's rounding)."""
    if digits == 0:
        if value >= 0:
            return math.floor(value + 0.5)
        else:
            return math.ceil(value - 0.5)
    factor = 10 ** digits
    if value >= 0:
        return math.floor(value * factor + 0.5) / factor
    else:
        return math.ceil(value * factor - 0.5) / factor


def compute(inputs: dict):
    c25 = _num(inputs.get("Levy Limit!C25"))
    c27 = _num(inputs.get("Levy Limit!C27"))
    c28 = _num(inputs.get("Levy Limit!C28"))
    c29 = _num(inputs.get("Levy Limit!C29"))

    # C24 = levylimI (named range, not among inputs → 0)
    c24 = 0.0

    # C26 = ROUND((C24 + C25) * 0.025, 0)
    c26 = _excel_round((c24 + c25) * 0.025, 0)

    # C30 = SUM(C24:C29)
    c30 = c24 + c25 + c26 + c27 + c28 + c29

    # C32 = optiontot * 0.025 (named range, not among inputs → 0)
    c32 = 0.0

    # E31 = IF(C30 > C32, C32, C30)
    if c30 > c32:
        return c32
    else:
        return c30