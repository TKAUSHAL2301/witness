"""Case selection: turn 12 workbooks into a frozen list of certification cases.

A case is (workbook, target output cell, typed input domain). Frozen to
results/cases.json before any porting happens, so the evaluation set cannot
drift to flatter whichever port I happen to produce.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from witness import dag as D
from witness.fuzz import VectorSampler
from witness.oracle import WorkbookOracle, get_oracle

SCREEN_DRAWS = 60
MIN_DISTINCT = 3
MIN_NONZERO_FRAC = 0.25


def sensitivity_screen(oracle: WorkbookOracle, target: str, specs: list) -> tuple[bool, str]:
    """Reject any target that does not actually respond to its inputs.

    Without this screen, 9 of the first 16 candidate cases certified a port that
    unconditionally returns 0.0 — the target was constant under sampling, so a
    do-nothing agent scored 100%. That is the exact defect the NeurIPS agentic-
    benchmark audit found in tau-bench and SWE-Lancer, and a case that cannot
    distinguish a real port from `return 0` measures nothing.
    """
    refs = [s.key for s in specs]
    try:
        fn, _ = oracle.compile_case(refs, target)
    except Exception as e:  # noqa: BLE001
        return False, f"cone: {type(e).__name__}"

    dicts = [s.to_dict() for s in specs]
    sampler = VectorSampler(dicts, seed=7)
    seen, nonzero, errs = set(), 0, 0
    for _ in range(SCREEN_DRAWS):
        try:
            v = fn(sampler.draw())
        except Exception:  # noqa: BLE001
            errs += 1
            continue
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            seen.add(round(float(v), 9))
            if abs(v) > 1e-9:
                nonzero += 1
        elif v is not None:
            seen.add(str(v))
    ok_draws = SCREEN_DRAWS - errs
    if ok_draws < SCREEN_DRAWS * 0.5:
        return False, f"unstable ({errs} errors)"
    if len(seen) < MIN_DISTINCT:
        return False, f"constant ({len(seen)} distinct values)"
    if nonzero < ok_draws * MIN_NONZERO_FRAC:
        return False, f"mostly zero ({nonzero}/{ok_draws} nonzero)"
    return True, f"{len(seen)} distinct, {nonzero}/{ok_draws} nonzero"


def main(argv: list[str]) -> int:
    corpus = Path(argv[1]) if len(argv) > 1 else Path("corpus")
    per_book = int(argv[2]) if len(argv) > 2 else 2

    cases = []
    for p in sorted(corpus.glob("*.xlsx")):
        try:
            g = D.build(p)
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {p.name}: {type(e).__name__}")
            continue
        if not g.formula_cells:
            print(f"[skip] {p.name}: no formulas")
            continue
        # Screen many more candidates than we keep; most will be rejected.
        picked_all = D.pick_cases(g, n=per_book * 25)
        if not picked_all:
            print(f"[skip] {p.name}: no clean output slice")
            continue
        try:
            oracle = get_oracle(p)
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {p.name}: oracle {type(e).__name__}")
            continue

        picked = []
        for sl in picked_all:
            if len(picked) >= per_book:
                break
            ok, why = sensitivity_screen(oracle, sl["target"], sl["inputs"])
            if not ok:
                continue
            sl["screen"] = why
            picked.append(sl)
        if not picked:
            print(f"[skip] {p.name}: no target survived the sensitivity screen")
            continue
        for sl in picked:
            cid = f"{p.stem}::{sl['target'].replace('!', '.')}"
            cases.append(
                {
                    "id": cid,
                    "workbook": str(p),
                    "target": sl["target"],
                    "formula_nodes": sl["formula_nodes"],
                    "screen": sl.get("screen", ""),
                    "inputs": [i.to_dict() for i in sl["inputs"]],
                }
            )
            print(
                f"[case] {cid:<58} {sl['formula_nodes']:>5} nodes "
                f"{len(sl['inputs']):>3} in  [{sl.get('screen', '')}]"
            )

    Path("results").mkdir(exist_ok=True)
    Path("results/cases.json").write_text(json.dumps(cases, indent=2, default=str))
    books = len({c["workbook"] for c in cases})
    print(f"\n{len(cases)} cases across {books} workbooks -> results/cases.json")
    return 0 if len(cases) >= 10 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
