def compute(inputs: dict):
    """Compute Annual!D31 = SUM(Annual!D5:D28) + SUM(Special!D5:D28)."""
    total = 0.0
    for sheet in ("Annual", "Special"):
        for row in range(5, 29):
            val = inputs.get(f"{sheet}!D{row}")
            if val is None or isinstance(val, bool):
                continue
            try:
                total += float(val)
            except (ValueError, TypeError):
                # Excel SUM ignores text values
                continue
    return total
