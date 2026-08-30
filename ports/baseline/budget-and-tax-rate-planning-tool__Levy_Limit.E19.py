import math


def _excel_round(value, digits):
    """Excel ROUND: round half away from zero (not banker's rounding)."""
    if digits == 0:
        if value >= 0:
            return math.floor(value + 0.5)
        else:
            return math.ceil(value - 0.5)
    factor = 10 ** digits
    return _excel_round(value * factor, 0) / factor


def compute(inputs: dict):
    """Port of Levy Limit!E19 from budget-and-tax-rate-planning-tool.xlsx.

    E19 = IF(C18 > C20, C20, C18)
    where:
        C14 = ROUND((C12 + C13) * 0.025, 0)
        C18 = SUM(C12:C17)  i.e. C12 + C13 + C14 + C15 + C16 + C17
        C20 is an input (Levy Ceiling)
    """

    def num(key):
        v = inputs.get(key)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    c12 = num("Levy Limit!C12")
    c13 = num("Levy Limit!C13")
    c15 = num("Levy Limit!C15")
    c16 = num("Levy Limit!C16")
    c17 = num("Levy Limit!C17")
    c20 = num("Levy Limit!C20")

    # C14 = ROUND((C12 + C13) * 0.025, 0)
    c14 = _excel_round((c12 + c13) * 0.025, 0)

    # C18 = SUM(C12:C17) = C12 + C13 + C14 + C15 + C16 + C17
    c18 = c12 + c13 + c14 + c15 + c16 + c17

    # E19 = IF(C18 > C20, C20, C18)
    if c18 > c20:
        return c20
    return c18
