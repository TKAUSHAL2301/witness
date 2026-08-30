def compute(inputs: dict):
    def num(val):
        """Convert a value to a number the way Excel does for arithmetic (+)."""
        if val is None:
            return 0
        if isinstance(val, bool):
            return int(val)
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            if val == '':
                return 0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0  # SUM skips text; + would #VALUE!, but we degrade gracefully
        return 0

    def excel_sum(keys):
        """Excel SUM: skip None, blank strings, and non-numeric strings."""
        total = 0
        for k in keys:
            v = inputs.get(k)
            if v is None or v == '':
                continue
            if isinstance(v, bool):
                total += int(v)
            elif isinstance(v, (int, float)):
                total += v
            elif isinstance(v, str):
                # SUM ignores text that can't convert
                try:
                    total += float(v)
                except (ValueError, TypeError):
                    pass
        return total

    c8_c17 = [f"Impact!C{r}" for r in range(8, 18)]
    c22_c28 = [f"Impact!C{r}" for r in range(22, 29)]

    c18 = excel_sum(c8_c17)
    c29 = excel_sum(c22_c28)
    c31 = c18 + c29
    c4 = num(inputs.get("Impact!C4"))
    c33 = c4 + c31
    return c33