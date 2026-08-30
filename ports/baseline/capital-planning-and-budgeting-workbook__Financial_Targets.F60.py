def compute(inputs: dict):
    """
    Computes Financial Targets!F60.

    Formula chain:
        F16  = F12 + F13 + F14 + F15
        F18  = F9 - F16                    (Net Operating Revenues)
        G60  = K16 + K17
        E60  = G60 / 2
        F60  = E60 * F18
    Simplified:
        F60  = ((K16 + K17) / 2) * (F9 - (F12 + F13 + F14 + F15))
    """

    def n(key):
        """Coerce a cell value to a number the way Excel does."""
        v = inputs.get(key)
        if v is None or v is True or v is False:
            return 0
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0

    f9 = n("Financial Targets!F9")
    f12 = n("Financial Targets!F12")
    f13 = n("Financial Targets!F13")
    f14 = n("Financial Targets!F14")
    f15 = n("Financial Targets!F15")
    k16 = n("Financial Targets!K16")
    k17 = n("Financial Targets!K17")

    f16 = f12 + f13 + f14 + f15
    f18 = f9 - f16
    g60 = k16 + k17
    e60 = g60 / 2
    f60 = e60 * f18
    return f60
