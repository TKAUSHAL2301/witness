def compute(inputs: dict):
    """Port of 'Recap Page 2'!L52 from budget-and-tax-rate-planning-tool.xlsx.

    L52 = SUM(L29 + L36 + L42 + L49)
      L29 = SUM(K27:K28)
      L36 = SUM(K32:K35)   -- K32 is a named-range formula (ESTREC), not an input; treated as 0
      L42 = SUM(K38:K41)   -- K40 (FREECASHTOT), K41 (OTHERAVAILTOT) are named-range formulas; treated as 0
      L49 = SUM(K45:K48)

    Net result: sum of the 11 input cells.
    """
    keys = [
        "Recap Page 2!K27",
        "Recap Page 2!K28",
        "Recap Page 2!K33",
        "Recap Page 2!K34",
        "Recap Page 2!K35",
        "Recap Page 2!K38",
        "Recap Page 2!K39",
        "Recap Page 2!K45",
        "Recap Page 2!K46",
        "Recap Page 2!K47",
        "Recap Page 2!K48",
    ]

    total = 0
    for key in keys:
        v = inputs.get(key)
        if v is None or isinstance(v, bool) or isinstance(v, str):
            # Excel SUM over a cell range ignores blanks, booleans, and text
            continue
        try:
            total += float(v)
        except (TypeError, ValueError):
            continue
    return total
