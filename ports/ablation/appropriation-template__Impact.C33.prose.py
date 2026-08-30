def compute(inputs: dict):
    def num(v):
        if v is None:
            return 0
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, (int, float)):
            return v
        if isinstance(v, str):
            if v == '':
                return 0
            try:
                return float(v)
            except (ValueError, TypeError):
                return 0
        return 0

    C8 = num(inputs.get("Impact!C8"))
    C9 = num(inputs.get("Impact!C9"))
    C10 = num(inputs.get("Impact!C10"))
    C11 = num(inputs.get("Impact!C11"))
    C12 = num(inputs.get("Impact!C12"))
    C13 = num(inputs.get("Impact!C13"))
    C14 = num(inputs.get("Impact!C14"))
    C15 = num(inputs.get("Impact!C15"))
    C16 = num(inputs.get("Impact!C16"))
    C17 = num(inputs.get("Impact!C17"))

    C18 = C8 + C9 + C10 + C11 + C12 + C13 + C14 + C15 + C16 + C17

    C22 = num(inputs.get("Impact!C22"))
    C23 = num(inputs.get("Impact!C23"))
    C24 = num(inputs.get("Impact!C24"))
    C25 = num(inputs.get("Impact!C25"))
    C26 = num(inputs.get("Impact!C26"))
    C27 = num(inputs.get("Impact!C27"))
    C28 = num(inputs.get("Impact!C28"))

    C29 = C22 + C23 + C24 + C25 + C26 + C27 + C28

    C31 = C18 + C29

    C4 = num(inputs.get("Impact!C4"))

    C33 = C4 + C31

    return C33