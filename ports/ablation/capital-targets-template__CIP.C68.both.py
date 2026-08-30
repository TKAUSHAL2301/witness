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

    C12 = n("CIP!C8") + n("CIP!C9") + n("CIP!C10") + n("CIP!C11")
    C17 = n("CIP!C14") + n("CIP!C15") + n("CIP!C16")
    C23 = n("CIP!C19") + n("CIP!C20") + n("CIP!C21") + n("CIP!C22")
    C28 = C17 + C23 + n("CIP!C27")
    C36 = n("CIP!C31") + n("CIP!C32") + n("CIP!C33") + n("CIP!C34") + n("CIP!C35")
    C43 = n("CIP!C38") + n("CIP!C39") + n("CIP!C40") + n("CIP!C41") + n("CIP!C42")
    C47 = n("CIP!C45") + n("CIP!C46")
    C53 = n("CIP!C49") + n("CIP!C50") + n("CIP!C51") + n("CIP!C52")
    C55 = C12 + C28 + C36 + C43 + C47 + C53
    C67 = sum(n(f"CIP!C{r}") for r in range(57, 67))
    C68 = C67 - C55
    return C68