Port written and verified. The computation matches Excel's cached value of **1,119,088** exactly.

**What H8 computes:** Total debt service — it sums two sections:
- **H6 (Short-term debt):** `ROUND(SUM(H11:H16) + SUM(H19:H24), 0)` — six input principal amounts plus six payment items (4 inputs + 2 hardcoded constant formulas)
- **H7 (Long-term debt):** `ROUND(SUM(H31:H38) + SUM(H41:H48), 0)` — eight input principal amounts plus eight payment items (3 inputs + 5 hardcoded constant formulas)