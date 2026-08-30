import math


def compute(inputs: dict):
    def num(v):
        if v is None or v == '':
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    def excel_round(x, d=0):
        if d == 0:
            if x >= 0:
                return math.floor(x + 0.5)
            else:
                return math.ceil(x - 0.5)
        factor = 10 ** d
        return excel_round(x * factor) / factor

    g = lambda k: num(inputs.get(k))

    H20 = 5375 * 2
    H21 = 3880 * 2

    H17 = sum(g(f"Debt!H{r}") for r in range(11, 17))
    H25 = g("Debt!H19") + H20 + H21 + g("Debt!H22") + g("Debt!H23") + g("Debt!H24")
    H26 = excel_round(H17 + H25)

    H39 = sum(g(f"Debt!H{r}") for r in range(31, 39))

    H41 = 3293.75 + 1743.75
    H42 = 2400 + 1800
    H44 = 93188.75 * 2
    H45 = 23481.25 * 2
    H46 = 2000 * 2

    H49 = H41 + H42 + g("Debt!H43") + H44 + H45 + H46 + g("Debt!H47") + g("Debt!H48")
    H50 = excel_round(H39 + H49)

    H6 = H26
    H7 = H50

    return H6 + H7