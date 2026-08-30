"""The experiment.

Both arms get the same cases, the same fuzzer, the same seeds, the same
tolerance and the same scorer. The only difference is how the port was
produced. Paired comparison: per-case difficulty cancels out.

Needs no API key — it evaluates the committed ports.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

from witness.fuzz import VectorSampler, fuzz_case
from witness.invariants import check as check_invariants
from witness.oracle import get_oracle
from witness.port import load_port, slugify

SEEDS = [11, 23, 47]


def evaluate(trials: int = 10_000, seeds: list[int] = None, arms=("baseline", "witness")) -> dict:
    seeds = seeds or SEEDS
    cases = json.loads(Path("results/cases.json").read_text())
    rows = []

    for case in cases:
        slug = slugify(case["id"])
        try:
            o = get_oracle(case["workbook"])
            refs = [s["key"] for s in case["inputs"]]
            oracle_fn, nodes = o.compile_case(refs, case["target"])
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {case['id']}: oracle {type(e).__name__}")
            continue

        row = {"case_id": case["id"], "nodes": nodes, "inputs": len(refs), "arms": {}}
        for arm in arms:
            p = Path("ports") / arm / f"{slug}.py"
            if not p.exists():
                row["arms"][arm] = {"missing": True, "certified": False}
                print(f"[{arm[:4]}] {case['id']:<52} PORT MISSING")
                continue
            port_fn = load_port(p, refs)
            if port_fn is None:
                row["arms"][arm] = {"import_failed": True, "certified": False}
                print(f"[{arm[:4]}] {case['id']:<52} IMPORT FAILED")
                continue

            runs = []
            for sd in seeds:
                t0 = time.time()
                r = fuzz_case(case, oracle_fn, port_fn, trials=trials, seed=sd)
                d = r.to_dict()
                d["seconds"] = round(time.time() - t0, 1)
                d["seed"] = sd
                runs.append(d)
            try:
                inv = check_invariants(
                    case, oracle_fn, port_fn, VectorSampler(case["inputs"], seed=97)
                ).to_dict()
            except Exception as e:  # noqa: BLE001
                inv = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
            certified_all = all(r["certified"] for r in runs) and not inv.get("violations")
            first_fail = min(
                (r["disagreement"]["trial"] for r in runs if r.get("disagreement")), default=None
            )
            worst = max(
                (abs(r["disagreement"].get("delta") or 0) for r in runs if r.get("disagreement")),
                default=0.0,
            )
            row["arms"][arm] = {
                "certified": certified_all,
                "runs": runs,
                "first_failing_trial": first_fail,
                "max_abs_delta": worst,
                "mean_agreed": statistics.mean(r["agreed"] for r in runs),
                "invariants": inv,
            }
            nviol = len(inv.get("violations", []))
            mark = "CERTIFIED" if certified_all else (
                f"INVARIANT-VIOLATION x{nviol}" if nviol and first_fail is None else f"FAILED@{first_fail}"
            )
            extra = f"  Δ={worst:,.2f}" if worst else ""
            print(f"[{arm[:4]}] {case['id']:<52} {mark}{extra}")
        rows.append(row)

    summary = {"trials": trials, "seeds": seeds, "cases": len(rows), "arms": {}}
    for arm in arms:
        cert = [r for r in rows if r["arms"].get(arm, {}).get("certified")]
        summary["arms"][arm] = {
            "certified": len(cert),
            "total": len(rows),
            "rate": round(len(cert) / len(rows), 4) if rows else 0.0,
        }

    out = {"summary": summary, "cases": rows}
    Path("results").mkdir(exist_ok=True)
    Path("results/evaluation.json").write_text(json.dumps(out, indent=2, default=str))
    return out


def print_table(out: dict) -> None:
    s = out["summary"]
    print(f"\n{'=' * 74}")
    print(f"CERTIFIED-EQUIVALENCE RATE  (pass^{s['trials']}, all of seeds {s['seeds']})")
    print(f"{'=' * 74}")
    print(f"{'METRIC':<38}{'BASELINE':>12}{'WITNESS':>12}{'CHANGE':>12}")
    b = s["arms"].get("baseline", {})
    w = s["arms"].get("witness", {})
    bc, wc, tot = b.get("certified", 0), w.get("certified", 0), s["cases"]
    print(f"{'Ports certified':<38}{f'{bc}/{tot}':>12}{f'{wc}/{tot}':>12}{f'+{wc - bc}':>12}")
    dr = w.get('rate', 0) - b.get('rate', 0)
    print(f"{'Certified-equivalence rate':<38}{b.get('rate', 0):>11.0%}{w.get('rate', 0):>12.0%}{f'+{dr:.0%}':>12}")
    deltas = [
        c["arms"]["baseline"].get("max_abs_delta", 0)
        for c in out["cases"]
        if not c["arms"].get("baseline", {}).get("certified")
    ]
    if deltas:
        print(f"{'Largest undetected baseline error':<38}{max(deltas):>11,.2f}{'—':>12}{'—':>12}")
    print(f"{'=' * 74}")


def main(argv: list[str]) -> int:
    trials = int(argv[1]) if len(argv) > 1 else 10_000
    out = evaluate(trials=trials)
    print_table(out)
    print("results/evaluation.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
