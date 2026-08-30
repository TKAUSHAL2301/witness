def _num(v):
    """Coerce a value to a number the way Excel does."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0
    return 0


def _excel_gt(a, b):
    """Replicate Excel's > comparison with type-based ordering.

    Excel ordering: blank < number < string < boolean.
    A number is never greater than a string (including empty string).
    """
    a_is_str = isinstance(a, str)
    b_is_str = isinstance(b, str)
    a_is_bool = isinstance(a, bool)
    b_is_bool = isinstance(b, bool)

    # Coerce None to 0 for comparison purposes
    if a is None:
        a = 0
    if b is None:
        b = 0

    # If both same type category, compare directly
    if a_is_bool and b_is_bool:
        return a > b
    if a_is_str and b_is_str:
        return a.lower() > b.lower()

    # Cross-type: blank(0) < number < string < boolean
    def _rank(v, was_str, was_bool):
        if was_bool:
            return 3
        if was_str:
            return 2
        return 1  # number (including coerced None)

    ra = _rank(a, a_is_str, a_is_bool)
    rb = _rank(b, b_is_str, b_is_bool)
    if ra != rb:
        return ra > rb

    return a > b


def compute(inputs: dict):
    C12 = _num(inputs.get("Levy Limit!C12"))
    C13 = _num(inputs.get("Levy Limit!C13"))
    C15 = _num(inputs.get("Levy Limit!C15"))
    C16 = _num(inputs.get("Levy Limit!C16"))
    C17 = _num(inputs.get("Levy Limit!C17"))
    C20_raw = inputs.get("Levy Limit!C20")

    # C14 = ROUND((C12+C13)*0.025, 0)
    C14 = round((C12 + C13) * 0.025)

    # C18 = SUM(C12:C17)
    C18 = C12 + C13 + C14 + C15 + C16 + C17

    # E19 = IF(C18>C20, C20, C18)
    # Keep C20 in original type for comparison to match Excel semantics
    if _excel_gt(C18, C20_raw):
        return _num(C20_raw)
    else:
        return C18