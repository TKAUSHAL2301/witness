def compute(inputs: dict):
    def num(v):
        if v is None or v == '':
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    cols = 'HIJKLMNOPQR'

    h38 = sum(num(inputs.get(f"6 - Operating Expenditures!{c}54")) for c in cols)
    h39 = sum(num(inputs.get(f"6 - Operating Expenditures!{c}55")) for c in cols)

    i38 = num(inputs.get("6 - Operating Expenditures!I38"))
    i39 = num(inputs.get("6 - Operating Expenditures!I39"))

    j38 = i38 * h38
    j39 = i39 * h39

    if j38 == 0:
        return float('inf') if j39 >= 0 else float('-inf')

    return (j39 / j38) - 1