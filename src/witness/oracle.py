"""The acceptance oracle: the workbook itself.

Wraps the pure-Python recalculation engine so a caller can push an input vector
in and read one target cell out. This is the half of the differential test that
is *not* under the agent's control, and the engine-trust gate has already shown
it reproduces Excel's own cached values on this corpus.
"""

from __future__ import annotations

import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
os.environ.setdefault("TQDM_DISABLE", "1")


def cell_key(workbook: str | Path, ref: str) -> str:
    """formulas addresses cells as '[filename]SHEETNAME'!COORD — the filename
    keeps its original case, the sheet name is upper-cased. Getting this wrong
    yields a silent KeyError rather than a wrong answer, which is at least
    honest, but it cost an hour to find."""
    book = Path(workbook).name
    sheet, coord = ref.split("!", 1)
    return f"'[{book}]{sheet.upper()}'!{coord.replace('$', '').upper()}"


_ORACLE_CACHE: dict[str, "WorkbookOracle"] = {}


def get_oracle(path: str | Path) -> "WorkbookOracle":
    """Compile each workbook at most once per process.

    Building the model for a large workbook costs seconds, and a single workbook
    supplies many cases. Rebuilding it per case turned a 6-minute evaluation into
    a multi-hour one — the fuzzing itself is ~1 ms per vector.
    """
    k = str(path)
    if k not in _ORACLE_CACHE:
        _ORACLE_CACHE[k] = WorkbookOracle(path)
    return _ORACLE_CACHE[k]


class WorkbookOracle:
    """Compile once, evaluate many times."""

    def __init__(self, path: str | Path):
        import formulas

        self.path = str(path)
        self.model = formulas.ExcelModel().loads(self.path).finish()
        self._base = None

    def baseline_solution(self) -> dict:
        if self._base is None:
            self._base = {k.upper(): v for k, v in self.model.calculate().items()}
        return self._base

    def evaluate(self, inputs: dict[str, object], target: str):
        """inputs: {cell_ref: value} using 'Sheet!A1' refs. Returns target value."""
        payload = {cell_key(self.path, r): v for r, v in inputs.items()}
        tkey = cell_key(self.path, target)
        sol = self.model.calculate(inputs=payload)
        norm = {k.upper(): v for k, v in sol.items()}
        return unwrap(norm.get(tkey.upper()))

    def compile_case(self, input_refs: list[str], target: str):
        """Prune the model to the dependency cone of one target cell.

        Recalculating a whole workbook per input vector costs ~466 ms, which
        puts 10,000 trials at 78 minutes for a single case. Shrinking to just
        the cone behind the target drops it to ~17 ms — 28x — and that is the
        only reason pass^10000 is affordable rather than aspirational.

        Returns (fn, n_nodes) where fn(list_of_values) -> target value.
        """
        import schedula as sh

        ik = [cell_key(self.path, r) for r in input_refs]
        tk = cell_key(self.path, target)
        sub = self.model.dsp.shrink_dsp(inputs=ik, outputs=[tk])
        if not len(sub.nodes):
            raise ValueError(f"empty dependency cone for {target}")
        pipe = sh.DispatchPipe(sub, function_id="case", inputs=ik, outputs=[tk])

        def fn(values: list):
            out = pipe(*values)
            if isinstance(out, (list, tuple)):
                out = out[0] if out else None
            return unwrap(out)

        return fn, len(sub.nodes)


def unwrap(v):
    """formulas returns numpy arrays and Range objects; reduce to a scalar."""
    import numpy as np

    if v is None:
        return None
    if isinstance(v, np.ndarray):
        if v.size == 0:
            return None
        v = v.flatten()[0]
    if hasattr(v, "value"):
        inner = v.value
        if isinstance(inner, np.ndarray):
            inner = inner.flatten()[0] if inner.size else None
        v = inner
    if isinstance(v, np.generic):
        v = v.item()
    return v
