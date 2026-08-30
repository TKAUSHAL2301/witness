def compute(inputs: dict):
    """
    Port of 6 - Operating Expenditures!K35.

    Formula chain:
        H34 = SUM(H50:R50)
        H35 = SUM(H51:R51)
        J34 = I34 * H34
        J35 = I35 * H35
        K35 = (J35 / J34) - 1
    """
    S = "6 - Operating Expenditures!"

    def val(ref):
        v = inputs.get(S + ref)
        if v is None:
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, str):
            try:
                return float(v)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    # H34 = SUM(H50:R50)  — columns H through R = H,I,J,K,L,M,N,O,P,Q,R
    cols = ["H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R"]
    h34 = sum(val(c + "50") for c in cols)

    # H35 = SUM(H51:R51)
    h35 = sum(val(c + "51") for c in cols)

    # I34, I35 are direct inputs
    i34 = val("I34")
    i35 = val("I35")

    # J34 = I34 * H34
    j34 = i34 * h34

    # J35 = I35 * H35
    j35 = i35 * h35

    # K35 = (J35 / J34) - 1
    if j34 == 0:
        # Excel would return #DIV/0!; return None or float('inf') equivalent
        return float('inf') if j35 != 0 else float('-inf')
    return (j35 / j34) - 1
