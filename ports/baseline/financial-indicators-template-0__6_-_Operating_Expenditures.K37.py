def compute(inputs: dict):
    """
    Computes cell K37 on sheet '6 - Operating Expenditures'.

    K37 = (J37 / J36) - 1

    Where:
        J37 = I37 * H37
        J36 = I36 * H36
        H37 = SUM(H53:R53)
        H36 = SUM(H52:R52)
    """
    S = "6 - Operating Expenditures!"

    def val(cell_ref):
        v = inputs.get(cell_ref)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # H36 = SUM(H52:R52)
    cols_52 = [val(S + c + "52") for c in "HIJKLMNOPQR"]
    h36 = sum(cols_52)

    # H37 = SUM(H53:R53)
    cols_53 = [val(S + c + "53") for c in "HIJKLMNOPQR"]
    h37 = sum(cols_53)

    i36 = val(S + "I36")
    i37 = val(S + "I37")

    j36 = i36 * h36
    j37 = i37 * h37

    # K37 = (J37 / J36) - 1   — Excel returns #DIV/0! when J36 is 0
    if j36 == 0:
        return float("inf") if j37 != 0 else None  # #DIV/0!
    return (j37 / j36) - 1
