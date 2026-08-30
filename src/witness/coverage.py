"""Formula coverage — which parts of the calculation were actually exercised.

A certificate that says "10,000 vectors agreed" is weaker than it sounds if
every one of those vectors drove the calculation down the same branch. An
`IF` whose false arm was never taken is untested, and the certificate should
say so in a number rather than a disclaimer.

Coverage here is measured on the oracle side, because the oracle is the
authority on what the calculation actually does:

  CELL COVERAGE    fraction of formula cells in the target's cone whose value
                   varied across the sampled vectors. A cell that never changed
                   was, for this input domain, effectively a constant.
  BRANCH COVERAGE  for each IF/IFS/CHOOSE cell, whether both outcomes were
                   observed. A branch seen only one way is reported explicitly.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from witness import dag as D
from witness.fuzz import VectorSampler
from witness.oracle import WorkbookOracle, cell_key, unwrap

BRANCHING = {"IF", "IFS", "CHOOSE", "SWITCH", "IFERROR", "IFNA"}


def _cone_cells(g: D.WorkbookDAG, target: str) -> list[str]:
    seen, stack, out = set(), [target], []
    while stack:
        k = stack.pop()
        if k in seen:
            continue
        seen.add(k)
        c = g.cells.get(k)
        if c is None or not c.is_formula:
            continue
        out.append(k)
        stack.extend(c.precedents)
    return out


def measure(case: dict, probes: int = 60, seed: int = 3) -> dict:
    g = D.build(Path(case["workbook"]))
    cone = _cone_cells(g, case["target"])
    branchy = [k for k in cone if g.cells[k].functions & BRANCHING]

    o = WorkbookOracle(case["workbook"])
    refs = [s["key"] for s in case["inputs"]]
    payload_keys = {r: cell_key(case["workbook"], r) for r in refs}
    watch = {k: cell_key(case["workbook"], k).upper() for k in cone}

    sampler = VectorSampler(case["inputs"], seed=seed)
    observed: dict[str, set] = {k: set() for k in cone}
    ok = 0
    for _ in range(probes):
        vec = sampler.draw()
        try:
            sol = o.model.calculate(
                inputs={payload_keys[refs[i]]: vec[i] for i in range(len(refs))}
            )
        except Exception:  # noqa: BLE001
            continue
        norm = {k.upper(): v for k, v in sol.items()}
        ok += 1
        for k, wk in watch.items():
            if wk in norm:
                try:
                    observed[k].add(repr(unwrap(norm[wk])))
                except Exception:  # noqa: BLE001
                    pass

    varied = [k for k in cone if len(observed[k]) > 1]
    constant = [k for k in cone if len(observed[k]) == 1]
    unreached = [k for k in cone if not observed[k]]
    branch_both = [k for k in branchy if len(observed[k]) > 1]
    branch_one = [k for k in branchy if len(observed[k]) == 1]

    return {
        "case_id": case["id"],
        "probes_run": ok,
        "cone_cells": len(cone),
        "varied": len(varied),
        "constant": len(constant),
        "unreached": len(unreached),
        "cell_coverage": round(len(varied) / len(cone), 4) if cone else 0.0,
        "branching_cells": len(branchy),
        "branches_both_ways": len(branch_both),
        "branches_one_way": len(branch_one),
        "branch_coverage": round(len(branch_both) / len(branchy), 4) if branchy else None,
        "constant_cells_sample": constant[:8],
        "one_way_branches_sample": branch_one[:8],
    }


def main(argv: list[str]) -> int:
    probes = int(argv[1]) if len(argv) > 1 else 60
    cases = json.loads(Path("results/cases.json").read_text())
    rows = []
    for c in cases:
        try:
            r = measure(c, probes=probes)
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {c['id'][:50]}: {type(e).__name__}")
            continue
        rows.append(r)
        bc = f"{r['branch_coverage']:.0%}" if r["branch_coverage"] is not None else "n/a"
        print(
            f"[cov] {c['id'][:50]:<50} cells {r['cell_coverage']:>6.0%} "
            f"({r['varied']}/{r['cone_cells']})  branches {bc:>5}"
        )
    Path("results").mkdir(exist_ok=True)
    Path("results/coverage.json").write_text(json.dumps(rows, indent=2, default=str))
    if rows:
        mean_c = sum(r["cell_coverage"] for r in rows) / len(rows)
        wb = [r["branch_coverage"] for r in rows if r["branch_coverage"] is not None]
        print(f"\nmean cell coverage: {mean_c:.1%}")
        if wb:
            print(f"mean branch coverage: {sum(wb) / len(wb):.1%}  ({len(wb)} cases with branches)")
    print("results/coverage.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
