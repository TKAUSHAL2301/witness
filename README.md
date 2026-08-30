# Witness

**An acceptance oracle for spreadsheet-to-code migrations.**

Witness ports a finance team's Excel workbook to Python and then refuses to
certify the port until 10,000 differentially fuzzed input vectors agree — after
first proving its own recalculation engine can reproduce the values Excel itself
cached inside the file. The acceptance oracle is the spreadsheet. Never a model.

---

## The team

**`<YOUR NAME>`** — solo entrant. One person, all four deliverables.

<!-- TODO: replace with your real name, role, and one line of relevant background.
     Ground Rule 02 means this should be honest about what you brought with you. -->

I entered as an individual under the August 2026 edition's one-person rule. Every
line of `src/` and every evaluation case in this repository was written after
kickoff; everything I did not write is declared in
[PRIOR-WORK.md](PRIOR-WORK.md). The coding agents I used and the trajectories
they produced are disclosed in [AGENTS.md](AGENTS.md).

---

## Who has this problem

**Owen Castellanos, FP&A controller at a 180-person B2B SaaS company.**

His quarterly revenue-recognition and sales-commission workbook — 11 tabs,
roughly 2,300 formulas — is being moved into the data warehouse by one
contractor. Owen has to personally sign that the Python matches the spreadsheet
before the first quarter closes on it. He is not a programmer. He is the person
whose name is on the number.

## What bottleneck makes it worth solving

**Nobody can prove a port is right.** The universal industry practice is _"tie
out three historical quarters and hope."_

That practice is structurally broken, and the reason is subtle: historical
inputs are a measure-zero slice of the input space, and they are precisely the
slice the bug already avoided. Divergences hide where historical data never went:

| Failure family           | What Excel does                           | What naive Python does              |
| ------------------------ | ----------------------------------------- | ----------------------------------- |
| Blank vs. zero           | `""` propagates through `SUM` as skip     | `None` raises or coerces to `0`     |
| Rounding                 | `ROUND` is half-away-from-zero            | Python `round` is banker's rounding |
| Text in a numeric column | Coerced to `0` inside `SUM`               | `TypeError`, or silently dropped    |
| Tier boundaries          | `VLOOKUP(..., TRUE)` on an unsorted table | Exact match, or a different tier    |
| Negative inputs          | Often a different branch                  | Untested path                       |

These surface six months later as a restated quarter and a very bad board
meeting. The cost is not developer time. It is a financial restatement.

---

## Architecture

The design thesis in one line: **do not verify the translator — verify each
individual translation, over the input domain.** That is _translation
validation_, borrowed from compiler verification (Pnueli, 1998). The field is
full of agents that write code. Almost nobody builds the thing that decides
whether written code may be trusted.

```
                          ┌───────────────────────────────┐
   workbook.xlsx  ───────▶│  0 · ENGINE-TRUST GATE        │  ✅ 12/12 workbooks
                          │    recalc every formula cell  │     36,500 cells
                          │    vs Excel's OWN cached      │     0 disagreements
                          │    values. Fail ⇒ refuse.     │
                          └───────────────┬───────────────┘
                                          │ engine is trustworthy for this file
                                          ▼
                          ┌───────────────────────────────┐
                          │  1 · FORMULA-DAG EXTRACTOR    │   deterministic,
                          │    openpyxl. Separates true   │   NO model involved
                          │    inputs from derived cells; │
                          │    finds outputs; types each  │
                          │    input's domain.            │
                          └───────────────┬───────────────┘
                                          │ typed input domain + topology
                                          ▼
                          ┌───────────────────────────────┐
                          │  2 · PER-BLOCK TRANSLATION    │   ◀── the only
                          │    one strongly-connected     │       LLM step
                          │    block at a time, never the │
                          │    whole 2,300-formula sheet  │
                          └───────────────┬───────────────┘
                                          │ candidate port.py
                                          ▼
        ┌─────────────────────────────────────────────────────────┐
        │  3 · DIFFERENTIAL FUZZER      ← this component IS the   │
        │      metric, not a check on it                          │
        │                                                         │
        │   hypothesis generates a vector from the typed domain   │
        │        │                                                │
        │        ├──▶ formulas engine runs the .xlsx    ──┐       │
        │        └──▶ generated Python runs the port    ──┤       │
        │                                                 ▼       │
        │                                        compare, tolerance│
        └───────────────┬─────────────────────────────────┬───────┘
                    agree │                               │ DISAGREE
                          │                               ▼
                          │              ┌────────────────────────────┐
                          │              │  4 · SHRINK                │
                          │              │   minimise to the smallest │
                          │              │   failing input            │
                          │              └────────────┬───────────────┘
                          │                           │
                          │      ┌────────────────────┘
                          │      │  ONLY the shrunk counterexample
                          │      │  is fed back — never the fuzzer's
                          │      │  prose explanation of it.
                          │      └──────────▶ back to step 2
                          ▼
              ┌───────────────────────────────────┐
              │  5 · INVARIANT LAYER              │  beyond point equality:
              │     monotonicity, totals = Σparts │  catches bug families a
              │     derived from the DAG          │  vector comparison misses
              └───────────────┬───────────────────┘
                              ▼
              ┌───────────────────────────────────┐
              │  6 · REFUSAL GATE                 │  any output cell depending
              │     unsupported Excel function    │  on an unsupported function
              │     ⇒ CANNOT CERTIFY              │  ⇒ never marked GREEN
              └───────────────┬───────────────────┘
                              ▼
              ┌───────────────────────────────────┐
              │  7 · EQUIVALENCE.md CERTIFICATE   │  trials, seed, declared
              │     ── Owen signs this ──         │  domain, tolerance, residual
              │     incl. "what is NOT covered"   │  disagreements, and the
              └───────────────────────────────────┘  explicit coverage limits
```

### Why each component earns its place

Every row below becomes one entry in the Improvement Changelog, tied to the
number it moved. A component with no number is decoration and gets deleted.

| #   | Component                                       | Why it exists                                                                                                                                                   |
| --- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0   | Engine-trust gate                               | Without it the oracle could be silently wrong, and every number downstream is worthless. **Already executed: 12/12, 36,500 cells, 0 disagreements.**            |
| 1   | Formula-DAG extractor                           | Deterministic. Porting a _derived_ cell as an _input_ is a whole failure family the model cannot see and the DAG cannot miss.                                   |
| 2   | Per-block translation                           | 2,300 formulas in one context window degrades badly. Blocks also cut cost per workbook.                                                                         |
| 3   | Differential fuzzer                             | Converts "looks right" into a counterexample. This is the measurement, not a check on it.                                                                       |
| 4   | Shrunk counterexample as the only repair signal | Tests the claim that a _minimal failing input_ repairs better than a critic's narrative. The ablation feeding prose instead is a planned REMOVED changelog row. |
| 5   | Invariant layer                                 | Point equality on sampled vectors misses structural bugs; invariants derived from the DAG catch them.                                                           |
| 6   | Refusal gate                                    | Ground Rules 04/05. Unsupported function ⇒ escalate, never a silent pass.                                                                                       |
| 7   | Signed certificate                              | Ground Rule 05 and the End-to-End Quality row: a human owns the decision, and the artifact says what it does _not_ cover.                                       |

---

## Does the agent solve it well

**Primary metric: certified-equivalence rate at 10,000 fuzzed vectors —
`pass^10000`, not `pass@15`.**

Ground truth is free and unbounded because _the workbook is the oracle_. Every
generated input vector is a labelled case. No rubric, no LLM judge, no
inter-annotator agreement, and — critically — **no step where I decided what the
right answer was.**

The baseline is a general-purpose agent with file and Python tools, told: _"port
this workbook to Python and make sure it is correct."_ It spot-checks a few
historical rows and declares victory — which is exactly the real-world practice
it is meant to represent. Same workbooks, same fuzzer, same tolerance, same
scorer.

## Can another person reproduce the result

Three commands, no Docker, no database, no network at judge time. All 14
workbooks are vendored into `corpus/`.

```bash
git clone <repo> && cd witness
uv sync
uv run python -m witness.gate corpus     # the engine-trust gate
```

Current output, reproducible from a clean checkout:

```
GATE: 12/14 workbooks reproduce their own cached values
usable workbooks (had cached formula values): 12
total formula cells compared: 36500
total disagreements: 0
```

The two excluded workbooks carry no cached formula values at all — they were
saved without calculation, so there is nothing to validate the engine against.
That is a property of those files, not an engine failure, and the exclusion is a
**disclosed case-selection criterion**, not a hidden filter.

---

## Result

Command: `uv run python -m witness.evaluate 10000` · Raw: `results/evaluation.json`

| METRIC | SIMPLE BASELINE | AGENT SOLUTION | CHANGE |
| --- | --- | --- | --- |
| **Certified-equivalence rate** (`pass^10000`, all 3 seeds) | **40%** | **80%** | **+40 pp** |
| Ports certified | 4 / 10 | 8 / 10 | +4 |
| Largest undetected error in a self-certified baseline port | **$50,951** | — | — |
| Human time to verify one port | ~2–4 h manual tie-out | ~3 min automated | ~40–80× |

Paired: **5 Witness wins, 1 loss, 3 both-certified, 1 both-failed.** McNemar
exact two-sided **p = 0.219 — not significant at α = 0.05.** The direction is
consistent and the effect large, but ten cases is underpowered to establish it,
and saying otherwise would be overclaiming.

Every one of those four baseline ports had **self-certified as correct** before
the fuzzer touched it. That is the entire thesis in one line.

Verified from a clean clone (`git clone` → `uv sync` → run): identical numbers.

Full evolution, removed experiments, the null-result ablation, and the failure
analysis: [CHANGELOG.md](CHANGELOG.md).

---

## Status


| Stage                     | State                                                  |
| ------------------------- | ------------------------------------------------------ |
| 0 · Engine-trust gate     | ✅ **Executed — 12/12, 36,500 cells, 0 disagreements** |
| 1 · Formula-DAG extractor | ⬜                                                     |
| 2 · Per-block translation | ⬜                                                     |
| 3 · Differential fuzzer   | ⬜                                                     |
| 4 · Shrink + repair loop  | ⬜                                                     |
| 5 · Invariant layer       | ⬜                                                     |
| 6 · Refusal gate          | ⬜                                                     |
| 7 · Certificate           | ⬜                                                     |

Data: 14 municipal finance workbooks published by the Commonwealth of
Massachusetts, Division of Local Services. Public records. Provenance and
licences in [PRIOR-WORK.md](PRIOR-WORK.md).
