"""pytest integration — Witness as a CI gate, not a demo.

The point of shipping this is that a spreadsheet port stops being a one-off
migration project and becomes a test that runs on every commit. Owen does not
want a report; he wants CI to go red when someone changes the port and it stops
matching the workbook.

Usage in a user's own test suite:

    from witness.pytest_plugin import certify_equivalent
    from mycompany.finance import quarterly_revenue

    test_revenue = certify_equivalent(
        workbook="books/close_q3.xlsx",
        target="Revenue!R20",
        port=quarterly_revenue,
        trials=10_000,
    )

or as a decorator over a function that *is* the port:

    @certify_equivalent(workbook="books/close_q3.xlsx", target="Revenue!R20")
    def quarterly_revenue(inputs: dict) -> float:
        ...

Either form produces a normal pytest test. On failure the assertion message is
the shrunk counterexample — the minimal input vector, both values, and the
delta — not a stack trace.
"""

from __future__ import annotations

from pathlib import Path

from witness import dag as D
from witness.fuzz import fuzz_case
from witness.oracle import WorkbookOracle

__all__ = ["certify_equivalent", "build_case", "CertificationError"]


class CertificationError(AssertionError):
    """Raised when a port disagrees with its workbook."""


def build_case(workbook: str | Path, target: str, max_inputs: int = 60) -> dict:
    """Derive the input domain for one target cell, deterministically."""
    g = D.build(Path(workbook))
    sl = D.slice_for_output(g, target, max_inputs=max_inputs)
    if not sl["inputs"]:
        raise ValueError(f"{target}: no free inputs found in {workbook}")
    if sl["nondeterministic"]:
        raise ValueError(
            f"{target} depends on volatile functions {sl['nondeterministic'][:3]}; "
            "it cannot have a stable oracle and cannot be certified."
        )
    return {
        "id": f"{Path(workbook).stem}::{target}",
        "workbook": str(workbook),
        "target": target,
        "formula_nodes": sl["formula_nodes"],
        "inputs": [i.to_dict() for i in sl["inputs"]],
    }


def _run(workbook, target, port, trials, seeds, max_inputs):
    case = build_case(workbook, target, max_inputs=max_inputs)
    refs = [s["key"] for s in case["inputs"]]
    oracle = WorkbookOracle(workbook)
    oracle_fn, nodes = oracle.compile_case(refs, target)

    def port_fn(values: list):
        return port({refs[i]: values[i] for i in range(len(refs))})

    for seed in seeds:
        r = fuzz_case(case, oracle_fn, port_fn, trials=trials, seed=seed)
        if r.certified:
            continue
        d = r.disagreement
        if d is None:
            raise CertificationError(
                f"{target}: no disagreement recorded but not certified "
                f"({r.agreed}/{r.trials_run} agreed, {r.oracle_exceptions} oracle errors)"
            )
        lines = [
            "",
            f"  Port does not match {Path(workbook).name} at {target}.",
            f"  Seed {seed}, first disagreement at trial {d.trial:,} of {trials:,}.",
            f"  {nodes} formula nodes behind this cell, {len(refs)} free inputs.",
            "",
            f"    Excel returned : {d.expected!r}",
            f"    Your port      : {d.actual!r}",
        ]
        if d.delta is not None:
            lines.append(f"    Difference     : {d.delta:,.6g}")
        lines += [
            f"    Minimal inputs : {d.minimal_change}",
            "",
            "  Smallest failing input vector:",
        ]
        for k, v in list(d.vector.items())[:25]:
            lines.append(f"    {k} = {v!r}")
        if len(d.vector) > 25:
            lines.append(f"    ... and {len(d.vector) - 25} more")
        lines.append("")
        raise CertificationError("\n".join(lines))
    return True


def certify_equivalent(
    workbook: str | Path,
    target: str,
    port=None,
    trials: int = 10_000,
    seeds=(11, 23, 47),
    max_inputs: int = 60,
):
    """Build a pytest test asserting a port matches its workbook.

    Call with `port=` to get a test function back; use without `port=` as a
    decorator over the port itself.
    """
    if port is not None:
        def test(_p=port):
            return _run(workbook, target, _p, trials, seeds, max_inputs)

        test.__name__ = f"test_certify_{Path(str(workbook)).stem}_{target}".replace(
            "!", "_"
        ).replace(" ", "_").replace("-", "_")
        test.__doc__ = (
            f"Witness: {Path(str(workbook)).name} {target} — "
            f"{trials:,} fuzzed vectors x {len(seeds)} seeds."
        )
        return test

    def decorator(fn):
        fn._witness_test = certify_equivalent(
            workbook, target, port=fn, trials=trials, seeds=seeds, max_inputs=max_inputs
        )
        return fn

    return decorator
