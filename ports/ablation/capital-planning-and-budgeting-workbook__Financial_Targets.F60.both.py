def compute(inputs: dict):
    def num(v):
        if v is None:
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            if v.strip() == '':
                return 0.0
            try:
                return float(v)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    F12 = num(inputs.get("Financial Targets!F12"))
    F13 = num(inputs.get("Financial Targets!F13"))
    F14 = num(inputs.get("Financial Targets!F14"))
    F15 = num(inputs.get("Financial Targets!F15"))
    F9 = num(inputs.get("Financial Targets!F9"))
    K16 = num(inputs.get("Financial Targets!K16"))
    K17 = num(inputs.get("Financial Targets!K17"))

    G60 = K16 + K17
    E60 = G60 / 2.0
    F16 = F12 + F13 + F14 + F15
    F18 = F9 - F16
    F60 = E60 * F18

    return F60