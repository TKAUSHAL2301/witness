def compute(inputs: dict):
    def val(key):
        v = inputs.get(key)
        if v is None or v == '' or v == '':
            return 0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    G7, G8, G9 = val("CPF!G7"), val("CPF!G8"), val("CPF!G9")
    G16, G17, G18 = val("CPF!G16"), val("CPF!G17"), val("CPF!G18")
    H7, H8, H9 = val("CPF!H7"), val("CPF!H8"), val("CPF!H9")
    H16, H17, H18 = val("CPF!H16"), val("CPF!H17"), val("CPF!H18")
    I7, I8, I9 = val("CPF!I7"), val("CPF!I8"), val("CPF!I9")
    I16, I17, I18 = val("CPF!I16"), val("CPF!I17"), val("CPF!I18")
    J16, J17, J18 = val("CPF!J16"), val("CPF!J17"), val("CPF!J18")
    R7, R8, R9 = val("CPF!R7"), val("CPF!R8"), val("CPF!R9")

    G10 = G7 + G8 + G9
    G19 = G16 + G17 + G18
    G20 = 0 if G19 == 0 else G19 - G10

    H10 = H7 + H8 + H9
    H19 = H16 + H17 + H18
    H20 = 0 if H19 == 0 else H19 - H10

    I10 = I7 + I8 + I9
    I19 = I16 + I17 + I18
    I20 = 0 if I19 == 0 else I19 - I10

    J7 = round(I7 + I7 * R7)
    J8 = round(I8 + I8 * R8)
    J9 = round(I9 + I9 * R9)
    J10 = J7 + J8 + J9
    J19 = J16 + J17 + J18
    J20 = 0 if J19 == 0 else J19 - J10

    # Q20 = IFERROR(AVERAGE((H20-G20)/G20, (I20-H20)/H20, (J20-I20)/I20), "")
    terms = []
    pairs = [(H20, G20), (I20, H20), (J20, I20)]
    try:
        for num_next, num_prev in pairs:
            if num_prev == 0:
                # division by zero in Excel propagates #DIV/0! into AVERAGE,
                # which makes AVERAGE return #DIV/0!, caught by IFERROR
                return ""
            terms.append((num_next - num_prev) / num_prev)
        return sum(terms) / len(terms)
    except Exception:
        return ""