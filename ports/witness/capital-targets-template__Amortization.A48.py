def compute(inputs: dict):
    val = inputs.get("Amortization!A22")
    if val is None:
        val = 0
    try:
        val = float(val)
    except (ValueError, TypeError):
        return val  # Excel would propagate #VALUE! but we return as-is
    return val + 26