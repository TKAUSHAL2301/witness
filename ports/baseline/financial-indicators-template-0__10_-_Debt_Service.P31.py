def compute(inputs: dict):
    """
    Port of target cell: 10 - Debt Service!P31

    Formula chain:
        J31 = '6 - Operating Expenditures'!I51 - '10 - Debt Service'!K31
        L31 = K31 + J31   (= '6 - Operating Expenditures'!I51)
        O33 = I33 - SUM(J33:N33)   (on '1 - Net Operating Revenues')
        M31 = O33
        P31 = L31 / M31
    """

    def n(key):
        """Convert cell value to number the way Excel does: None->0, bool->int, str->0."""
        v = inputs.get(key)
        if v is None:
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0

    # J31 = OE!I51 - DS!K31
    oe_i51 = n("6 - Operating Expenditures!I51")
    ds_k31 = n("10 - Debt Service!K31")
    j31 = oe_i51 - ds_k31

    # L31 = K31 + J31
    l31 = ds_k31 + j31  # simplifies to oe_i51

    # O33 on '1 - Net Operating Revenues' = I33 - SUM(J33:N33)
    i33 = n("1 - Net Operating Revenues!I33")
    j33 = n("1 - Net Operating Revenues!J33")
    k33 = n("1 - Net Operating Revenues!K33")
    l33 = n("1 - Net Operating Revenues!L33")
    m33 = n("1 - Net Operating Revenues!M33")
    n33 = n("1 - Net Operating Revenues!N33")
    m31 = i33 - (j33 + k33 + l33 + m33 + n33)

    # P31 = L31 / M31  — Excel returns #DIV/0! when M31 is 0
    if m31 == 0:
        return None
    return l31 / m31
