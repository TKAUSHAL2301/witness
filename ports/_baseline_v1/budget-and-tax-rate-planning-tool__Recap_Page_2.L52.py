def compute(inputs: dict):
    def num(key):
        v = inputs.get(key)
        if v is None:
            return 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # L29 = SUM(K27:K28)
    l29 = num("Recap Page 2!K27") + num("Recap Page 2!K28")

    # L36 = SUM(K32:K35); K32 is =ESTREC (cross-sheet, not an input, constant 0)
    l36 = num("Recap Page 2!K33") + num("Recap Page 2!K34") + num("Recap Page 2!K35")

    # L42 = SUM(K38:K41); K40=FREECASHTOT, K41=OTHERAVAILTOT (cross-sheet, constant 0)
    l42 = num("Recap Page 2!K38") + num("Recap Page 2!K39")

    # L49 = SUM(K45:K48)
    l49 = (num("Recap Page 2!K45") + num("Recap Page 2!K46")
         + num("Recap Page 2!K47") + num("Recap Page 2!K48"))

    # L52 = SUM(L29 + L36 + L42 + L49)
    return l29 + l36 + l42 + l49