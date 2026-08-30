def compute(inputs: dict):
    """
    Port of Financial Targets!F41 from the capital-planning-and-budgeting workbook.

    Formula chain:
        F16 = SUM(F12:F15)           -- total revenue offsets
        F18 = F9 - F16               -- net operating revenues
        G41 = K12                    -- budgetary reserve fund target %
        E41 = G41 / 2                -- minimum (half of target)
        F41 = E41 * F18              -- minimum reserve dollar amount
    """

    def n(cell):
        """Coerce a cell value to a number the way Excel does."""
        v = inputs.get(cell)
        if v is None or v is True or v is False:
            return 0
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0

    F12 = n("Financial Targets!F12")
    F13 = n("Financial Targets!F13")
    F14 = n("Financial Targets!F14")
    F15 = n("Financial Targets!F15")
    F9  = n("Financial Targets!F9")
    K12 = n("Financial Targets!K12")

    F16 = F12 + F13 + F14 + F15      # SUM(F12:F15)
    F18 = F9 - F16                    # Net Operating Revenues
    G41 = K12                         # target %
    E41 = G41 / 2                     # minimum %
    F41 = E41 * F18                   # dollar amount

    return F41
