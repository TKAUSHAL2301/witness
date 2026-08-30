def compute(inputs: dict):
    """
    Compute Financial Targets!J60.

    Formula chain:
        F16 = F12 + F13 + F14 + F15
        F18 = F9 - F16                  (Net Operating Revenues)
        G60 = K16 + K17
        I60 = G60 * 2
        J60 = I60 * F18                 (Max debt service % * Net Operating Revenues)

    All inputs that are None (blank) are treated as 0 for arithmetic,
    matching Excel behaviour.
    """

    def num(key):
        v = inputs.get(key)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    F12 = num("Financial Targets!F12")
    F13 = num("Financial Targets!F13")
    F14 = num("Financial Targets!F14")
    F15 = num("Financial Targets!F15")
    F9  = num("Financial Targets!F9")
    K16 = num("Financial Targets!K16")
    K17 = num("Financial Targets!K17")

    F16 = F12 + F13 + F14 + F15
    F18 = F9 - F16                      # Net Operating Revenues
    G60 = K16 + K17
    I60 = G60 * 2
    J60 = I60 * F18
    return J60
