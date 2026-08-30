def compute(inputs: dict):
    def n(key):
        """Coerce a cell value to a number the way Excel SUM/arithmetic does."""
        v = inputs.get(key)
        if v is None or v is True or v is False or isinstance(v, str):
            return 0.0
        return float(v)

    # C12 = SUM(C8:C11)
    c12 = n("CIP!C8") + n("CIP!C9") + n("CIP!C10") + n("CIP!C11")

    # C17 = SUM(C14:C16)
    c17 = n("CIP!C14") + n("CIP!C15") + n("CIP!C16")

    # C23 = SUM(C19:C22)
    c23 = n("CIP!C19") + n("CIP!C20") + n("CIP!C21") + n("CIP!C22")

    # C28 = C17 + C23 + C27
    c28 = c17 + c23 + n("CIP!C27")

    # C36 = SUM(C31:C35)
    c36 = (n("CIP!C31") + n("CIP!C32") + n("CIP!C33")
           + n("CIP!C34") + n("CIP!C35"))

    # C43 = SUM(C38:C42)
    c43 = (n("CIP!C38") + n("CIP!C39") + n("CIP!C40")
           + n("CIP!C41") + n("CIP!C42"))

    # C47 = SUM(C45:C46)
    c47 = n("CIP!C45") + n("CIP!C46")

    # C53 = SUM(C49:C52)
    c53 = n("CIP!C49") + n("CIP!C50") + n("CIP!C51") + n("CIP!C52")

    # C55 = C12 + C28 + C36 + C43 + C47 + C53
    c55 = c12 + c28 + c36 + c43 + c47 + c53

    # C67 = SUM(C57:C66)
    c67 = (n("CIP!C57") + n("CIP!C58") + n("CIP!C59") + n("CIP!C60")
           + n("CIP!C61") + n("CIP!C62") + n("CIP!C63") + n("CIP!C64")
           + n("CIP!C65") + n("CIP!C66"))

    # C68 = C67 - C55
    return c67 - c55
