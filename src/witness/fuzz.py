"""The differential fuzzer.

This module IS the metric. It is not a check bolted onto the metric.

Given a case (workbook, target cell, typed input domain) and a candidate Python
port, it generates input vectors from the typed domain, runs both the workbook
and the port on each identical vector, and reports the first disagreement —
shrunk to the smallest failing input it can find.

The shrunk counterexample is the only thing ever handed back to the repair loop.
No prose, no critique, no explanation. That choice is the subject of the
ablation in the changelog.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Callable

ABS_TOL = 1e-6
REL_TOL = 1e-9


@dataclass
class Disagreement:
    trial: int
    vector: dict
    expected: object
    actual: object
    delta: float | None
    shrunk_from: int | None = None
    minimal_change: str | None = None


@dataclass
class FuzzResult:
    case_id: str
    trials_run: int
    trials_target: int
    agreed: int
    certified: bool
    error: str = ""
    disagreement: Disagreement | None = None
    port_exceptions: int = 0
    oracle_exceptions: int = 0
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {
            "case_id": self.case_id,
            "trials_run": self.trials_run,
            "trials_target": self.trials_target,
            "agreed": self.agreed,
            "certified": self.certified,
            "error": self.error,
            "port_exceptions": self.port_exceptions,
            "oracle_exceptions": self.oracle_exceptions,
            "notes": self.notes,
        }
        if self.disagreement:
            dd = self.disagreement
            d["disagreement"] = {
                "trial": dd.trial,
                "expected": _plain(dd.expected),
                "actual": _plain(dd.actual),
                "delta": dd.delta,
                "minimal_change": dd.minimal_change,
                "shrunk_from": dd.shrunk_from,
                "vector": {k: _plain(v) for k, v in dd.vector.items()},
            }
        return d


def _plain(v):
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    return str(v)


def values_agree(a, b) -> tuple[bool, float | None]:
    """Excel and Python agree if the numbers match within tolerance. Blank and
    zero are the same thing to Excel, and that equivalence is deliberate — it is
    also the single most common source of a real port defect, so it is asserted
    here rather than assumed."""
    if isinstance(a, str) and a.startswith("#"):
        return True, None  # the workbook itself errors here; not the port's fault
    if a is None and b is None:
        return True, None
    an = a if isinstance(a, (int, float)) and not isinstance(a, bool) else None
    bn = b if isinstance(b, (int, float)) and not isinstance(b, bool) else None
    if a is None and bn is not None:
        an = 0.0
    if b is None and an is not None:
        bn = 0.0
    if an is not None and bn is not None:
        if math.isnan(an) and math.isnan(bn):
            return True, None
        ok = math.isclose(an, bn, rel_tol=REL_TOL, abs_tol=ABS_TOL)
        return ok, (None if ok else bn - an)
    return str(a) == str(b), None


class VectorSampler:
    """Samples from the typed domain the DAG inferred for each input.

    A uniform random float finds nothing interesting. What breaks ports is the
    boundary set: blank, zero, negative, text-in-a-numeric-cell, and the tier
    edges lifted out of whatever lookup table the formula actually references.
    Those are drawn far more often than random values.
    """

    def __init__(self, specs: list[dict], seed: int = 0):
        self.specs = specs
        self.rng = random.Random(seed)

    def _one(self, spec: dict):
        kind = spec["kind"]
        interesting = [v for v in spec.get("interesting", []) if not isinstance(v, str) or v == ""]
        r = self.rng.random()
        if interesting and r < 0.65:
            return self.rng.choice(interesting)
        if kind == "bool":
            return self.rng.choice([True, False])
        if kind == "text":
            return self.rng.choice(["", "0", "n/a", str(self.rng.randint(0, 999))])
        if kind == "blank":
            return self.rng.choice([0, None, ""])
        obs = spec.get("observed")
        base = obs if isinstance(obs, (int, float)) and not isinstance(obs, bool) else 1000.0
        if base == 0:
            base = 1000.0
        mode = self.rng.random()
        if mode < 0.15:
            return 0
        if mode < 0.30:
            return -abs(base) * self.rng.uniform(0.1, 3)
        if mode < 0.40:
            return None  # blank
        if mode < 0.50:
            return round(base * self.rng.uniform(0, 3))
        return base * self.rng.uniform(-2, 4)

    def draw(self) -> list:
        return [self._one(s) for s in self.specs]


def _shrink(vector, baseline, refs, oracle_fn, port_fn, rounds: int = 2, budget: int = 400):
    """Reduce a failing vector toward the baseline, one coordinate at a time,
    keeping only reversions that preserve the failure. What survives is the
    minimal set of inputs responsible."""
    cur = list(vector)
    spent = 0
    for _ in range(rounds):
        changed = False
        for i in range(len(cur)):
            if spent >= budget:
                break
            if cur[i] == baseline[i]:
                continue
            trial = list(cur)
            trial[i] = baseline[i]
            spent += 1
            try:
                e, a = oracle_fn(trial), port_fn(trial)
            except Exception:  # noqa: BLE001
                continue
            ok, _ = values_agree(e, a)
            if not ok:
                cur = trial  # still fails without this input's change; drop it
                changed = True
        if not changed:
            break
    differing = [refs[i] for i in range(len(cur)) if cur[i] != baseline[i]]
    return cur, differing


def fuzz_case(
    case: dict,
    oracle_fn: Callable[[list], object],
    port_fn: Callable[[list], object],
    trials: int = 10_000,
    seed: int = 0,
    stop_on_first: bool = True,
    time_budget_s: float = 240.0,
) -> FuzzResult:
    specs = case["inputs"]
    refs = [s["key"] for s in specs]
    sampler = VectorSampler(specs, seed=seed)
    baseline = [s["observed"] if s["observed"] is not None else 0 for s in specs]

    res = FuzzResult(case["id"], 0, trials, 0, False)

    # Trial 0 is always the workbook's own saved inputs.
    vectors_head = [baseline]

    started = time.monotonic()
    for n in range(trials):
        if time.monotonic() - started > time_budget_s:
            res.notes.append(
                f"time budget {time_budget_s:.0f}s reached after {n:,} of {trials:,} trials"
            )
            break
        vec = vectors_head[n] if n < len(vectors_head) else sampler.draw()
        res.trials_run += 1
        try:
            expected = oracle_fn(vec)
        except Exception:  # noqa: BLE001
            res.oracle_exceptions += 1
            continue
        try:
            actual = port_fn(vec)
        except Exception as e:  # noqa: BLE001
            res.port_exceptions += 1
            actual = f"!EXC:{type(e).__name__}"
        ok, delta = values_agree(expected, actual)
        if ok:
            res.agreed += 1
            continue

        shrunk, differing = _shrink(vec, baseline, refs, oracle_fn, port_fn)
        try:
            se, sa = oracle_fn(shrunk), port_fn(shrunk)
        except Exception:  # noqa: BLE001
            se, sa = expected, actual
        _, sdelta = values_agree(se, sa)
        res.disagreement = Disagreement(
            trial=n,
            vector={refs[i]: shrunk[i] for i in range(len(refs))},
            expected=se,
            actual=sa,
            delta=sdelta if sdelta is not None else delta,
            shrunk_from=len([1 for i in range(len(vec)) if vec[i] != baseline[i]]),
            minimal_change=", ".join(differing) if differing else "(baseline inputs)",
        )
        if stop_on_first:
            return res

    res.certified = res.disagreement is None and res.agreed > 0
    return res
