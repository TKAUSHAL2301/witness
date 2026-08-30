def compute(inputs: dict):
    """
    Port of 6 - Operating Expenditures!K39

    K39 = (J39 / J38) - 1
    J39 = I39 * H39
    J38 = I38 * H38
    H38 = SUM(H54:R54)
    H39 = SUM(H55:R55)
    """
    S = "6 - Operating Expenditures!"

    def num(key):
        v = inputs.get(S + key)
        if v is None:
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # H38 = SUM(H54:R54)  — columns H through R, row 54
    row54_cols = ["H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R"]
    h38 = sum(num(c + "54") for c in row54_cols)

    # H39 = SUM(H55:R55)  — columns H through R, row 55
    h39 = sum(num(c + "55") for c in row54_cols)

    # J38 = I38 * H38
    i38 = num("I38")
    j38 = i38 * h38

    # J39 = I39 * H39
    i39 = num("I39")
    j39 = i39 * h39

    # K39 = (J39 / J38) - 1
    if j38 == 0:
        # Excel returns #DIV/0! when dividing by zero
        return float('inf')  # represent DIV/0 as inf

    return (j39 / j38) - 1.0
