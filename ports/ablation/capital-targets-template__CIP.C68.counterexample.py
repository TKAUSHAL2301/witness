def compute(inputs: dict):
    def n(key):
        v = inputs.get(key)
        if v is None or v == '' or v is False:
            return 0
        if v is True:
            return 1
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0

    def sum_range(prefix, start, end):
        return sum(n(f"{prefix}{i}") for i in range(start, end + 1))

    P = "CIP!C"

    C12 = sum_range(P, 8, 11)
    C17 = sum_range(P, 14, 16)
    C23 = sum_range(P, 19, 22)
    C28 = C17 + C23 + n(f"{P}27")
    C36 = sum_range(P, 31, 35)
    C43 = sum_range(P, 38, 42)
    C47 = sum_range(P, 45, 46)
    C53 = sum_range(P, 49, 52)
    C55 = C12 + C28 + C36 + C43 + C47 + C53
    C67 = sum_range(P, 57, 66)
    C68 = C67 - C55
    return C68