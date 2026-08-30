def compute(inputs: dict):
    """
    Port of Debt!I8 from capital-targets-template.xlsx.

    I8 = SUM(I6:I7)
    I6 = I26 = ROUND(I17 + I25, 0)
    I7 = I50 = ROUND(I39 + I49, 0)

    I17 = SUM(I11:I16)                          — all inputs
    I25 = SUM(I19:I24)                          — I19,I22,I23,I24 are inputs;
                                                  I20 = 4250*2, I21 = 3455*2 are constants
    I39 = SUM(I31:I38)                          — all inputs
    I49 = SUM(I41:I48)                          — I41,I43,I46,I47,I48 are inputs;
                                                  I42 = 1800+1200, I44 = 84738.75*2,
                                                  I45 = 21356.25*2 are constants
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

    # --- first block (I6 path) ---
    i17 = n("Debt!I11") + n("Debt!I12") + n("Debt!I13") + n("Debt!I14") + n("Debt!I15") + n("Debt!I16")

    i20 = 4250 * 2    # 8500  (hard-coded formula in workbook)
    i21 = 3455 * 2    # 6910  (hard-coded formula in workbook)
    i25 = n("Debt!I19") + i20 + i21 + n("Debt!I22") + n("Debt!I23") + n("Debt!I24")

    i26 = round(i17 + i25)   # ROUND(..., 0)
    i6 = i26

    # --- second block (I7 path) ---
    i39 = (n("Debt!I31") + n("Debt!I32") + n("Debt!I33") + n("Debt!I34")
           + n("Debt!I35") + n("Debt!I36") + n("Debt!I37") + n("Debt!I38"))

    i42 = 1800 + 1200         # 3000    (hard-coded formula in workbook)
    i44 = 84738.75 * 2        # 169477.5
    i45 = 21356.25 * 2        # 42712.5
    i49 = n("Debt!I41") + i42 + n("Debt!I43") + i44 + i45 + n("Debt!I46") + n("Debt!I47") + n("Debt!I48")

    i50 = round(i39 + i49)    # ROUND(..., 0)
    i7 = i50

    # --- target ---
    i8 = i6 + i7
    return i8
