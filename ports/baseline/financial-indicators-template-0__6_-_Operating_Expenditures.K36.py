def compute(inputs: dict):
    """
    Port of 6 - Operating Expenditures!K36.

    K36 = (J36 / J35) - 1
    J36 = I36 * H36
    J35 = I35 * H35
    H35 = SUM(H51:R51)
    H36 = SUM(H52:R52)
    """
    S = "6 - Operating Expenditures!"

    def val(ref):
        v = inputs.get(S + ref)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # H35 = SUM(H51:R51)
    row51_cols = ["H51", "I51", "J51", "K51", "L51", "M51", "N51", "O51", "P51", "Q51", "R51"]
    H35 = sum(val(c) for c in row51_cols)

    # H36 = SUM(H52:R52)
    row52_cols = ["H52", "I52", "J52", "K52", "L52", "M52", "N52", "O52", "P52", "Q52", "R52"]
    H36 = sum(val(c) for c in row52_cols)

    I35 = val("I35")
    I36 = val("I36")

    J35 = I35 * H35
    J36 = I36 * H36

    if J35 == 0:
        return "#DIV/0!"

    return (J36 / J35) - 1
