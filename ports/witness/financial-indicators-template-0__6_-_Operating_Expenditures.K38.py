def compute(inputs: dict):
    def num(v):
        if v is None or v == '':
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    cols = 'HIJKLMNOPQR'

    h37 = sum(num(inputs.get(f"6 - Operating Expenditures!{c}53")) for c in cols)
    h38 = sum(num(inputs.get(f"6 - Operating Expenditures!{c}54")) for c in cols)

    i37 = num(inputs.get("6 - Operating Expenditures!I37"))
    i38 = num(inputs.get("6 - Operating Expenditures!I38"))

    j37 = i37 * h37
    j38 = i38 * h38

    if j37 == 0:
        return float('inf') if j38 >= 0 else float('-inf')  # #DIV/0!

    return (j38 / j37) - 1