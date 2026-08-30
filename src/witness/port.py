"""Port generation — the two arms of the experiment.

BASELINE  one general-purpose agent with basic tools, one instruction:
          "port this and make sure it is correct." It is allowed to read the
          workbook however it likes and to self-check however it likes. This is
          not a strawman: it is what the PDF names as an acceptable baseline
          ("one general purpose agent with basic tools") and it is what teams
          actually do today.

WITNESS   the same agent, same model, same budget, but given (a) the extracted
          formula cone instead of a raw file, (b) a typed input domain, and
          (c) a repair loop fed the shrunk counterexample from the differential
          fuzzer — and nothing else. No prose critique. That last constraint is
          the subject of the ablation.

Both arms emit ports/<arm>/<case>.py exposing compute(inputs: dict) -> value.
The generated ports are committed, so the evaluation is reproducible with no
API key. Only regeneration needs credentials.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

def slugify(case_id: str) -> str:
    """Stable filename for a case id. Shared with the evaluator."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", case_id)


CONTRACT = """\
Write a single self-contained Python module. It must define exactly:

    def compute(inputs: dict):
        ...

`inputs` maps cell references (the exact strings listed below, e.g. "Sheet1!B4")
to values. A value may be a float, an int, a string, True/False, or None.
None means the cell is BLANK in Excel.

Return the value of the target cell.

Rules:
- Standard library only. No imports of openpyxl, formulas, pandas, or numpy.
- Handle blank (None), zero, negative, and text-in-a-numeric-cell inputs the way
  Excel does. Do not raise on unexpected input; return what Excel would return.
- Output ONLY the Python module inside one ```python fenced block. No prose.
"""


def _run_agent(prompt: str, cwd: Path, turns: int = 30, tools: str | None = None) -> str:
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")}
    cmd = ["claude", "-p", prompt, "--max-turns", str(turns)]
    if tools:
        cmd += ["--allowedTools", tools]
    r = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f"agent exit {r.returncode}: {r.stderr[:400]}")
    return r.stdout


def _extract_code(text: str) -> str:
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    if blocks:
        return max(blocks, key=len).strip()
    return text.strip()


def _cone_source(case: dict) -> str:
    """The formulas behind the target — 'better context' in the PDF's language.
    The baseline does NOT get this; it gets the raw workbook."""
    from witness import dag as D

    g = D.build(Path(case["workbook"]))
    keys, stack, seen = [], [case["target"]], set()
    while stack:
        k = stack.pop()
        if k in seen:
            continue
        seen.add(k)
        c = g.cells.get(k)
        if c is None or not c.is_formula:
            continue
        keys.append(k)
        stack.extend(c.precedents)
    lines = []
    for k in sorted(keys):
        c = g.cells[k]
        lines.append(f"  {k}  :  {c.formula}")
    return "\n".join(lines[:400])


def _input_block(case: dict) -> str:
    lines = []
    for s in case["inputs"]:
        interesting = ", ".join(repr(v) for v in s["interesting"][:6])
        used = ",".join(sorted(s["used_by"])[:6])
        lines.append(f'  "{s["key"]}"  kind={s["kind"]}  observed={s["observed"]!r}'
                     + (f"  feeds={used}" if used else "")
                     + (f"  boundary_values=[{interesting}]" if interesting else ""))
    return "\n".join(lines)


def gen_baseline(case: dict, out: Path) -> str:
    """One general-purpose agent with basic tools, in an isolated sandbox.

    The agent is given file tools on purpose — that is what the PDF's allowed
    baseline ("one general purpose agent with basic tools") means, and it is
    what a real engineer would have. It runs in a temp directory containing a
    copy of the workbook so it cannot reach the repo, and it is told exactly
    where to write its answer. The first version of this harness read the
    agent's stdout instead, which silently captured its prose summary rather
    than its code on 3 of 10 cases and scored the baseline as broken. That was
    a defect in the measurement, not in the baseline.
    """
    import shutil
    import tempfile

    src = Path(case["workbook"])
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        shutil.copy2(src, work / src.name)
        target_file = work / "port.py"
        prompt = textwrap.dedent(f"""\
            Port one calculation out of an Excel workbook into Python, and make sure it is correct.

            Workbook: ./{src.name}   (in the current directory)
            Target cell: {case["target"]}
            Input cells: {", ".join(s["key"] for s in case["inputs"])}

            Read the workbook, work out what the target cell computes, and write the port.
            Check your work however you think best — you have Python available.

            Write your finished module to ./port.py in this directory.

            {CONTRACT}
            """)
        txt = _run_agent(prompt, work, turns=30, tools="Read,Write,Edit,Bash,Glob,Grep")
        if target_file.exists() and target_file.stat().st_size > 0:
            code = target_file.read_text()
        else:
            code = _extract_code(txt)
    out.write_text(code)
    return code


def gen_witness(case: dict, out: Path, max_repairs: int = 3) -> dict:
    """Structured context + a repair loop fed only the shrunk counterexample."""
    from witness.fuzz import fuzz_case
    from witness.oracle import WorkbookOracle

    o = WorkbookOracle(case["workbook"])
    refs = [s["key"] for s in case["inputs"]]
    oracle_fn, _ = o.compile_case(refs, case["target"])

    base_prompt = textwrap.dedent(f"""\
        Reimplement one Excel calculation in Python.

        TARGET CELL: {case["target"]}

        The exact formulas behind it, as extracted from the workbook:
        {_cone_source(case)}

        The input cells, with the domain each one is sampled from:
        {_input_block(case)}

        {CONTRACT}
        """)

    history = []
    code = _extract_code(_run_agent(base_prompt, Path.cwd(), turns=6, tools=""))
    out.write_text(code)

    for attempt in range(max_repairs):
        port_fn = load_port(out, refs)
        if port_fn is None:
            fb = "The module failed to import or has no compute(inputs) function."
        else:
            res = fuzz_case(case, oracle_fn, port_fn, trials=2000, seed=11)
            history.append({"attempt": attempt, "agreed": res.agreed, "trials": res.trials_run,
                            "certified": res.certified})
            if res.certified:
                return {"code": code, "repairs": attempt, "history": history, "certified": True}
            d = res.disagreement
            # THE REPAIR SIGNAL. Shrunk counterexample only — no critique, no prose.
            fb = json.dumps({
                "failing_inputs": {k: v for k, v in d.vector.items()},
                "excel_returned": _j(d.expected),
                "your_port_returned": _j(d.actual),
                "minimal_differing_inputs": d.minimal_change,
            }, indent=2, default=str)

        repair = base_prompt + textwrap.dedent(f"""

            Your previous module was:
            ```python
            {code}
            ```

            It disagreed with Excel on this input vector:
            {fb}

            Emit the corrected module.
            """)
        code = _extract_code(_run_agent(repair, Path.cwd(), turns=6, tools=""))
        out.write_text(code)

    return {"code": code, "repairs": max_repairs, "history": history, "certified": False}


def _j(v):
    return v if isinstance(v, (int, float, str, bool)) or v is None else str(v)


def load_port(path: Path, refs: list[str]):
    """Import a generated port and adapt it to fn(list_of_values) -> value."""
    import importlib.util

    try:
        spec = importlib.util.spec_from_file_location(f"port_{abs(hash(str(path)))}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        compute = getattr(mod, "compute", None)
        if compute is None:
            return None
    except Exception:  # noqa: BLE001
        return None

    def fn(values: list):
        return compute({refs[i]: values[i] for i in range(len(refs))})

    return fn


def main(argv: list[str]) -> int:
    arm = argv[1] if len(argv) > 1 else "both"
    only = argv[2] if len(argv) > 2 else None
    cases = json.loads(Path("results/cases.json").read_text())
    if only:
        cases = [c for c in cases if only in c["id"]]

    log = []
    for c in cases:
        slug = slugify(c["id"])
        for a in (["baseline", "witness"] if arm == "both" else [arm]):
            d = Path("ports") / a
            d.mkdir(parents=True, exist_ok=True)
            out = d / f"{slug}.py"
            if out.exists() and out.stat().st_size > 0:
                print(f"[skip] {a}/{slug} exists")
                continue
            try:
                if a == "baseline":
                    gen_baseline(c, out)
                    print(f"[ ok ] baseline/{slug}  ({len(out.read_text())} bytes)")
                    log.append({"arm": a, "case": c["id"], "ok": True})
                else:
                    r = gen_witness(c, out)
                    print(f"[ ok ] witness/{slug}  repairs={r['repairs']} certified={r['certified']}")
                    log.append({"arm": a, "case": c["id"], "ok": True,
                                "repairs": r["repairs"], "history": r["history"]})
            except Exception as e:  # noqa: BLE001
                print(f"[FAIL] {a}/{slug}: {type(e).__name__}: {str(e)[:150]}")
                log.append({"arm": a, "case": c["id"], "ok": False, "error": str(e)[:300]})

    Path("results").mkdir(exist_ok=True)
    Path("results/portgen.json").write_text(json.dumps(log, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
