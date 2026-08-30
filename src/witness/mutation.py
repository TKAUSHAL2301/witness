"""Mutation testing for the verifier itself.

Accuracy on a fixed case set tells you whether an agent guessed right. It does
not tell you whether your *verifier* can detect a defect at all. A mutation
score does: inject a known defect into a known-good port and ask whether the
fuzzer catches it.

The first version of this suite used a single mutant — "treat blank as zero" —
and caught 0 of 10 cases. That was the wrong mutant for this corpus, not a weak
fuzzer: these workbooks feed their targets through SUM chains where Excel and
Python already agree on blanks. This version injects the failure families that
the corpus actually exhibits, which the real experiment surfaced:

  ROUNDING        banker's rounding vs Excel's half-away-from-zero
                  (this is the exact defect that beat Witness on Debt.H8)
  DATE_SERIAL     off-by-one on the Excel epoch / phantom 1900-02-29
                  (the family behind the four largest baseline errors)
  OFF_BY_ONE      a boundary shifted by one unit
  SIGN            negative inputs treated as their absolute value
  TRUNCATE        int() instead of round()
  SCALE           a percentage applied as a whole number

EQUIVALENT mutants are included as false-alarm controls. They change the code
without changing its meaning, and the fuzzer MUST NOT flag them. Without those
controls a mutation score just rewards paranoia.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from witness.fuzz import fuzz_case
from witness.oracle import WorkbookOracle
from witness.port import load_port, slugify


def _n(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


# --- semantic mutants: each MUST be caught -----------------------------------
SEMANTIC = {
    "rounding_bankers": lambda v: (round(v) if _n(v) is not None else v),
    "date_serial_off_by_one": lambda v: (v + 1 if _n(v) is not None and abs(v) > 20000 else v),
    "off_by_one": lambda v: (v + 1 if _n(v) is not None else v),
    "sign_flip_on_negative": lambda v: (abs(v) if _n(v) is not None else v),
    "truncate_not_round": lambda v: (float(int(v)) if _n(v) is not None else v),
    "scale_percent": lambda v: (v / 100.0 if _n(v) is not None and abs(v) > 1 else v),
    "epsilon_drift": lambda v: (v * 1.0001 if _n(v) is not None and abs(v) > 1 else v),
}

# --- equivalent mutants: each MUST NOT be caught ------------------------------
EQUIVALENT = {
    "identity": lambda v: v,
    "float_cast": lambda v: (float(v) if _n(v) is not None else v),
    "add_zero": lambda v: (v + 0.0 if _n(v) is not None else v),
    "negate_twice": lambda v: (-(-v) if _n(v) is not None else v),
    "sub_tiny_below_tolerance": lambda v: (v - 1e-12 if _n(v) is not None else v),
}


def run(trials: int = 2000, seed: int = 5, arm: str = "witness") -> dict:
    cases = json.loads(Path("results/cases.json").read_text())
    rows = []

    for case in cases:
        slug = slugify(case["id"])
        p = Path("ports") / arm / f"{slug}.py"
        if not p.exists():
            continue
        try:
            o = WorkbookOracle(case["workbook"])
            refs = [s["key"] for s in case["inputs"]]
            oracle_fn, _ = o.compile_case(refs, case["target"])
        except Exception:  # noqa: BLE001
            continue
        port_fn = load_port(p, refs)
        if port_fn is None:
            continue

        # Only mutate ports that are themselves clean: mutating an already-wrong
        # port measures nothing.
        base = fuzz_case(case, oracle_fn, port_fn, trials=min(trials, 1000), seed=seed)
        if not base.certified:
            rows.append({"case_id": case["id"], "skipped": "port not certified"})
            continue

        killed, missed, false_alarms, clean = [], [], [], []
        for name, mut in SEMANTIC.items():
            mutated = (lambda m: (lambda vs: m(port_fn(vs))))(mut)
            r = fuzz_case(case, oracle_fn, mutated, trials=trials, seed=seed)
            (killed if not r.certified else missed).append(name)
        for name, mut in EQUIVALENT.items():
            mutated = (lambda m: (lambda vs: m(port_fn(vs))))(mut)
            r = fuzz_case(case, oracle_fn, mutated, trials=trials, seed=seed)
            (false_alarms if not r.certified else clean).append(name)

        rows.append(
            {
                "case_id": case["id"],
                "killed": killed,
                "missed": missed,
                "false_alarms": false_alarms,
                "clean": clean,
                "kill_rate": round(len(killed) / len(SEMANTIC), 3),
            }
        )
        print(
            f"[{len(killed)}/{len(SEMANTIC)} killed, {len(false_alarms)}/{len(EQUIVALENT)} false alarms] "
            f"{case['id'][:54]}"
            + (f"   missed: {','.join(missed)}" if missed else "")
        )

    scored = [r for r in rows if "kill_rate" in r]
    tot_k = sum(len(r["killed"]) for r in scored)
    tot_s = len(scored) * len(SEMANTIC)
    tot_f = sum(len(r["false_alarms"]) for r in scored)
    tot_e = len(scored) * len(EQUIVALENT)
    summary = {
        "cases_scored": len(scored),
        "semantic_mutants_per_case": len(SEMANTIC),
        "equivalent_mutants_per_case": len(EQUIVALENT),
        "mutation_kill_rate": round(tot_k / tot_s, 4) if tot_s else 0.0,
        "false_alarm_rate": round(tot_f / tot_e, 4) if tot_e else 0.0,
        "killed": tot_k,
        "semantic_total": tot_s,
        "false_alarms": tot_f,
        "equivalent_total": tot_e,
    }
    Path("results").mkdir(exist_ok=True)
    Path("results/mutation.json").write_text(
        json.dumps({"summary": summary, "cases": rows}, indent=2, default=str)
    )
    print(f"\n{'=' * 70}")
    print(f"MUTATION SCORE  ({len(scored)} certified ports, {trials:,} trials per mutant)")
    print(f"{'=' * 70}")
    print(f"  kill rate        {tot_k}/{tot_s}   {summary['mutation_kill_rate']:.1%}")
    print(f"  false-alarm rate {tot_f}/{tot_e}   {summary['false_alarm_rate']:.1%}   (must be 0%)")
    print(f"{'=' * 70}")
    return summary


def main(argv: list[str]) -> int:
    trials = int(argv[1]) if len(argv) > 1 else 2000
    arm = argv[2] if len(argv) > 2 else "witness"
    s = run(trials=trials, arm=arm)
    print("results/mutation.json written")
    return 0 if s["false_alarm_rate"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
