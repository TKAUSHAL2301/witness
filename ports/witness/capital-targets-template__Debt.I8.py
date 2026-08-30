import math


def _num(v):
    """Convert a value to a number the way Excel does for SUM/arithmetic."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    return 0


def _excel_round(value, digits=0):
    """Excel ROUND: half away from zero, not banker's rounding."""
    if digits == 0:
        if value >= 0:
            return math.floor(value + 0.5)
        else:
            return math.ceil(value - 0.5)
    factor = 10 ** digits
    if value >= 0:
        return math.floor(value * factor + 0.5) / factor
    else:
        return math.ceil(value * factor - 0.5) / factor


def compute(inputs: dict):
    g = lambda k: _num(inputs.get(k))

    # Constants baked into formulas
    I20 = 4250 * 2
    I21 = 3455 * 2
    I42 = 1800 + 1200
    I44 = 84738.75 * 2
    I45 = 21356.25 * 2

    # Block 1: General Obligation
    I17 = sum(g(f"Debt!I{r}") for r in range(11, 17))
    I25 = g("Debt!I19") + I20 + I21 + g("Debt!I22") + g("Debt!I23") + g("Debt!I24")
    I26 = _excel_round(I17 + I25, 0)

    # Block 2: Revenue
    I39 = sum(g(f"Debt!I{r}") for r in range(31, 39))
    I49 = g("Debt!I41") + I42 + g("Debt!I43") + I44 + I45 + g("Debt!I46") + g("Debt!I47") + g("Debt!I48")
    I50 = _excel_round(I39 + I49, 0)

    I6 = I26
    I7 = I50
    I8 = I6 + I7

    return I8