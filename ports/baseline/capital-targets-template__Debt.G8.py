import math


def _excel_round(value, digits=0):
    """ROUND() the way Excel does it — half away from zero, not banker's rounding."""
    if digits == 0:
        return int(math.floor(value + 0.5)) if value >= 0 else int(math.ceil(value - 0.5))
    factor = 10 ** digits
    return _excel_round(value * factor) / factor


def compute(inputs: dict):
    """
    Port of Debt!G8 from capital-targets-template.xlsx.

    G8 = SUM(G6:G7)
    G6 = G26 = ROUND(G17 + G25, 0)
    G7 = G50 = ROUND(G39 + G49, 0)

    G17 = SUM(G11:G16)          -- all inputs
    G25 = SUM(G19:G24)          -- G19,G22,G23,G24 are inputs; G20=13000, G21=8610
    G39 = SUM(G31:G38)          -- all inputs
    G49 = SUM(G41:G48)          -- G43,G47,G48 are inputs; G41=8137.50, G42=5475, G44=203277.50, G45=51462.50, G46=9000
    """

    def n(cell):
        """Convert a cell value to a number the way Excel does."""
        v = inputs.get(cell)
        if v is None or v == "":
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # G17 = SUM(G11:G16)
    g17 = sum(n(f"Debt!G{r}") for r in range(11, 17))

    # G25 = SUM(G19:G24)
    # G20 = 6500*2 = 13000 (constant in formula)
    # G21 = 4305*2 = 8610  (constant in formula)
    g25 = n("Debt!G19") + 13000.0 + 8610.0 + n("Debt!G22") + n("Debt!G23") + n("Debt!G24")

    # G26 = ROUND(G17 + G25, 0)
    g26 = _excel_round(g17 + g25)

    # G39 = SUM(G31:G38)
    g39 = sum(n(f"Debt!G{r}") for r in range(31, 39))

    # G49 = SUM(G41:G48)
    # G41 = 4843.75 + 3293.75 = 8137.50
    # G42 = 3075 + 2400       = 5475.00
    # G44 = 101638.75 * 2     = 203277.50
    # G45 = 25731.25 * 2      = 51462.50
    # G46 = 4500 * 2           = 9000.00
    g49 = (8137.50 + 5475.00 + n("Debt!G43") + 203277.50 + 51462.50 + 9000.00
           + n("Debt!G47") + n("Debt!G48"))

    # G50 = ROUND(G39 + G49, 0)
    g50 = _excel_round(g39 + g49)

    # G8 = SUM(G6:G7) = G26 + G50
    return g26 + g50
