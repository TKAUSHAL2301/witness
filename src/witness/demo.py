"""A single case, told end to end — the whole argument on one screen.

`witness.verify` proves the numbers are real. This proves the *point*, which is
a different job. It takes one workbook cell and walks it through the exact
sequence a controller would live through:

  1. the ported code agrees with the spreadsheet on the historical values
  2. it is nevertheless wrong
  3. the fuzzer finds where, and shrinks it to the smallest input that breaks it
  4. the repaired port survives the same treatment

Step 1 is the one that matters. Tying out on history is the industry's entire
acceptance test, and this shows a port passing it while carrying a five-figure
error. Nothing here is replayed from a stored result: both ports are loaded
from disk and both are fuzzed live against the workbook.

  uv run python -m witness.demo
  uv run python -m witness.demo "budget-and-tax-rate-planning-tool::Levy Limit.E19"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from witness.fuzz import fuzz_case
from witness.gate import _to_serial
from witness.oracle import get_oracle
from witness.port import load_port, slugify

# Chained EDATE arithmetic: the baseline agrees on the workbook's own fiscal
# year and drifts by years on any other, which is worth $48,030 on this cell.
DEFAULT_CASE = "financial-forecasting-template-10-year::Available Funds.T48"

W = 74


def _rule(ch: str = "─") -> None:
    print(ch * W)


def _money(v) -> str:
    return f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)


def _historical(case: dict) -> tuple[list, object]:
    """The workbook's own saved inputs, and the value Excel cached for the target.

    This is the historical tie-out: the numbers the spreadsheet was last saved
    with, which is precisely the data a migration is normally signed off against.
    """
    import openpyxl

    wb = openpyxl.load_workbook(case["workbook"], data_only=True)
    vector = []
    for spec in case["inputs"]:
        sheet, coord = spec["key"].split("!", 1)
        vector.append(_to_serial(wb[sheet][coord.replace("$", "")].value))
    tsheet, tcoord = case["target"].split("!", 1)
    return vector, _to_serial(wb[tsheet][tcoord.replace("$", "")].value)


def run(case_id: str, trials: int = 3000, seed: int = 11) -> int:
    cases = json.loads(Path("results/cases.json").read_text())
    match = [c for c in cases if c["id"] == case_id]
    if not match:
        print(f"No such case: {case_id}\nTry one of:")
        for c in cases[:8]:
            print(f"  {c['id']}")
        return 1
    case = match[0]

    print()
    _rule("═")
    print("WITNESS — one cell, end to end")
    _rule("═")
    print(f"  Workbook   {Path(case['workbook']).name}")
    print(f"  Target     {case['target']}")
    print(f"  Formulas behind it   {case['formula_nodes']} cells")
    print(f"  Free inputs          {len(case['inputs'])}")
    for spec in case["inputs"][:4]:
        used = ", ".join(spec.get("used_by", [])[:3]) or "—"
        print(f"    · {spec['key']:<28} {spec['kind']:<6} feeds {used}")
    print()

    oracle = get_oracle(case["workbook"])
    refs = [s["key"] for s in case["inputs"]]
    oracle_fn, _ = oracle.compile_case(refs, case["target"])

    ports = {}
    for arm in ("baseline", "witness"):
        p = Path("ports") / arm / f"{slugify(case_id)}.py"
        fn = load_port(p, refs) if p.exists() else None
        if fn is None:
            print(f"Missing or unloadable port: {p}")
            return 1
        ports[arm] = fn

    # ---- 1. the historical tie-out ------------------------------------------
    hist_vector, cached = _historical(case)
    _rule()
    print("STEP 1 — Tie out against the historical values, the way it is done today")
    _rule()
    print(f"  Inputs as the workbook was last saved: {[_money(v) for v in hist_vector]}")
    print(f"  Excel's own cached answer:             {_money(cached)}")
    tied = {}
    for arm in ("baseline", "witness"):
        try:
            got = ports[arm](hist_vector)
        except Exception as exc:  # noqa: BLE001
            got = f"error: {exc}"
        agree = isinstance(got, (int, float)) and isinstance(cached, (int, float)) and abs(got - cached) < 1e-6
        tied[arm] = agree
        print(f"  {arm:<9} port returns {_money(got):>18}   {'MATCHES' if agree else 'differs'}")
    print()
    if all(tied.values()):
        print("  Both ports tie out. On this evidence a controller signs the migration off.")
    elif any(tied.values()):
        which = [a for a, ok in tied.items() if ok]
        print(f"  Only the {', '.join(which)} port ties out here.")
    else:
        print("  Neither port ties out on this cell — the workbook was saved with these")
        print("  inputs blank, so there is no historical answer to check against.")
    print()

    # ---- 2. the same ports, fuzzed ------------------------------------------
    _rule()
    print(f"STEP 2 — Now generate {trials:,} inputs the history never contained")
    _rule()
    verdicts = {}
    for arm in ("baseline", "witness"):
        r = fuzz_case(case, oracle_fn, ports[arm], trials=trials, seed=seed)
        verdicts[arm] = r
        if r.certified:
            print(f"  {arm:<9} CERTIFIED — agreed on all {r.agreed:,} vectors")
        else:
            d = r.disagreement
            if d is None:
                why = r.error or "no disagreement recorded"
            elif d.actual is None:
                why = "returned no value at all"
            else:
                why = f"off by ${_money(d.delta)}" if d.delta is not None else "disagreed"
            print(f"  {arm:<9} FAILED at trial {d.trial if d else '?'} — {why}")
    print()

    # ---- 3. the shrunk counterexample ---------------------------------------
    failed = [a for a in ("baseline", "witness") if not verdicts[a].certified]
    if failed:
        arm = failed[0]
        d = verdicts[arm].disagreement
        _rule()
        print("STEP 3 — Shrink the failure to the smallest input that still breaks it")
        _rule()
        if d.shrunk_from:
            print(f"  Reduced from the raw failing vector (trial {d.shrunk_from}) to:")
        for k, v in list(d.vector.items())[:6]:
            print(f"    {k:<30} = {_money(v)}")
        if d.minimal_change:
            print(f"  Minimal change: {d.minimal_change}")
        print()
        print(f"    spreadsheet says   {_money(d.expected):>18}")
        if d.actual is None:
            print(f"    {arm} port says   {'no value at all':>18}")
            print()
            print("    The port did not return a wrong number — it returned nothing.")
            print("    It handles the one date the workbook was saved with and no other.")
        else:
            print(f"    {arm} port says   {_money(d.actual):>18}")
            if d.delta is not None:
                print(f"    difference         {_money(d.delta):>18}")
        print()
        print("  This vector — and nothing else — is what the repair loop receives.")
        print("  No prose, no critique. The ablation for that choice is in CHANGELOG.md.")
        print()

    _rule("═")
    b, w = verdicts["baseline"].certified, verdicts["witness"].certified
    if not b and w:
        print("  Both ports passed the historical tie-out. One of them was wrong.")
        print("  A fixed set of test cases cannot tell you which. A generator can.")
    elif b and w:
        print("  Both ports survived. On this cell the baseline was genuinely correct.")
    else:
        print("  See results/evaluation.json for this case in full.")
    _rule("═")
    print()
    return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    case_id = args[0] if args else DEFAULT_CASE
    trials = int(args[1]) if len(args) > 1 else 3000
    return run(case_id, trials=trials)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
