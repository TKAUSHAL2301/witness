def _num(v):
    """Coerce a value to a number the way Excel does in SUM (blanks and strings are 0)."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    # strings are ignored by SUM
    return 0


def compute(inputs: dict):
    g = lambda k: inputs.get(k)

    # L29 = SUM(K27:K28)
    L29 = _num(g("Recap Page 2!K27")) + _num(g("Recap Page 2!K28"))

    # K32 = ESTREC (named range, an input we don't have — not in inputs, so 0)
    # K40 = FREECASHTOT (same)
    # K41 = OTHERAVAILTOT (same)
    # These are not listed as inputs, so they resolve to 0.
    K32 = 0
    K40 = 0
    K41 = 0

    # L36 = SUM(K32:K35)
    L36 = (_num(K32)
           + _num(g("Recap Page 2!K33"))
           + _num(g("Recap Page 2!K34"))
           + _num(g("Recap Page 2!K35")))

    # L42 = SUM(K38:K41)
    L42 = (_num(g("Recap Page 2!K38"))
           + _num(g("Recap Page 2!K39"))
           + _num(K40)
           + _num(K41))

    # L49 = SUM(K45:K48)
    L49 = (_num(g("Recap Page 2!K45"))
           + _num(g("Recap Page 2!K46"))
           + _num(g("Recap Page 2!K47"))
           + _num(g("Recap Page 2!K48")))

    # L52 = SUM(L29+L36+L42+L49)  — note: SUM of a single expression = just the sum
    L52 = L29 + L36 + L42 + L49

    return L52