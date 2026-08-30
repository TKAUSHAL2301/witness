import math


def compute(inputs: dict):
    """
    Computes Debt!G8 = Total Debt = GF Within-levy Debt Service + GF Gross Excluded Debt Service.

    Formula chain:
        G8  = G6 + G7
        G6  = G26 = ROUND(G17 + G25, 0)
        G17 = SUM(G11:G16)
        G25 = SUM(G19, G20, G21, G22, G23, G24)
              where G20 = 6500*2 = 13000 (constant), G21 = 4305*2 = 8610 (constant)
        G7  = G50 = ROUND(G39 + G49, 0)
        G39 = SUM(G31:G38)
        G49 = SUM(G41:G48)
              where G41 = 4843.75+3293.75 = 8137.5, G42 = 3075+2400 = 5475,
                    G44 = 101638.75*2 = 203277.5, G45 = 25731.25*2 = 51462.5,
                    G46 = 4500*2 = 9000 (all constants)
    """

    def excel_round(x):
        """ROUND(x, 0) with Excel semantics: round half away from zero (not banker's)."""
        if x >= 0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    def n(key):
        """Coerce an input to a number the way Excel does: None/blank -> 0, bool -> int, str -> 0."""
        v = inputs.get(key)
        if v is None:
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, (int, float)):
            return float(v)
        # String: Excel SUM ignores strings; treat as 0
        return 0.0

    # --- Within-levy principal (G17 = SUM(G11:G16)) ---
    g17 = (
        n("Debt!G11")
        + n("Debt!G12")
        + n("Debt!G13")
        + n("Debt!G14")
        + n("Debt!G15")
        + n("Debt!G16")
    )

    # --- Within-levy interest (G25 = SUM(G19:G24)) ---
    # G20 and G21 are constant formulas, not inputs
    g20 = 6500.0 * 2  # =6500*2
    g21 = 4305.0 * 2  # =4305*2
    g25 = (
        n("Debt!G19")
        + g20
        + g21
        + n("Debt!G22")
        + n("Debt!G23")
        + n("Debt!G24")
    )

    # G26 = ROUND(G17 + G25, 0)
    g26 = excel_round(g17 + g25)

    # G6 = G26
    g6 = g26

    # --- Excluded principal (G39 = SUM(G31:G38)) ---
    g39 = (
        n("Debt!G31")
        + n("Debt!G32")
        + n("Debt!G33")
        + n("Debt!G34")
        + n("Debt!G35")
        + n("Debt!G36")
        + n("Debt!G37")
        + n("Debt!G38")
    )

    # --- Excluded interest (G49 = SUM(G41:G48)) ---
    # G41, G42, G44, G45, G46 are constant formulas, not inputs
    g41 = 4843.75 + 3293.75  # =4843.75+3293.75
    g42 = 3075.0 + 2400.0    # =3075+2400
    g44 = 101638.75 * 2       # =101638.75*2
    g45 = 25731.25 * 2        # =25731.25*2
    g46 = 4500.0 * 2          # =4500*2
    g49 = (
        g41
        + g42
        + n("Debt!G43")
        + g44
        + g45
        + g46
        + n("Debt!G47")
        + n("Debt!G48")
    )

    # G50 = ROUND(G39 + G49, 0)
    g50 = excel_round(g39 + g49)

    # G7 = G50
    g7 = g50

    # G8 = G6 + G7 = SUM(G6:G7)
    return g6 + g7
