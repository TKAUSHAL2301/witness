import math

def compute(inputs: dict):
    def n(key):
        v = inputs.get(key)
        if v is None or v == '' or isinstance(v, str):
            return 0
        if isinstance(v, bool):
            return int(v)
        return v

    def xl_round(x):
        if x >= 0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)

    G17 = sum(n(f"Debt!G{r}") for r in range(11, 17))
    G20 = 6500 * 2
    G21 = 4305 * 2
    G25 = sum([n("Debt!G19"), G20, G21, n("Debt!G22"), n("Debt!G23"), n("Debt!G24")])
    G26 = xl_round(G17 + G25)

    G39 = sum(n(f"Debt!G{r}") for r in range(31, 39))
    G41 = 4843.75 + 3293.75
    G42 = 3075 + 2400
    G44 = 101638.75 * 2
    G45 = 25731.25 * 2
    G46 = 4500 * 2
    G49 = sum([G41, G42, n("Debt!G43"), G44, G45, G46, n("Debt!G47"), n("Debt!G48")])
    G50 = xl_round(G39 + G49)

    G6 = G26
    G7 = G50
    G8 = G6 + G7
    return G8