def compute(inputs: dict):
    def num(v):
        """Coerce a value to a number the way Excel SUM does."""
        if v is None:
            return 0
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s == '':
                return 0
            try:
                return float(s)
            except (ValueError, OverflowError):
                return 0
        return 0

    g = inputs.get

    # Position Control intermediate sums
    pc_J456 = num(g("Position Control!J454")) + num(g("Position Control!J455"))
    pc_J462 = (num(g("Position Control!J458")) + num(g("Position Control!J459"))
               + num(g("Position Control!J460")) + num(g("Position Control!J461")))
    pc_J467 = (num(g("Position Control!J464")) + num(g("Position Control!J465"))
               + num(g("Position Control!J466")))
    pc_J482 = sum(num(g(f"Position Control!J{r}")) for r in range(469, 482))
    pc_J494 = sum(num(g(f"Position Control!J{r}")) for r in range(484, 494))

    pc_J497 = pc_J456
    pc_J498 = pc_J462
    pc_J499 = pc_J467
    pc_J500 = pc_J482
    pc_J501 = pc_J494

    pc_J509 = num(g("Position Control!J507")) + num(g("Position Control!J508"))
    pc_J516 = num(g("Position Control!J516"))
    pc_J521 = num(g("Position Control!J521"))
    pc_J536 = sum(num(g(f"Position Control!J{r}")) for r in range(528, 536))
    pc_J548 = sum(num(g(f"Position Control!J{r}")) for r in range(538, 548))

    pc_J551 = pc_J509
    pc_J552 = pc_J516
    pc_J553 = pc_J521
    pc_J554 = pc_J536
    pc_J555 = pc_J548

    # COLA calculations
    J91 = pc_J497
    J92 = pc_J551
    J93 = J91 + J92

    J99 = pc_J498
    J100 = pc_J552
    J101 = J99 + J100

    J107 = num(g("COLA!J107"))
    J108 = pc_J499
    J109 = pc_J553
    J110 = num(g("COLA!J110"))
    J111 = pc_J500
    J112 = pc_J554
    J113 = J107 + J108 + J109 + J110 + J111 + J112

    J118 = pc_J501
    J119 = pc_J555
    J120 = J118 + J119

    J122 = J93 + J101 + J113 + J120
    return J122