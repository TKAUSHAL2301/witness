def compute(inputs: dict):
    """
    Port of COLA!J122 (Grand Total for Enterprise Funds COLA).

    COLA!J122 = J93 + J101 + J113 + J120

    Where:
      J93  = Total Elected Officials   = SUM(J91:J92)
      J101 = Total Exempt/Comp Plan    = SUM(J99:J100)
      J113 = Total CBA                 = SUM(J107:J112)
      J120 = Total Other Compensation  = SUM(J118:J119)

    Each of those pulls from Position Control summary rows, which in turn
    are SUM ranges over the input cells.
    """

    def n(key):
        """Coerce an input to a number the way Excel does.
        None (blank) -> 0, bool -> 1/0, str -> 0 if non-numeric, number -> float.
        """
        v = inputs.get(key)
        if v is None:
            return 0.0
        if isinstance(v, bool):
            return 1.0 if v else 0.0
        if isinstance(v, (int, float)):
            return float(v)
        # String: try to parse as number, else treat as 0 (Excel SUM ignores text)
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return 0.0
            try:
                return float(s)
            except ValueError:
                return 0.0
        return 0.0

    # --- Position Control intermediate sums (Wastewater) ---

    # PC!J456 = SUM(J454:J455)  -> Elected-Stipends (Wastewater)
    pc_j456 = n("Position Control!J454") + n("Position Control!J455")

    # PC!J462 = SUM(J458:J461)  -> Exempt (Wastewater)
    pc_j462 = (n("Position Control!J458") + n("Position Control!J459")
               + n("Position Control!J460") + n("Position Control!J461"))

    # PC!J467 = SUM(J464:J466)  -> Clerical (Wastewater)
    pc_j467 = (n("Position Control!J464") + n("Position Control!J465")
               + n("Position Control!J466"))

    # PC!J482 = SUM(J469:J481)  -> Laborers (Wastewater)
    pc_j482 = sum(n(f"Position Control!J{r}") for r in range(469, 482))

    # PC!J494 = SUM(J484:J493)  -> Additional (Wastewater)
    pc_j494 = sum(n(f"Position Control!J{r}") for r in range(484, 494))

    # --- Position Control intermediate sums (Water) ---

    # PC!J509 = SUM(J507:J508)  -> Elected-Stipends (Water)
    pc_j509 = n("Position Control!J507") + n("Position Control!J508")

    # PC!J516 is a direct input  -> Exempt (Water)
    pc_j516 = n("Position Control!J516")

    # PC!J521 is a direct input  -> Clerical (Water)
    pc_j521 = n("Position Control!J521")

    # PC!J536 = SUM(J528:J535)  -> Laborers (Water)
    pc_j536 = sum(n(f"Position Control!J{r}") for r in range(528, 536))

    # PC!J548 = SUM(J538:J547)  -> Additional (Water)
    pc_j548 = sum(n(f"Position Control!J{r}") for r in range(538, 548))

    # --- Position Control summary rows ---
    # PC!J497 = J456 (Wastewater Elected Stipends)
    # PC!J498 = J462 (Wastewater Exempt)
    # PC!J499 = J467 (Wastewater Clerical)
    # PC!J500 = J482 (Wastewater Laborers)
    # PC!J501 = J494 (Wastewater Additional)
    # PC!J551 = J509 (Water Elected Stipends)
    # PC!J552 = J516 (Water Exempt)
    # PC!J553 = J521 (Water Clerical)
    # PC!J554 = J536 (Water Laborers)
    # PC!J555 = J548 (Water Additional)

    # --- COLA sheet rows ---

    # J91 = PC!J497,  J92 = PC!J551
    cola_j91 = pc_j456
    cola_j92 = pc_j509

    # J93 = SUM(J91:J92)  -> Total Elected Officials
    cola_j93 = cola_j91 + cola_j92

    # J99 = PC!J498,  J100 = PC!J552
    cola_j99 = pc_j462
    cola_j100 = pc_j516

    # J101 = SUM(J99:J100)  -> Total Exempt/Compensation Plan
    cola_j101 = cola_j99 + cola_j100

    # J107 = input (COLA!J107), J108 = PC!J499, J109 = PC!J553
    # J110 = input (COLA!J110), J111 = PC!J500, J112 = PC!J554
    cola_j107 = n("COLA!J107")
    cola_j108 = pc_j467
    cola_j109 = pc_j521
    cola_j110 = n("COLA!J110")
    cola_j111 = pc_j482
    cola_j112 = pc_j536

    # J113 = SUM(J107:J112)  -> Total CBA
    cola_j113 = cola_j107 + cola_j108 + cola_j109 + cola_j110 + cola_j111 + cola_j112

    # J118 = PC!J501,  J119 = PC!J555
    cola_j118 = pc_j494
    cola_j119 = pc_j548

    # J120 = SUM(J118:J119)  -> Total Other Compensation
    cola_j120 = cola_j118 + cola_j119

    # J122 = J93 + J101 + J113 + J120  -> Grand Total
    return cola_j93 + cola_j101 + cola_j113 + cola_j120
