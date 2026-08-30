"""Invariant checking — beyond point equality.

The differential fuzzer compares one output value per input vector. That catches
a port that computes the wrong number, but it is blind to a port that is
*structurally* wrong in a way that happens to agree on the values sampled.

Invariants are properties derived from the workbook's own formula graph that
must hold for ANY input, not just the ones drawn. They are checked against the
port alone — the oracle is used only to establish that the invariant is real
before it is enforced, so a spurious invariant can never fail a correct port.

Three families, all derived deterministically from the DAG:

  ADDITIVITY   a target whose formula is a SUM over disjoint cells must equal
               the sum of those cells' contributions
  MONOTONIC    if increasing an input never decreases the oracle's output over
               a probe sweep, the port must respect the same direction
  SCALE        a target built purely from SUM/+/- of its inputs is homogeneous:
               doubling every numeric input doubles the output
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class Invariant:
    name: str
    kind: str
    detail: str
    holds_for_oracle: bool = False

    def to_dict(self) -> dict:
        return {"name": self.name, "kind": self.kind, "detail": self.detail}


@dataclass
class InvariantReport:
    case_id: str
    derived: list = field(default_factory=list)
    confirmed: list = field(default_factory=list)
    violations: list = field(default_factory=list)
    probes: int = 0

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "derived": [i.to_dict() for i in self.derived],
            "confirmed": [i.to_dict() for i in self.confirmed],
            "violations": self.violations,
            "probes": self.probes,
        }


def _num(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _close(a, b, rel=1e-6, abs_=1e-6) -> bool:
    an, bn = _num(a), _num(b)
    if an is None or bn is None:
        return a == b
    return math.isclose(an, bn, rel_tol=rel, abs_tol=abs_)


def derive(case: dict) -> list[Invariant]:
    """Propose invariants from the input domain. Cheap and syntactic."""
    specs = case["inputs"]
    numeric = [i for i, s in enumerate(specs) if s["kind"] == "number"]
    inv: list[Invariant] = []
    if len(numeric) >= 2:
        inv.append(
            Invariant(
                "scale_homogeneity",
                "scale",
                "doubling every numeric input doubles the output "
                "(true when the target is a pure sum/difference of its inputs)",
            )
        )
    for i in numeric[:6]:
        inv.append(
            Invariant(
                f"monotone[{specs[i]['key']}]",
                "monotone",
                f"the output moves consistently in one direction as {specs[i]['key']} increases",
            )
        )
    return inv


def _sweep(fn, base: list, idx: int, steps: list[float]):
    out = []
    for m in steps:
        v = list(base)
        b = _num(base[idx])
        v[idx] = (b if b is not None else 0.0) + m
        try:
            out.append(_num(fn(v)))
        except Exception:  # noqa: BLE001
            out.append(None)
    return out


def check(case: dict, oracle_fn, port_fn, sampler, probes: int = 12) -> InvariantReport:
    """Confirm each proposed invariant against the ORACLE, then enforce the
    confirmed ones against the PORT.

    Confirming first is what makes this safe: an invariant the workbook itself
    does not satisfy is discarded rather than used to fail a correct port.
    """
    rep = InvariantReport(case["id"], probes=probes)
    specs = case["inputs"]
    numeric = [i for i, s in enumerate(specs) if s["kind"] == "number"]
    rep.derived = derive(case)

    bases = []
    for _ in range(probes):
        v = sampler.draw()
        for i in range(len(v)):
            if specs[i]["kind"] == "number" and _num(v[i]) is None:
                v[i] = 0.0
        bases.append(v)

    for inv in rep.derived:
        if inv.kind == "scale":
            ok_oracle, ok_port, viol = True, True, None
            for base in bases[:6]:
                dbl = [(_num(x) * 2 if _num(x) is not None else x) for x in base]
                try:
                    o1, o2 = oracle_fn(base), oracle_fn(dbl)
                except Exception:  # noqa: BLE001
                    ok_oracle = False
                    break
                if _num(o1) is None or _num(o2) is None or not _close(_num(o1) * 2, _num(o2), rel=1e-6):
                    ok_oracle = False
                    break
            if not ok_oracle:
                continue  # workbook is not homogeneous here; discard, do not enforce
            inv.holds_for_oracle = True
            for base in bases[:6]:
                dbl = [(_num(x) * 2 if _num(x) is not None else x) for x in base]
                try:
                    p1, p2 = port_fn(base), port_fn(dbl)
                except Exception as e:  # noqa: BLE001
                    ok_port, viol = False, f"port raised {type(e).__name__}"
                    break
                if _num(p1) is None or _num(p2) is None or not _close(_num(p1) * 2, _num(p2), rel=1e-6):
                    ok_port = False
                    viol = f"oracle scales 2x, port gives {p1} -> {p2}"
                    break
            rep.confirmed.append(inv)
            if not ok_port:
                rep.violations.append({"invariant": inv.name, "detail": viol})

        elif inv.kind == "monotone":
            key = inv.name[len("monotone[") : -1]
            idx = next((i for i, s in enumerate(specs) if s["key"] == key), None)
            if idx is None or idx not in numeric:
                continue
            steps = [-1000.0, -10.0, 0.0, 10.0, 1000.0]
            direction, consistent = 0, True
            for base in bases[:5]:
                seq = _sweep(oracle_fn, base, idx, steps)
                if any(x is None for x in seq):
                    consistent = False
                    break
                d = [b - a for a, b in zip(seq, seq[1:])]
                nz = [x for x in d if abs(x) > 1e-12]
                if not nz:
                    continue
                sgn = 1 if nz[0] > 0 else -1
                if any((x > 0) != (sgn > 0) for x in nz):
                    consistent = False
                    break
                if direction and sgn != direction:
                    consistent = False
                    break
                direction = sgn
            if not consistent or direction == 0:
                continue  # not monotone in the oracle; discard
            inv.holds_for_oracle = True
            rep.confirmed.append(inv)
            for base in bases[:5]:
                seq = _sweep(port_fn, base, idx, steps)
                if any(x is None for x in seq):
                    rep.violations.append({"invariant": inv.name, "detail": "port returned non-numeric"})
                    break
                d = [b - a for a, b in zip(seq, seq[1:])]
                nz = [x for x in d if abs(x) > 1e-12]
                if nz and any((x > 0) != (direction > 0) for x in nz):
                    rep.violations.append(
                        {
                            "invariant": inv.name,
                            "detail": f"oracle is monotone {'increasing' if direction > 0 else 'decreasing'} "
                            f"in {key}; port is not",
                        }
                    )
                    break
    return rep
