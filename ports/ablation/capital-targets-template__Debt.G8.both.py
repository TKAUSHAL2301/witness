import math

def compute(inputs: dict):
    def num(v):
        if v is None or v == '':
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    def excel_round(x, d=0):
        if d == 0:
            return float(math.floor(abs(x) + 0.5)) * (1 if x >= 0 else -1) if x != 0 else 0.0
        factor = 10 ** d
        return float(math.floor(abs(x) * factor + 0.5)) / factor * (1 if x >= 0 else -1) if x != 0 else 0.0

    g = lambda ref: num(inputs.get(ref))

    G17 = g("Debt!G11") + g("Debt!G12") + g("Debt!G13") + g("Debt!G14") + g("Debt!G15") + g("Debt!G16")

    G20 = 6500 * 2
    G21 = 4305 * 2

    G25 = g("Debt!G19") + G20 + G21 + g("Debt!G22") + g("Debt!G23") + g("Debt!G24")

    G26 = excel_round(G17 + G25, 0)

    G39 = (g("Debt!G31") + g("Debt!G32") + g("Debt!G33") + g("Debt!G34")
         + g("Debt!G35") + g("Debt!G36") + g("Debt!G37") + g("Debt!G38"))

    G41 = 4843.75 + 3293.75
    G42 = 3075 + 2400
    G44 = 101638.75 * 2
    G45 = 25731.25 * 2
    G46 = 4500 * 2

    G49 = G41 + G42 + g("Debt!G43") + G44 + G45 + G46 + g("Debt!G47") + g("Debt!G48")

    G50 = excel_round(G39 + G49, 0)

    G6 = G26
    G7 = G50

    return G6 + G7