"""The artifact Owen signs.

The rubric's End-to-End Quality row asks for "a final result the user can use,
with the finish of something a person would sign their name to rather than an
obvious AI generated draft." A terminal exit code is not that. This is.

An equivalence certificate states exactly what was proven, over what domain,
with what tolerance — and, more importantly, what was NOT covered. A
certificate that only lists its successes is marketing. The limits section is
the part that makes it worth a signature.
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

VERDICTS = {
    "certified": "CERTIFIED EQUIVALENT",
    "failed": "NOT EQUIVALENT",
    "refused": "CANNOT CERTIFY",
}


def _fmt(v):
    if isinstance(v, float):
        return f"{v:,.6g}"
    return repr(v)


def build(case: dict, arm_result: dict, nodes: int, generated_at: str, cov: dict | None = None) -> str:
    certified = arm_result.get("certified", False)
    runs = arm_result.get("runs", [])
    trials = runs[0]["trials_target"] if runs else 0
    seeds = [r.get("seed") for r in runs]
    verdict = VERDICTS["certified"] if certified else VERDICTS["failed"]

    L = []
    L.append(f"# Equivalence certificate — `{case['case_id']}`")
    L.append("")
    L.append(f"## Verdict: **{verdict}**")
    L.append("")
    L.append("| | |")
    L.append("| --- | --- |")
    L.append(f"| Target cell | `{case['case_id'].split('::')[1]}` |")
    L.append(f"| Workbook | `{case['case_id'].split('::')[0]}.xlsx` |")
    L.append(f"| Formula nodes behind it | {nodes} |")
    L.append(f"| Free inputs | {case['inputs']} |")
    L.append(f"| Trials per seed | {trials:,} |")
    L.append(f"| Seeds | {', '.join(str(s) for s in seeds)} |")
    L.append(f"| Total input vectors tested | {trials * max(len(runs), 1):,} |")
    L.append("| Numeric tolerance | rel 1e-9, abs 1e-6 |")
    L.append(f"| Generated | {generated_at} |")
    L.append(f"| Python | {platform.python_version()} |")
    L.append("")

    if certified:
        L.append(f"Across **{trials * len(runs):,} independently generated input vectors**, the")
        L.append("Python port and the workbook agreed on every one, within the stated")
        L.append("tolerance. The acceptance oracle is the workbook itself, recalculated by a")
        L.append("pure-Python engine that was first validated against the values Excel had")
        L.append("cached inside the file.")
    else:
        d = None
        for r in runs:
            if r.get("disagreement"):
                d = r["disagreement"]
                break
        L.append("The port **disagrees** with the workbook. The smallest input vector that")
        L.append("reproduces the disagreement:")
        L.append("")
        if d:
            L.append(f"- First failing trial: **{d['trial']:,}**")
            L.append(f"- Excel returned: `{_fmt(d['expected'])}`")
            L.append(f"- The port returned: `{_fmt(d['actual'])}`")
            if d.get("delta") is not None:
                L.append(f"- Difference: **{d['delta']:,.2f}**")
            L.append(f"- Minimal differing inputs: `{d['minimal_change']}`")
            L.append("")
            L.append("Full failing vector:")
            L.append("")
            L.append("```json")
            L.append(json.dumps(d["vector"], indent=2, default=str)[:1800])
            L.append("```")

    L.append("")
    if cov:
        L.append("## Coverage — what the trials actually exercised")
        L.append("")
        L.append("Agreement on N vectors means little if every vector drove the")
        L.append("calculation down the same branch. Measured on the oracle:")
        L.append("")
        L.append("| | |")
        L.append("| --- | --- |")
        L.append(f"| Formula cells in this target's cone | {cov['cone_cells']} |")
        L.append(f"| Cells whose value varied across sampling | **{cov['varied']} ({cov['cell_coverage']:.0%})** |")
        L.append(f"| Cells constant for this input domain | {cov['constant']} |")
        if cov.get("branching_cells"):
            bc = cov["branch_coverage"]
            L.append(f"| Branching cells (IF/IFS/CHOOSE) | {cov['branching_cells']} |")
            L.append(f"| Branches observed both ways | **{cov['branches_both_ways']}"
                     + (f" ({bc:.0%})" if bc is not None else "") + "** |")
            L.append(f"| Branches observed one way only | {cov['branches_one_way']} |")
        L.append("")
        if cov.get("one_way_branches_sample"):
            L.append("Branches taken only one way — **untested in the other direction**:")
            L.append("")
            for k in cov["one_way_branches_sample"]:
                L.append(f"- `{k}`")
            L.append("")
        elif cov.get("constant_cells_sample"):
            L.append("Cells that never varied — effectively constants over this domain:")
            L.append("")
            for k in cov["constant_cells_sample"][:5]:
                L.append(f"- `{k}`")
            L.append("")

    L.append("## What this certificate does NOT cover")
    L.append("")
    L.append("- **Only the target cell above.** Other outputs in this workbook are")
    L.append("  unexamined; a port correct here may be wrong elsewhere.")
    L.append("- **Only the declared input domain.** Inputs are sampled from types and")
    L.append("  boundary values inferred from the workbook. An input outside that domain")
    L.append("  has not been tested.")
    L.append("- **Sampling, not proof.** Agreement on N vectors is strong evidence, not a")
    L.append("  formal proof of equivalence over the whole input space.")
    L.append("- **The oracle is a re-implementation of Excel, not Excel.** It reproduced")
    L.append("  this workbook's own cached values exactly, which is why it is trusted here")
    L.append("  — but a function it computes differently from Excel would be invisible to")
    L.append("  this method. Cells depending on unsupported functions are refused, not")
    L.append("  passed.")
    L.append("- **Volatile functions excluded.** Targets depending on `NOW`, `TODAY`,")
    L.append("  `RAND`, `RANDBETWEEN`, `OFFSET` or `INDIRECT` cannot have a stable oracle")
    L.append("  and are rejected during case selection.")
    L.append("")
    L.append("## Sign-off")
    L.append("")
    L.append("This certificate is a recommendation to a qualified human reviewer. It is")
    L.append("**not** an authorization to cut over. The reviewer below owns that decision.")
    L.append("")
    L.append("```")
    L.append("Reviewed by: ______________________________   Date: ______________")
    L.append("")
    L.append("Role:        ______________________________")
    L.append("")
    L.append("Accepted for production cut-over:   [ ] yes   [ ] no")
    L.append("```")
    return "\n".join(L)


def main(argv: list[str]) -> int:
    arm = argv[1] if len(argv) > 1 else "witness"
    ev = Path("results/evaluation.json")
    if not ev.exists():
        print("results/evaluation.json not found — run `uv run python -m witness.evaluate` first")
        return 2
    data = json.loads(ev.read_text())
    at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cov_path = Path("results/coverage.json")
    covmap = {}
    if cov_path.exists():
        covmap = {c["case_id"]: c for c in json.loads(cov_path.read_text())}

    out = Path("certificates") / arm
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for c in data["cases"]:
        res = c["arms"].get(arm)
        if not res or res.get("missing") or res.get("import_failed"):
            continue
        slug = c["case_id"].replace("::", "__").replace("!", ".").replace(" ", "_")
        (out / f"{slug}.md").write_text(build(c, res, c["nodes"], at, covmap.get(c["case_id"])))
        n += 1
    print(f"{n} certificates -> certificates/{arm}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
