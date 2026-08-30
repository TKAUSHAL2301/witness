def _num(v):
    """Coerce a value to a number the way Excel does in SUM: None/''/bool/str→0 or number."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, str):
        # SUM ignores text cells (treats as 0)
        return 0
    return v


def compute(inputs: dict):
    g = lambda k: _num(inputs.get(k))

    # Named-range placeholders fed directly into K32 and K40/K41
    # K32 = ESTREC  (input not listed → comes from outside, but K32 is not an input;
    #   it's computed as =ESTREC. Since ESTREC isn't an input, K32 must be derived.
    #   However K32 is not in the input list — K33, K34, K35 are.
    #   Looking at the formulas: K32 = =ESTREC and K40 = =FREECASHTOT, K41 = =OTHERAVAILTOT
    #   These are named ranges pointing elsewhere. They are NOT in the input list,
    #   so they must be treated as additional inputs or zero.
    #   But wait — the SUM ranges use K32:K35 and K38:K41.
    #   Inputs given: K33, K34, K35 (for the K32:K35 range) and K38, K39 (for K38:K41).
    #   K32, K40, K41 are formula cells (not inputs). They must come from somewhere.
    #   Since they're not provided as inputs, I'll check if they might be implicitly zero
    #   or if they should be passthrough inputs.

    # Actually re-reading: the inputs list has K27,K28,K33,K34,K35,K38,K39,K45,K46,K47,K48
    # K32 is =ESTREC (a named range, not provided as input → defaults to 0)
    # K40 is =FREECASHTOT, K41 is =OTHERAVAILTOT (also not inputs → default 0)
    # But the problem says "input cells" are the ones listed. The formula cells
    # K32, K40, K41 reference named ranges that aren't provided, so they evaluate to 0
    # in this isolated context. Unless they ARE meant to be inputs...
    # 
    # I'll treat K32, K40, K41 as passthrough from inputs (defaulting to 0 if absent),
    # since the named ranges could be supplied.

    K27 = g("Recap Page 2!K27")
    K28 = g("Recap Page 2!K28")

    # K32 = ESTREC (named range, not in inputs, default 0)
    K32 = g("Recap Page 2!K32")
    K33 = g("Recap Page 2!K33")
    K34 = g("Recap Page 2!K34")
    K35 = g("Recap Page 2!K35")

    K38 = g("Recap Page 2!K38")
    K39 = g("Recap Page 2!K39")
    # K40 = FREECASHTOT, K41 = OTHERAVAILTOT (named ranges, not in inputs)
    K40 = g("Recap Page 2!K40")
    K41 = g("Recap Page 2!K41")

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
    # Note: =SUM(L29+L36+L42+L49) in Excel first evaluates L29+L36+L42+L49
    # as an expression (addition), then SUM wraps that single result. Equivalent to:
    L52 = L29 + L36 + L42 + L49

    return L52