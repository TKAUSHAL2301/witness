def compute(inputs: dict):
    """
    Port of CPF!Q20 from financial-forecasting-template-5-year.xlsx.

    Q20 = IFERROR(AVERAGE((H20-G20)/G20, (I20-H20)/H20, (J20-I20)/I20), "")

    Where X20 = IF(X19=0, 0, X19 - X10)
          X19 = SUM(X16:X18)   (actual revenues)
          X10 = SUM(X7:X9)     (budget revenues)

    For columns G, H, I: X7/X8/X9 are direct inputs.
    For column J: J7 = ROUND(I7 + I7*R7, 0), similarly J8, J9.
    """

    def val(key):
        v = inputs.get(key)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    def excel_round(x):
        # Excel ROUND(x, 0): round half away from zero
        if x >= 0:
            return int(x + 0.5)
        else:
            return -int(-x + 0.5)

    # Budget totals (X10 = SUM(X7:X9))
    g10 = val("CPF!G7") + val("CPF!G8") + val("CPF!G9")
    h10 = val("CPF!H7") + val("CPF!H8") + val("CPF!H9")
    i10 = val("CPF!I7") + val("CPF!I8") + val("CPF!I9")

    # J7 = ROUND(I7 + I7*R7, 0), etc.
    j7 = excel_round(val("CPF!I7") + val("CPF!I7") * val("CPF!R7"))
    j8 = excel_round(val("CPF!I8") + val("CPF!I8") * val("CPF!R8"))
    j9 = excel_round(val("CPF!I9") + val("CPF!I9") * val("CPF!R9"))
    j10 = j7 + j8 + j9

    # Actual totals (X19 = SUM(X16:X18))
    g19 = val("CPF!G16") + val("CPF!G17") + val("CPF!G18")
    h19 = val("CPF!H16") + val("CPF!H17") + val("CPF!H18")
    i19 = val("CPF!I16") + val("CPF!I17") + val("CPF!I18")
    j19 = val("CPF!J16") + val("CPF!J17") + val("CPF!J18")

    # X20 = IF(X19=0, 0, X19 - X10)
    def diff(actual_sum, budget_sum):
        if actual_sum == 0:
            return 0.0
        return actual_sum - budget_sum

    g20 = diff(g19, g10)
    h20 = diff(h19, h10)
    i20 = diff(i19, i10)
    j20 = diff(j19, j10)

    # Q20 = IFERROR(AVERAGE((H20-G20)/G20, (I20-H20)/H20, (J20-I20)/I20), "")
    try:
        if g20 == 0 or h20 == 0 or i20 == 0:
            return ""
        term1 = (h20 - g20) / g20
        term2 = (i20 - h20) / h20
        term3 = (j20 - i20) / i20
        return (term1 + term2 + term3) / 3.0
    except (ZeroDivisionError, ArithmeticError):
        return ""
