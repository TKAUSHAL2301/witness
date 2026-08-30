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

    def excel_gt(a, b):
        """Excel comparison: numbers < text < booleans in mixed-type comparisons."""
        a_val = inputs.get("Levy Limit!C18_raw", a)
        b_val = inputs.get("Levy Limit!C20")
        # We need the raw values for comparison typing
        # Retype: determine type ranks (number=0, text=1, bool=2)
        def type_rank(v):
            if isinstance(v, bool):
                return 2
            if isinstance(v, (int, float)):
                return 0
            if isinstance(v, str):
                return 1
            if v is None:
                return 0  # blank treated as 0 (number)
            return 0
        ra = type_rank(a)
        rb = type_rank(b)
        if ra != rb:
            return ra > rb
        return num(a) > num(b) if ra == 0 else a > b

    C12 = num(inputs.get("Levy Limit!C12"))
    C13 = num(inputs.get("Levy Limit!C13"))
    C15 = num(inputs.get("Levy Limit!C15"))
    C16 = num(inputs.get("Levy Limit!C16"))
    C17 = num(inputs.get("Levy Limit!C17"))
    C20_raw = inputs.get("Levy Limit!C20")
    C20 = num(C20_raw)

    C14 = round((C12 + C13) * 0.025)
    C18 = C12 + C13 + C14 + C15 + C16 + C17

    # Excel IF(C18>C20, C20, C18) — comparison uses Excel mixed-type rules
    # In Excel: numbers < text < booleans when comparing across types
    # C18 is always numeric (result of SUM). C20 may be text.
    C18_is_num = True
    C20_is_text = isinstance(C20_raw, str) and not (C20_raw == '')  
    # blank ("") is treated as 0/number in comparisons? Actually no:
    # "" is a text value in Excel comparisons, so number < ""
    C20_is_text = isinstance(C20_raw, str)
    
    if C20_is_text:
        # number is always less than text in Excel, so C18 > C20 is FALSE
        gt = False
    elif C20_raw is None:
        # None/blank is numeric 0
        gt = C18 > 0
    else:
        gt = C18 > C20

    E19 = C20 if gt else C18
    return E19