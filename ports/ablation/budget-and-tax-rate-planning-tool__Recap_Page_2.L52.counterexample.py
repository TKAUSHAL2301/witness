def _num(v):
    """Convert a value to a number the way Excel does for SUM."""
    if v is None or v == '':
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0


def compute(inputs: dict):
    g = lambda k: _num(inputs.get(k))

    K27 = g("Recap Page 2!K27")
    K28 = g("Recap Page 2!K28")

    # K32 = ESTREC (named range, treated as input; not in inputs so 0)
    K32 = 0
    K33 = g("Recap Page 2!K33")
    K34 = g("Recap Page 2!K34")
    K35 = g("Recap Page 2!K35")

    K38 = g("Recap Page 2!K38")
    K39 = g("Recap Page 2!K39")
    # K40 = FREECASHTOT (named range, not in inputs so 0)
    K40 = 0
    # K41 = OTHERAVAILTOT (named range, not in inputs so 0)
    K41 = 0

    K45 = g("Recap Page 2!K45")
    K46 = g("Recap Page 2!K46")
    K47 = g("Recap Page 2!K47")
    K48 = g("Recap Page 2!K48")

    # L29 = SUM(K27:K28)
    L29 = K27 + K28

    # L36 = SUM(K32:K35)
    L36 = K32 + K33 + K34 + K35

    # L42 = SUM(K38:K41)
    L42 = K38 + K39 + K40 + K41

    # L49 = SUM(K45:K48)
    L49 = K45 + K46 + K47 + K48

    # L52 = SUM(L29+L36+L42+L49)
    L52 = L29 + L36 + L42 + L49

    return L52