def compute(inputs: dict):
    """
    Port of Recap Page 2!L22 from budget-and-tax-rate-planning-tool.xlsx.

    L22 = SUM(L18:L21) + L4
    L18 = SUM(K7:K16)
    L4  = TOTAPPROP (Recap Page 4!D33) — not an input; constant 0.
    L19, L20, L21 are direct inputs.

    So: L22 = SUM(K7:K16) + L19 + L20 + L21
    """

    def n(key):
        """Coerce a cell value to a number the way Excel does."""
        v = inputs.get(key)
        if v is None or v is True or v is False:
            return 0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    k_sum = sum(n(f"Recap Page 2!K{r}") for r in range(7, 17))  # K7:K16

    l19 = n("Recap Page 2!L19")
    l20 = n("Recap Page 2!L20")
    l21 = n("Recap Page 2!L21")

    return k_sum + l19 + l20 + l21
