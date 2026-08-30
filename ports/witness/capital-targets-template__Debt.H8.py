def compute(inputs: dict):
    """
    Port of Debt!H8 from capital-targets-template.xlsx

    H8 = SUM(H6:H7)
    H6 = H26 = ROUND(H17 + H25, 0)
    H7 = H50 = ROUND(H39 + H49, 0)

    H17 = SUM(H11:H16)                    — all inputs
    H25 = SUM(H19:H24)                    — H19,H22,H23,H24 inputs; H20=5375*2, H21=3880*2 constants
    H39 = SUM(H31:H38)                    — all inputs
    H49 = SUM(H41:H48)                    — H43,H47,H48 inputs; H41=3293.75+1743.75, H42=2400+1800,
                                             H44=93188.75*2, H45=23481.25*2, H46=2000*2 constants
    """

    def n(cell):
        """Coerce a cell value to a number the way Excel does."""
        v = inputs.get(cell)
        if v is None or v == "":
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # H17 = SUM(H11:H16)
    h17 = n("Debt!H11") + n("Debt!H12") + n("Debt!H13") + n("Debt!H14") + n("Debt!H15") + n("Debt!H16")

    # H20, H21 are constant formulas (not inputs)
    h20 = 5375 * 2       # 10750
    h21 = 3880 * 2       # 7760

    # H25 = SUM(H19:H24)
    h25 = n("Debt!H19") + h20 + h21 + n("Debt!H22") + n("Debt!H23") + n("Debt!H24")

    # H26 = ROUND(H17 + H25, 0)
    h26 = round(h17 + h25)

    # H6 = H26
    h6 = h26

    # H39 = SUM(H31:H38)
    h39 = (n("Debt!H31") + n("Debt!H32") + n("Debt!H33") + n("Debt!H34")
         + n("Debt!H35") + n("Debt!H36") + n("Debt!H37") + n("Debt!H38"))

    # H41..H46 are constant formulas (not inputs)
    h41 = 3293.75 + 1743.75    # 5037.5
    h42 = 2400 + 1800          # 4200
    h44 = 93188.75 * 2         # 186377.5
    h45 = 23481.25 * 2         # 46962.5
    h46 = 2000 * 2             # 4000

    # H49 = SUM(H41:H48)
    h49 = h41 + h42 + n("Debt!H43") + h44 + h45 + h46 + n("Debt!H47") + n("Debt!H48")

    # H50 = ROUND(H39 + H49, 0)
    h50 = round(h39 + h49)

    # H7 = H50
    h7 = h50

    # H8 = SUM(H6:H7) = H6 + H7
    return h6 + h7
