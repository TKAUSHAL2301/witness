def compute(inputs: dict):
    def n(key):
        v = inputs.get(key)
        if v is None or v == '':
            return 0
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    C12 = sum(n(f"CIP!C{r}") for r in (8, 9, 10, 11))
    C17 = sum(n(f"CIP!C{r}") for r in (14, 15, 16))
    C23 = sum(n(f"CIP!C{r}") for r in (19, 20, 21, 22))
    C28 = C17 + C23 + n("CIP!C27")
    C36 = sum(n(f"CIP!C{r}") for r in (31, 32, 33, 34, 35))
    C43 = sum(n(f"CIP!C{r}") for r in (38, 39, 40, 41, 42))
    C47 = sum(n(f"CIP!C{r}") for r in (45, 46))
    C53 = sum(n(f"CIP!C{r}") for r in (49, 50, 51, 52))
    C55 = C12 + C28 + C36 + C43 + C47 + C53
    C67 = sum(n(f"CIP!C{r}") for r in range(57, 67))
    C68 = C67 - C55
    return C68