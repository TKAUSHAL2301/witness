def _num(v):
    """Coerce a value to a number the way Excel does."""
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
        except (ValueError, OverflowError):
            return 0.0
    return 0.0


def compute(inputs: dict):
    g = lambda k: _num(inputs.get(k))

    # J17 = SUM(J11:J16)
    j17 = g("Debt!J11") + g("Debt!J12") + g("Debt!J13") + g("Debt!J14") + g("Debt!J15") + g("Debt!J16")

    # J20 = 3125*2, J21 = 3030*2
    j20 = 3125 * 2
    j21 = 3030 * 2

    # J25 = SUM(J19:J24)
    j25 = g("Debt!J19") + j20 + j21 + g("Debt!J22") + g("Debt!J23") + g("Debt!J24")

    # J26 = ROUND(J17+J25, 0)
    j26 = round(j17 + j25, 0)

    # J39 = SUM(J31:J38)
    j39 = (g("Debt!J31") + g("Debt!J32") + g("Debt!J33") + g("Debt!J34")
           + g("Debt!J35") + g("Debt!J36") + g("Debt!J37") + g("Debt!J38"))

    # J42 = 1200+600, J44 = 76288.75*2, J45 = 19231.25*2
    j42 = 1200 + 600
    j44 = 76288.75 * 2
    j45 = 19231.25 * 2

    # J49 = SUM(J41:J48)
    j49 = g("Debt!J41") + j42 + g("Debt!J43") + j44 + j45 + g("Debt!J46") + g("Debt!J47") + g("Debt!J48")

    # J50 = ROUND(J39+J49, 0)
    j50 = round(j39 + j49, 0)

    # J6 = J26, J7 = J50
    # J8 = SUM(J6:J7)
    return j26 + j50