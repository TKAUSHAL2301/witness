def compute(inputs: dict):
    b13 = inputs.get("Amortization!B13")
    if b13 is None or b13 == '':
        b13 = 0
    try:
        b13 = float(b13)
    except (ValueError, TypeError):
        return "#VALUE!"
    return b13 + 35