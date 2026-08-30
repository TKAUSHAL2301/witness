def compute(inputs: dict):
    def num(v):
        if v is None:
            return 0
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, str):
            s = v.strip()
            if s == '':
                return 0
            try:
                return float(s)
            except (ValueError, TypeError):
                return 0
        return 0

    def sum_nums(vals):
        total = 0
        for v in vals:
            if isinstance(v, str):
                s = v.strip()
                if s == '' or s == ' ':
                    continue
                try:
                    total += float(s)
                except (ValueError, TypeError):
                    continue
            elif v is None:
                continue
            elif isinstance(v, (int, float)):
                total += v
        return total

    g = inputs.get

    # Position Control intermediates
    pc_J456 = sum_nums([g("Position Control!J454"), g("Position Control!J455")])
    pc_J462 = sum_nums([g("Position Control!J458"), g("Position Control!J459"),
                        g("Position Control!J460"), g("Position Control!J461")])
    pc_J494 = sum_nums([g("Position Control!J484"), g("Position Control!J485"),
                        g("Position Control!J486"), g("Position Control!J487"),
                        g("Position Control!J488"), g("Position Control!J489"),
                        g("Position Control!J490"), g("Position Control!J491"),
                        g("Position Control!J492"), g("Position Control!J493")])
    pc_J498 = pc_J462
    pc_J501 = pc_J494
    pc_J516 = num(g("Position Control!J516"))
    pc_J521 = num(g("Position Control!J521"))
    pc_J536 = sum_nums([g("Position Control!J528"), g("Position Control!J529"),
                        g("Position Control!J530"), g("Position Control!J531"),
                        g("Position Control!J532"), g("Position Control!J533"),
                        g("Position Control!J534"), g("Position Control!J535")])
    pc_J548 = sum_nums([g("Position Control!J538"), g("Position Control!J539"),
                        g("Position Control!J540"), g("Position Control!J541"),
                        g("Position Control!J542"), g("Position Control!J543"),
                        g("Position Control!J544"), g("Position Control!J545"),
                        g("Position Control!J546"), g("Position Control!J547")])
    pc_J552 = pc_J516
    pc_J553 = pc_J521
    pc_J554 = pc_J536
    pc_J555 = pc_J548
    pc_J189 = num(g("Position Control!J189"))
    pc_J190 = num(g("Position Control!J190"))

    # COLA intermediates
    j91 = pc_J456
    j92 = num(g("COLA!J92"))
    j93 = j91 + j92

    j99 = pc_J498
    j100 = pc_J552
    j101 = j99 + j100

    j107 = num(g("COLA!J107"))
    j108 = pc_J189
    j109 = pc_J553
    j110 = g("COLA!J110")
    j111 = pc_J190
    j112 = pc_J554
    j113 = sum_nums([j107, j108, j109, j110, j111, j112])

    j118 = pc_J501
    j119 = pc_J555
    j120 = j118 + j119

    j122 = j93 + j101 + j113 + j120
    return j122