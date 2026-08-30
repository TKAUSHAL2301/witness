def _num(v):
    """Convert a value to a number the way Excel does."""
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


def _is_text(v):
    """Return True if v would be a text value in Excel (non-numeric string)."""
    if not isinstance(v, str):
        return False
    if v == '':
        return True
    try:
        float(v)
        return False
    except (ValueError, TypeError):
        return True


def _excel_gt(a, b):
    """Excel comparison: numbers < booleans < text."""
    # Determine types for ordering: 0=number, 1=bool (not used here), 2=text
    a_is_text = isinstance(a, str) and _is_text(a)
    b_is_text = isinstance(b, str) and _is_text(b)

    if a_is_text and not b_is_text:
        # text > number
        return True
    if not a_is_text and b_is_text:
        # number < text
        return False
    # Same type: compare numerically
    return _num(a) > _num(b)


def compute(inputs: dict):
    c12 = _num(inputs.get("Levy Limit!C12"))
    c13 = _num(inputs.get("Levy Limit!C13"))
    c15 = _num(inputs.get("Levy Limit!C15"))
    c16 = _num(inputs.get("Levy Limit!C16"))
    c17 = _num(inputs.get("Levy Limit!C17"))
    c20_raw = inputs.get("Levy Limit!C20")

    # C14 = ROUND((C12+C13)*0.025, 0)
    c14 = round((c12 + c13) * 0.025)

    # C18 = SUM(C12:C17)
    c18 = c12 + c13 + c14 + c15 + c16 + c17

    c20 = _num(c20_raw)

    # E19 = IF(C18>C20, C20, C18)
    # Use Excel comparison semantics (numbers < text)
    if _excel_gt(c18, c20_raw if c20_raw is not None else c20):
        return c20
    else:
        return c18