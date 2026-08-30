def compute(inputs: dict):
    def num(v):
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

    F12 = num(inputs.get("Financial Targets!F12"))
    F13 = num(inputs.get("Financial Targets!F13"))
    F14 = num(inputs.get("Financial Targets!F14"))
    F15 = num(inputs.get("Financial Targets!F15"))
    F9 = num(inputs.get("Financial Targets!F9"))
    K12 = num(inputs.get("Financial Targets!K12"))

    # F16 = SUM(F12:F15)
    F16 = F12 + F13 + F14 + F15

    # F18 = F9 - F16
    F18 = F9 - F16

    # G41 = K12
    G41 = K12

    # E41 = G41 / 2
    if G41 == 0:
        return 0.0 / 1  # Excel would return #DIV/0! but G41/2 can't div-by-zero; it's just division by 2
    E41 = G41 / 2.0

    # F41 = E41 * F18
    F41 = E41 * F18

    return F41