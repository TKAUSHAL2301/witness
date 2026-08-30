import math

def compute(inputs: dict):
    def n(key):
        v = inputs.get(key)
        if v is None or v == '' or v is False:
            return 0.0
        if v is True:
            return 1.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    def excel_round(x):
        if x >= 0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    H17 = sum(n(f"Debt!H{r}") for r in range(11, 17))

    H20 = 5375 * 2
    H21 = 3880 * 2

    H25 = n("Debt!H19") + H20 + H21 + n("Debt!H22") + n("Debt!H23") + n("Debt!H24")

    H26 = excel_round(H17 + H25)

    H39 = sum(n(f"Debt!H{r}") for r in range(31, 39))

    H41 = 3293.75 + 1743.75
    H42 = 2400 + 1800
    H44 = 93188.75 * 2
    H45 = 23481.25 * 2
    H46 = 2000 * 2

    H49 = H41 + H42 + n("Debt!H43") + H44 + H45 + H46 + n("Debt!H47") + n("Debt!H48")

    H50 = excel_round(H39 + H49)

    H6 = H26
    H7 = H50

    return H6 + H7