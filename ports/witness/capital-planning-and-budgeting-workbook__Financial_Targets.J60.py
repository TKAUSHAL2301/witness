def _num(v):
    """Convert a value to a number the way Excel does."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        if v.strip() == '':
            return 0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0
    return 0


def compute(inputs: dict):
    F12 = _num(inputs.get("Financial Targets!F12"))
    F13 = _num(inputs.get("Financial Targets!F13"))
    F14 = _num(inputs.get("Financial Targets!F14"))
    F15 = _num(inputs.get("Financial Targets!F15"))
    F9 = _num(inputs.get("Financial Targets!F9"))
    K16 = _num(inputs.get("Financial Targets!K16"))
    K17 = _num(inputs.get("Financial Targets!K17"))

    F16 = F12 + F13 + F14 + F15          # =SUM(F12:F15)
    F18 = F9 - F16                        # =F9-F16
    G60 = K16 + K17                       # =K16+K17
    I60 = G60 * 2                         # =G60*2
    J60 = I60 * F18                       # =I60*$F$18
    return J60