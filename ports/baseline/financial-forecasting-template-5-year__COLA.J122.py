def compute(inputs: dict):
    """
    Computes COLA!J122 = J93 + J101 + J113 + J120

    Full formula tree:
      J93  = J91 + J92
             J91 = PC!J456 = PC!J454 + PC!J455
             J92 = input (COLA!J92)
      J101 = J99 + J100
             J99  = PC!J498 = PC!J462 = SUM(PC!J458:J461)
             J100 = PC!J552 = PC!J516
      J113 = SUM(J107:J112)
             J107 = input (COLA!J107)
             J108 = PC!J189
             J109 = PC!J553 = PC!J521
             J110 = input (COLA!J110)  -- text/space in the workbook
             J111 = PC!J190
             J112 = PC!J554 = PC!J536 = SUM(PC!J528:J535)
      J120 = J118 + J119
             J118 = PC!J501 = PC!J494 = SUM(PC!J484:J493)
             J119 = PC!J555 = PC!J548 = SUM(PC!J538:J547)
    """

    def n(key):
        """Convert an input to a number the way Excel does for SUM/+.
        None (blank) -> 0, bool -> 1/0, numeric -> float, string -> 0 (SUM ignores text)."""
        v = inputs.get(key)
        if v is None:
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, (int, float)):
            return float(v)
        # strings: in SUM and + context, treated as 0
        if isinstance(v, str):
            try:
                return float(v)
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    # --- Position Control intermediates ---
    # PC!J456 = PC!J454 + PC!J455
    pc_j456 = n("Position Control!J454") + n("Position Control!J455")

    # PC!J462 = SUM(PC!J458:J461)
    pc_j462 = (n("Position Control!J458") + n("Position Control!J459")
               + n("Position Control!J460") + n("Position Control!J461"))

    # PC!J494 = SUM(PC!J484:J493)
    pc_j494 = sum(n(f"Position Control!J{r}") for r in range(484, 494))

    # PC!J536 = SUM(PC!J528:J535)
    pc_j536 = sum(n(f"Position Control!J{r}") for r in range(528, 536))

    # PC!J548 = SUM(PC!J538:J547)
    pc_j548 = sum(n(f"Position Control!J{r}") for r in range(538, 548))

    # --- COLA intermediates ---
    # J91 = PC!J456;  J92 = input
    j91 = pc_j456
    j92 = n("COLA!J92")
    j93 = j91 + j92

    # J99 = PC!J498 = PC!J462;  J100 = PC!J552 = PC!J516
    j99 = pc_j462
    j100 = n("Position Control!J516")
    j101 = j99 + j100

    # J107 = input;  J108 = PC!J189;  J109 = PC!J553 = PC!J521
    # J110 = input;  J111 = PC!J190;  J112 = PC!J554 = PC!J536
    j107 = n("COLA!J107")
    j108 = n("Position Control!J189")
    j109 = n("Position Control!J521")
    j110 = n("COLA!J110")
    j111 = n("Position Control!J190")
    j112 = pc_j536
    j113 = j107 + j108 + j109 + j110 + j111 + j112

    # J118 = PC!J501 = PC!J494;  J119 = PC!J555 = PC!J548
    j118 = pc_j494
    j119 = pc_j548
    j120 = j118 + j119

    # J122 = J93 + J101 + J113 + J120
    return j93 + j101 + j113 + j120
