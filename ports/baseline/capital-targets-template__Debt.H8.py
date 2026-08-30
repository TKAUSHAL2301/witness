import math


def compute(inputs: dict):
    """
    Computes Debt!H8 (Total Debt) from the given input cells.

    H8 = SUM(H6:H7)
    H6 = H26 = ROUND(H17 + H25, 0)
      H17 = SUM(H11:H16)          -- within-levy principal
      H25 = SUM(H19:H24)          -- within-levy interest
    H7 = H50 = ROUND(H39 + H49, 0)
      H39 = SUM(H31:H38)          -- excluded principal
      H49 = SUM(H41:H48)          -- excluded interest
    """

    def excel_round(x, digits=0):
        """ROUND(x, digits) with Excel semantics (half away from zero)."""
        if digits == 0:
            return int(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1)
        m = 10 ** digits
        return math.floor(abs(x) * m + 0.5) / m * (1 if x >= 0 else -1)

    def n(key):
        """Convert an input to a number the way Excel would."""
        v = inputs.get(key)
        if v is None or v is True or v is False:
            return 0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    # Within-levy principal: SUM(H11:H16)
    h17 = n("Debt!H11") + n("Debt!H12") + n("Debt!H13") + n("Debt!H14") + n("Debt!H15") + n("Debt!H16")

    # Within-levy interest: SUM(H19:H24)
    # H19 is an input; H20 and H21 are formulas over constants; H22-H24 are inputs
    h20 = 5375 * 2   # =5375*2
    h21 = 3880 * 2   # =3880*2
    h25 = n("Debt!H19") + h20 + h21 + n("Debt!H22") + n("Debt!H23") + n("Debt!H24")

    # H6 = H26 = ROUND(H17 + H25, 0)
    h6 = excel_round(h17 + h25)

    # Excluded principal: SUM(H31:H38)
    h39 = (n("Debt!H31") + n("Debt!H32") + n("Debt!H33") + n("Debt!H34")
         + n("Debt!H35") + n("Debt!H36") + n("Debt!H37") + n("Debt!H38"))

    # Excluded interest: SUM(H41:H48)
    # H41, H42, H44, H45, H46 are formulas over constants; H43, H47, H48 are inputs
    h41 = 3293.75 + 1743.75   # =3293.75+1743.75
    h42 = 2400 + 1800         # =2400+1800
    h44 = 93188.75 * 2        # =93188.75*2
    h45 = 23481.25 * 2        # =23481.25*2
    h46 = 2000 * 2            # =2000*2
    h49 = h41 + h42 + n("Debt!H43") + h44 + h45 + h46 + n("Debt!H47") + n("Debt!H48")

    # H7 = H50 = ROUND(H39 + H49, 0)
    h7 = excel_round(h39 + h49)

    # H8 = SUM(H6:H7)
    return h6 + h7
