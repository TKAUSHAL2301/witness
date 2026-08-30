def compute(inputs: dict):
    def num(v):
        if v is None or v == '':
            return 0
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, (int, float)):
            return v
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    c8 = num(inputs.get("Impact!C8"))
    c9 = num(inputs.get("Impact!C9"))
    c10 = num(inputs.get("Impact!C10"))
    c11 = num(inputs.get("Impact!C11"))
    c12 = num(inputs.get("Impact!C12"))
    c13 = num(inputs.get("Impact!C13"))
    c14 = num(inputs.get("Impact!C14"))
    c15 = num(inputs.get("Impact!C15"))
    c16 = num(inputs.get("Impact!C16"))
    c17 = num(inputs.get("Impact!C17"))

    c18 = c8 + c9 + c10 + c11 + c12 + c13 + c14 + c15 + c16 + c17

    c22 = num(inputs.get("Impact!C22"))
    c23 = num(inputs.get("Impact!C23"))
    c24 = num(inputs.get("Impact!C24"))
    c25 = num(inputs.get("Impact!C25"))
    c26 = num(inputs.get("Impact!C26"))
    c27 = num(inputs.get("Impact!C27"))
    c28 = num(inputs.get("Impact!C28"))

    c29 = c22 + c23 + c24 + c25 + c26 + c27 + c28

    c31 = c18 + c29

    c4 = num(inputs.get("Impact!C4"))

    c33 = c4 + c31
    return c33