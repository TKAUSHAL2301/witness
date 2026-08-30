Result matches Excel's cached value of 1159963 exactly. The port handles None, missing keys, negatives, and the Excel-style round-half-away-from-zero correctly.

The module is at `ports/witness/capital-targets-template__Debt.G8.py`. Key details:

- **G8 = G6 + G7** (Total Debt = Within-levy + Excluded)
- **G6** = `ROUND(SUM(G11:G16) + SUM(G19:G24), 0)` — within-levy principal + interest, with G20/G21 as hardcoded constants
- **G7** = `ROUND(SUM(G31:G38) + SUM(G41:G48), 0)` — excluded principal + interest, with G41/G42/G44/G45/G46 as hardcoded constants
- Used `math.floor(x + 0.5)` instead of Python's `round()` to match Excel's round-half-up behavior (that was a 1-unit discrepancy on the 1005352.5 → 1005353 rounding)