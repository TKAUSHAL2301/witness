def _num(v):
    """Coerce a value to a number the way Excel does."""
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return v
    return 0


def _is_numeric(v):
    """Return True if v is a real numeric value (not blank, not text)."""
    if v is None:
        return False
    if isinstance(v, bool):
        return True
    if isinstance(v, (int, float)):
        return True
    return False


def compute(inputs: dict):
    C12 = _num(inputs.get("Levy Limit!C12"))
    C13 = _num(inputs.get("Levy Limit!C13"))
    C15 = _num(inputs.get("Levy Limit!C15"))
    C16 = _num(inputs.get("Levy Limit!C16"))
    C17 = _num(inputs.get("Levy Limit!C17"))

    raw_C20 = inputs.get("Levy Limit!C20")
    C20 = _num(raw_C20)

    C14 = round((C12 + C13) * 0.025)
    C18 = C12 + C13 + C14 + C15 + C16 + C17

    # Excel: numbers are always "less than" text/strings in comparisons,
    # so if C20 is text or blank string, C18 > C20 is FALSE → return C18.
    if not _is_numeric(raw_C20):
        return C18

    E19 = C20 if C18 > C20 else C18
    return E19