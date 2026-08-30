def compute(inputs: dict):
    """Port of Debt!J8 from capital-targets-template.xlsx.

    J8 = SUM(J6:J7)
    J6 = J26 = ROUND(J17 + J25, 0)
    J7 = J50 = ROUND(J39 + J49, 0)
    J17 = SUM(J11:J16)
    J25 = SUM(J19:J24)   where J20=6250, J21=6060 are constants
    J39 = SUM(J31:J38)
    J49 = SUM(J41:J48)   where J42=1800, J44=152577.5, J45=38462.5 are constants
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

    # J17 = SUM(J11:J16)
    j17 = n("Debt!J11") + n("Debt!J12") + n("Debt!J13") + n("Debt!J14") + n("Debt!J15") + n("Debt!J16")

    # J25 = SUM(J19:J24)  — J20 = 3125*2, J21 = 3030*2 are hardcoded constants
    j20 = 3125 * 2   # 6250
    j21 = 3030 * 2   # 6060
    j25 = n("Debt!J19") + j20 + j21 + n("Debt!J22") + n("Debt!J23") + n("Debt!J24")

    # J26 = ROUND(J17 + J25, 0)
    j26 = round(j17 + j25)

    # J39 = SUM(J31:J38)
    j39 = (n("Debt!J31") + n("Debt!J32") + n("Debt!J33") + n("Debt!J34")
           + n("Debt!J35") + n("Debt!J36") + n("Debt!J37") + n("Debt!J38"))

    # J49 = SUM(J41:J48)  — J42 = 1200+600, J44 = 76288.75*2, J45 = 19231.25*2
    j42 = 1200 + 600       # 1800
    j44 = 76288.75 * 2     # 152577.5
    j45 = 19231.25 * 2     # 38462.5
    j49 = (n("Debt!J41") + j42 + n("Debt!J43") + j44 + j45
           + n("Debt!J46") + n("Debt!J47") + n("Debt!J48"))

    # J50 = ROUND(J39 + J49, 0)
    j50 = round(j39 + j49)

    # J8 = SUM(J6:J7) = J26 + J50
    return j26 + j50
