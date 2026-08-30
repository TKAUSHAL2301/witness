def _num(v):
    """Coerce a value to a number the way Excel does."""
    if v is None:
        return 0.0
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        if v.strip() == "":
            return 0.0
        try:
            return float(v)
        except (ValueError, OverflowError):
            return 0.0
    return 0.0


def compute(inputs: dict):
    F12 = _num(inputs.get("Financial Targets!F12"))
    F13 = _num(inputs.get("Financial Targets!F13"))
    F14 = _num(inputs.get("Financial Targets!F14"))
    F15 = _num(inputs.get("Financial Targets!F15"))
    F9  = _num(inputs.get("Financial Targets!F9"))
    K16 = _num(inputs.get("Financial Targets!K16"))
    K17 = _num(inputs.get("Financial Targets!K17"))

    # G60 = K16 + K17
    G60 = K16 + K17
    # E60 = G60 / 2
    E60 = G60 / 2
    # F16 = SUM(F12:F15)
    F16 = F12 + F13 + F14 + F15
    # F18 = F9 - F16
    F18 = F9 - F16
    # F60 = E60 * F18
    F60 = E60 * F18

    return F60