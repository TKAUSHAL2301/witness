def compute(inputs: dict):
    def n(key):
        v = inputs.get(key)
        if v is None or v == '' or v is False:
            return 0.0
        if v is True:
            return 1.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    def nv(key):
        """For non-SUM arithmetic: None/''→0, but string→#VALUE!"""
        v = inputs.get(key)
        if v is None or v == '':
            return 0.0
        if v is True:
            return 1.0
        if v is False:
            return 0.0
        if isinstance(v, str):
            try:
                return float(v)
            except (ValueError, TypeError):
                return float('nan')
        return float(v)

    # R50 is a formula =295283+0, constant
    R50 = 295283.0

    # H34 = SUM(H50:R50)
    sum_50 = sum(n(f"6 - Operating Expenditures!{c}50") for c in "HIJKLMNOPQ") + R50

    # H35 = SUM(H51:R51)
    sum_51 = sum(n(f"6 - Operating Expenditures!{c}51") for c in "HIJKLMNOPQR")

    H34 = sum_50
    H35 = sum_51

    I34 = nv("6 - Operating Expenditures!I34")
    I35 = nv("6 - Operating Expenditures!I35")

    J34 = I34 * H34
    J35 = I35 * H35

    # K35 = (J35/J34) - 1
    if J34 == 0:
        return float('inf') if J35 != 0 else float('nan')  # #DIV/0!

    return (J35 / J34) - 1