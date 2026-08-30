def compute(inputs: dict):
    """
    Port of '6 - Operating Expenditures'!K38.

    Formula chain:
        H37 = SUM(H53:R53)
        H38 = SUM(H54:R54)
        J37 = I37 * H37
        J38 = I38 * H38
        K38 = (J38 / J37) - 1

    If J37 is zero, Excel returns #DIV/0!  — we return None.
    """
    S = "6 - Operating Expenditures!"

    def num(key):
        v = inputs.get(S + key)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    cols_53_54 = ["H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R"]

    h37 = sum(num(c + "53") for c in cols_53_54)
    h38 = sum(num(c + "54") for c in cols_53_54)

    i37 = num("I37")
    i38 = num("I38")

    j37 = i37 * h37
    j38 = i38 * h38

    if j37 == 0:
        return None  # #DIV/0!

    return (j38 / j37) - 1
