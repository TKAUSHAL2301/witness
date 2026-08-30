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

    I33 = num(inputs.get("1 - Net Operating Revenues!I33"))
    J33 = num(inputs.get("1 - Net Operating Revenues!J33"))
    K33 = num(inputs.get("1 - Net Operating Revenues!K33"))
    L33 = num(inputs.get("1 - Net Operating Revenues!L33"))
    M33 = num(inputs.get("1 - Net Operating Revenues!M33"))
    N33 = num(inputs.get("1 - Net Operating Revenues!N33"))
    K31 = num(inputs.get("10 - Debt Service!K31"))
    I51 = num(inputs.get("6 - Operating Expenditures!I51"))

    # 1 - Net Operating Revenues!O33 = I33 - SUM(J33:N33)
    O33 = I33 - (J33 + K33 + L33 + M33 + N33)

    # 10 - Debt Service!J31 = '6 - Operating Expenditures'!I51 - K31
    J31 = I51 - K31

    # 10 - Debt Service!L31 = K31 + J31
    L31 = K31 + J31

    # 10 - Debt Service!M31 = O33
    M31 = O33

    # 10 - Debt Service!P31 = L31 / M31
    if M31 == 0:
        # Excel #DIV/0!
        return float('inf')

    return L31 / M31