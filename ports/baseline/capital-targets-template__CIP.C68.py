def compute(inputs: dict):
    """Port of CIP!C68 from capital-targets-template.xlsx.

    C68 = C67 - C55
    C67 = SUM(C57:C66)                          (sources of funds)
    C55 = C12 + C28 + C36 + C43 + C47 + C53     (uses of funds)

    Intermediate subtotals:
        C12 = SUM(C8:C11)
        C28 = C17 + C23 + C27
        C17 = SUM(C14:C16)
        C23 = SUM(C19:C22)
        C36 = SUM(C31:C35)
        C43 = SUM(C38:C42)
        C47 = SUM(C45:C46)
        C53 = SUM(C49:C52)
    """

    def n(cell):
        """Coerce a cell value to a number the way Excel does."""
        v = inputs.get(cell)
        if v is None or v == "":
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # --- uses of funds ---
    c12 = n("CIP!C8") + n("CIP!C9") + n("CIP!C10") + n("CIP!C11")

    c17 = n("CIP!C14") + n("CIP!C15") + n("CIP!C16")
    c23 = n("CIP!C19") + n("CIP!C20") + n("CIP!C21") + n("CIP!C22")
    c28 = c17 + c23 + n("CIP!C27")

    c36 = (n("CIP!C31") + n("CIP!C32") + n("CIP!C33")
           + n("CIP!C34") + n("CIP!C35"))

    c43 = (n("CIP!C38") + n("CIP!C39") + n("CIP!C40")
           + n("CIP!C41") + n("CIP!C42"))

    c47 = n("CIP!C45") + n("CIP!C46")

    c53 = n("CIP!C49") + n("CIP!C50") + n("CIP!C51") + n("CIP!C52")

    c55 = c12 + c28 + c36 + c43 + c47 + c53

    # --- sources of funds ---
    c67 = (n("CIP!C57") + n("CIP!C58") + n("CIP!C59") + n("CIP!C60")
           + n("CIP!C61") + n("CIP!C62") + n("CIP!C63") + n("CIP!C64")
           + n("CIP!C65") + n("CIP!C66"))

    # --- target cell ---
    c68 = c67 - c55
    return c68
