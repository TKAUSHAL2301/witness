def compute(inputs: dict):
    def num(key):
        v = inputs.get(key)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # R50 is not an input; it is a constant formula =295283+0
    R50 = 295283.0

    # H34 = SUM(H50:R50)
    row50_cols = ["H50", "I50", "J50", "K50", "L50", "M50", "N50", "O50", "P50", "Q50"]
    h34 = sum(num("6 - Operating Expenditures!" + c) for c in row50_cols) + R50

    # H35 = SUM(H51:R51)
    row51_cols = ["H51", "I51", "J51", "K51", "L51", "M51", "N51", "O51", "P51", "Q51", "R51"]
    h35 = sum(num("6 - Operating Expenditures!" + c) for c in row51_cols)

    i34 = num("6 - Operating Expenditures!I34")
    i35 = num("6 - Operating Expenditures!I35")

    # J34 = I34 * H34
    j34 = i34 * h34

    # J35 = I35 * H35
    j35 = i35 * h35

    # K35 = (J35 / J34) - 1
    if j34 == 0:
        return None
    return (j35 / j34) - 1