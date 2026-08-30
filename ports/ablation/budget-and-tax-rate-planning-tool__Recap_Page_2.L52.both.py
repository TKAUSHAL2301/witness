def compute(inputs: dict):
    def num(v):
        if v is None or v == '':
            return 0
        if isinstance(v, bool):
            return int(v)
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    K27 = num(inputs.get("Recap Page 2!K27"))
    K28 = num(inputs.get("Recap Page 2!K28"))
    K32 = num(inputs.get("Recap Page 2!K32", 0))  # =ESTREC named range, treat as input
    K33 = num(inputs.get("Recap Page 2!K33"))
    K34 = num(inputs.get("Recap Page 2!K34"))
    K35 = num(inputs.get("Recap Page 2!K35"))
    K38 = num(inputs.get("Recap Page 2!K38"))
    K39 = num(inputs.get("Recap Page 2!K39"))
    K40 = num(inputs.get("Recap Page 2!K40", 0))  # =FREECASHTOT named range
    K41 = num(inputs.get("Recap Page 2!K41", 0))  # =OTHERAVAILTOT named range
    K45 = num(inputs.get("Recap Page 2!K45"))
    K46 = num(inputs.get("Recap Page 2!K46"))
    K47 = num(inputs.get("Recap Page 2!K47"))
    K48 = num(inputs.get("Recap Page 2!K48"))

    L29 = K27 + K28                          # =SUM(K27:K28)
    L36 = K32 + K33 + K34 + K35              # =SUM(K32:K35)
    L42 = K38 + K39 + K40 + K41              # =SUM(K38:K41)
    L49 = K45 + K46 + K47 + K48              # =SUM(K45:K48)
    L52 = L29 + L36 + L42 + L49              # =SUM(L29+L36+L42+L49)

    return L52