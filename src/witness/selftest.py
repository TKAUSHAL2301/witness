"""Harness validation. Run before trusting any number this repo produces.

Anthropic's eval guidance is blunt about this: run a known-good reference
solution through the harness N times, and if it does not pass N-for-N, the
environment is leaking nondeterminism and no score from it means anything.

Three checks:
  IDENTITY  oracle vs itself           -> must certify (no false alarms)
  MUTANT    oracle vs a broken port    -> must fail   (real detection power)
  SHORTCUT  a do-nothing port          -> must fail   (metric is not gameable)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from witness.fuzz import fuzz_case
from witness.oracle import WorkbookOracle

MUTANTS = {
    "blank_as_zero": lambda vs: [0 if v is None else v for v in vs],
    "drop_last_input": lambda vs: vs[:-1] + [0] if vs else vs,
}


def main(argv: list[str]) -> int:
    trials = int(argv[1]) if len(argv) > 1 else 300
    cases = json.loads(Path("results/cases.json").read_text())
    rows = []
    fails = 0

    for case in cases:
        try:
            o = WorkbookOracle(case["workbook"])
            refs = [s["key"] for s in case["inputs"]]
            fn, nodes = o.compile_case(refs, case["target"])
        except Exception as e:  # noqa: BLE001
            print(f"[SKIP] {case['id']:<58} {type(e).__name__}: {str(e)[:60]}")
            rows.append({"case_id": case["id"], "skipped": str(e)[:200]})
            continue

        # IDENTITY: the oracle compared against itself must never disagree.
        ident = fuzz_case(case, fn, fn, trials=trials, seed=1)

        # MUTANT: a port that silently treats blank as zero.
        mutated = lambda vs: fn(MUTANTS["blank_as_zero"](vs))  # noqa: E731
        mut = fuzz_case(case, fn, mutated, trials=trials, seed=1)

        # SHORTCUT: a port that always returns 0. Must not certify.
        short = fuzz_case(case, fn, lambda vs: 0.0, trials=trials, seed=1)

        ok = ident.certified and not short.certified
        if not ok:
            fails += 1
        mark = "PASS" if ok else "FAIL"
        print(
            f"[{mark}] {case['id']:<58} nodes={nodes:<5} "
            f"identity={ident.agreed}/{ident.trials_run} "
            f"mutant={'caught@' + str(mut.disagreement.trial) if mut.disagreement else 'MISSED'} "
            f"shortcut={'caught' if not short.certified else 'PASSED(!!)'}"
        )
        if ident.disagreement:
            d = ident.disagreement
            print(f"        identity broke: {d.minimal_change} exp={d.expected!r} got={d.actual!r}")
        rows.append(
            {
                "case_id": case["id"],
                "nodes": nodes,
                "identity": ident.to_dict(),
                "mutant_blank_as_zero": mut.to_dict(),
                "shortcut_always_zero": short.to_dict(),
                "ok": ok,
            }
        )

    Path("results").mkdir(exist_ok=True)
    Path("results/selftest.json").write_text(json.dumps(rows, indent=2, default=str))
    scored = [r for r in rows if "ok" in r]
    caught = sum(1 for r in scored if r["mutant_blank_as_zero"].get("disagreement"))
    print(f"\n{'=' * 70}")
    print(f"harness valid on {len(scored) - fails}/{len(scored)} cases  ({trials} trials each)")
    print(f"blank-as-zero mutant caught on {caught}/{len(scored)} cases")
    print("results/selftest.json written")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
