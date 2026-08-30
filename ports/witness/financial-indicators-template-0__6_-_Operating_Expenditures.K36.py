def compute(inputs: dict):
    def num(v):
        if v is None or v == '':
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    def sum_range(row, cols):
        total = 0.0
        for c in cols:
            v = inputs.get(f"6 - Operating Expenditures!{c}{row}")
            if v is None or v == '' or isinstance(v, str):
                continue
            total += num(v)
        return total

    cols = ['H','I','J','K','L','M','N','O','P','Q','R']

    H35 = sum_range(51, cols)
    H36 = sum_range(52, cols)

    I35 = num(inputs.get("6 - Operating Expenditures!I35"))
    I36 = num(inputs.get("6 - Operating Expenditures!I36"))

    J35 = I35 * H35
    J36 = I36 * H36

    if J35 == 0:
        return float('inf')  # #DIV/0!

    return (J36 / J35) - 1