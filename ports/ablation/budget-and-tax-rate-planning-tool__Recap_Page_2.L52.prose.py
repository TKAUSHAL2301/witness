def compute(inputs: dict):
    """Compute Recap Page 2!L52 = SUM(L29+L36+L42+L49)."""

    def val(key):
        """Get numeric value of a cell, treating None/blank/'' as 0 (Excel SUM semantics)."""
        v = inputs.get(key)
        if v is None or v == '':
            return 0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    # L29 = SUM(K27:K28)
    L29 = val("Recap Page 2!K27") + val("Recap Page 2!K28")

    # L36 = SUM(K32:K35)  where K32 = ESTREC (named range, may come as K32 input)
    L36 = (val("Recap Page 2!K32")
         + val("Recap Page 2!K33")
         + val("Recap Page 2!K34")
         + val("Recap Page 2!K35"))

    # L42 = SUM(K38:K41)  where K40 = FREECASHTOT, K41 = OTHERAVAILTOT
    L42 = (val("Recap Page 2!K38")
         + val("Recap Page 2!K39")
         + val("Recap Page 2!K40")
         + val("Recap Page 2!K41"))

    # L49 = SUM(K45:K48)
    L49 = (val("Recap Page 2!K45")
         + val("Recap Page 2!K46")
         + val("Recap Page 2!K47")
         + val("Recap Page 2!K48"))

    # L52 = SUM(L29+L36+L42+L49)
    return L29 + L36 + L42 + L49