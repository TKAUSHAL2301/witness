import math


def _num(v):
    """Coerce a value to a number the way Excel does: None/blank→0, bool→int, str→0 (in SUM context)."""
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


def _excel_round(value, digits):
    """ROUND using Excel's half-away-from-zero semantics."""
    if value == 0:
        return 0
    factor = 10 ** digits
    return int(math.floor(abs(value) * factor + 0.5)) / factor * (1 if value >= 0 else -1)


def compute(inputs: dict):
    C25 = _num(inputs.get("Levy Limit!C25"))
    C27 = _num(inputs.get("Levy Limit!C27"))
    C28 = _num(inputs.get("Levy Limit!C28"))
    C29 = _num(inputs.get("Levy Limit!C29"))

    # C24 = levylimI (named range, not an input → 0)
    C24 = 0
    # C26 = ROUND((C24 + C25) * 0.025, 0)
    C26 = _excel_round((C24 + C25) * 0.025, 0)
    # C30 = SUM(C24:C29)
    C30 = C24 + C25 + C26 + C27 + C28 + C29
    # C32 = optiontot * 0.025 (named range, not an input → 0)
    C32 = 0
    # E31 = IF(C30 > C32, C32, C30)
    if C30 > C32:
        return C32
    else:
        return C30