"""Ablation — what the repair loop is actually fed.

Witness hands the agent ONLY a shrunk counterexample: the minimal failing input
vector, both outputs, and which inputs differ. No explanation of what went
wrong.

The obvious alternative — and what most agent repair loops actually do — is to
have a model look at the failure and write a critique, then hand that critique
to the fixer. This module runs that arm on the same cases with the same budget
so the changelog can report a number instead of an opinion.

Arms:
  counterexample  shrunk failing vector only          (what Witness ships)
  prose           an LLM critique of the failure      (the removed experiment)
  both            counterexample + critique           (does more context help?)

Reported: repairs-to-certify, and certified-or-not at the same trial budget.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

from witness.fuzz import fuzz_case
from witness.oracle import get_oracle
from witness.port import CONTRACT, _cone_source, _input_block, _run_agent, _extract_code, load_port, slugify

TRIALS = 2000
SEED = 11
MAX_REPAIRS = 3


def _critique(case: dict, code: str, d) -> str:
    """The prose arm: ask a model to explain the failure, then pass the prose on."""
    p = textwrap.dedent(f"""\
        A Python port of an Excel formula disagrees with the spreadsheet.

        Target: {case["target"]}
        Failing inputs: {json.dumps(d.vector, default=str)[:1200]}
        Excel returned: {d.expected!r}
        The port returned: {d.actual!r}

        The port:
        ```python
        {code[:6000]}
        ```

        Explain in prose what is wrong and how to fix it. Do not write code.
        """)
    return _run_agent(p, Path.cwd(), turns=2, tools="")[:4000]


def run_arm(case: dict, arm: str, oracle_fn, refs: list[str], workdir: Path) -> dict:
    base_prompt = textwrap.dedent(f"""\
        Reimplement one Excel calculation in Python.

        TARGET CELL: {case["target"]}

        The exact formulas behind it, as extracted from the workbook:
        {_cone_source(case)}

        The input cells, with the domain each one is sampled from:
        {_input_block(case)}

        {CONTRACT}
        """)

    out = workdir / f"{slugify(case['id'])}.{arm}.py"
    code = _extract_code(_run_agent(base_prompt, Path.cwd(), turns=6, tools=""))
    out.write_text(code)

    history = []
    for attempt in range(MAX_REPAIRS):
        fn = load_port(out, refs)
        if fn is None:
            fb, d = "The module failed to import or defines no compute(inputs).", None
        else:
            r = fuzz_case(case, oracle_fn, fn, trials=TRIALS, seed=SEED)
            history.append({"attempt": attempt, "agreed": r.agreed, "certified": r.certified})
            if r.certified:
                return {"arm": arm, "certified": True, "repairs": attempt, "history": history}
            d = r.disagreement
            ce = json.dumps(
                {
                    "failing_inputs": d.vector,
                    "excel_returned": d.expected,
                    "your_port_returned": d.actual,
                    "minimal_differing_inputs": d.minimal_change,
                },
                indent=2,
                default=str,
            )
            if arm == "counterexample":
                fb = ce
            elif arm == "prose":
                fb = _critique(case, code, d)
            else:  # both
                fb = ce + "\n\nAnalysis:\n" + _critique(case, code, d)

        repair = base_prompt + textwrap.dedent(f"""

            Your previous module was:
            ```python
            {code}
            ```

            It disagreed with Excel. Here is what is known about the failure:
            {fb}

            Emit the corrected module.
            """)
        code = _extract_code(_run_agent(repair, Path.cwd(), turns=6, tools=""))
        out.write_text(code)

    return {"arm": arm, "certified": False, "repairs": MAX_REPAIRS, "history": history}


def main(argv: list[str]) -> int:
    n_cases = int(argv[1]) if len(argv) > 1 else 4
    arms = ["counterexample", "prose", "both"]
    cases = json.loads(Path("results/cases.json").read_text())[:n_cases]
    work = Path("ports/ablation")
    work.mkdir(parents=True, exist_ok=True)

    rows = []
    for c in cases:
        try:
            o = get_oracle(c["workbook"])
            refs = [s["key"] for s in c["inputs"]]
            oracle_fn, _ = o.compile_case(refs, c["target"])
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {c['id']}: {type(e).__name__}")
            continue
        row = {"case_id": c["id"], "arms": {}}
        for a in arms:
            try:
                r = run_arm(c, a, oracle_fn, refs, work)
            except Exception as e:  # noqa: BLE001
                r = {"arm": a, "certified": False, "repairs": None, "error": str(e)[:200]}
            row["arms"][a] = r
            mark = "certified" if r["certified"] else "FAILED"
            print(f"[{a:>14}] {c['id']:<46} {mark} after {r['repairs']} repairs")
        rows.append(row)

    summary = {}
    for a in arms:
        got = [r["arms"][a] for r in rows if a in r["arms"]]
        cert = [g for g in got if g["certified"]]
        summary[a] = {
            "certified": len(cert),
            "total": len(got),
            "mean_repairs_when_certified": (
                round(sum(g["repairs"] for g in cert) / len(cert), 2) if cert else None
            ),
        }

    Path("results/ablation.json").write_text(
        json.dumps({"summary": summary, "cases": rows}, indent=2, default=str)
    )
    print(f"\n{'=' * 68}")
    print(f"{'REPAIR SIGNAL':<22}{'CERTIFIED':>12}{'MEAN REPAIRS':>16}")
    for a in arms:
        s = summary[a]
        print(f"{a:<22}{f'{s['certified']}/{s['total']}':>12}"
              f"{str(s['mean_repairs_when_certified']):>16}")
    print(f"{'=' * 68}\nresults/ablation.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
