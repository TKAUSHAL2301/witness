def compute(inputs: dict):
    def num(v):
        if v is None or v == '':
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    cols = 'HIJKLMNOPQR'

    h36 = sum(num(inputs.get(f"6 - Operating Expenditures!{c}52")) for c in cols)
    h37 = sum(num(inputs.get(f"6 - Operating Expenditures!{c}53")) for c in cols)

    i36 = num(inputs.get("6 - Operating Expenditures!I36"))
    i37 = num(inputs.get("6 - Operating Expenditures!I37"))

    j36 = i36 * h36
    j37 = i37 * h37

    if j36 == 0:
        return "#DIV/0!"

    return (j37 / j36) - 1