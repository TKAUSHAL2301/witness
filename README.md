# Witness

**An acceptance oracle for spreadsheet-to-code migrations.**

Witness ports a finance team's Excel workbook to Python and then refuses to
certify the port until **9,000 differentially fuzzed input vectors** agree —
after first proving its own recalculation engine can reproduce the values Excel
itself cached inside the file. The acceptance oracle is the spreadsheet. Never a
model.

_(9,000 = 3,000 trials × 3 independent seeds per case, the budget the reported
experiment actually ran. The harness and the pytest gate both default to 10,000
per seed; the reported run was capped to fit the event's clock, and every number
below is from the 3,000 × 3 configuration.)_

---

## The team

**Tanya Kaushal** — solo entrant. One person, all four deliverables.

I entered as an individual under the August 2026 edition's one-person rule. Every
line of `src/` and every evaluation case in this repository was written after
kickoff; everything I did not write is declared in
[PRIOR-WORK.md](PRIOR-WORK.md). The coding agents I used and the trajectories
they produced are disclosed in [AGENTS.md](AGENTS.md).

**On the two git author identities.** `git log` shows commits under two names —
`Tanya Kaushal` and `Witness` — because I ran some sessions with a per-repository
author set to the project name. **Both are me.** There is no second contributor.
I have deliberately not rewritten the history to normalise them: the commit
timestamps are the evidence that this was built after kickoff (Ground Rule 02),
and rewriting them would destroy exactly the record a reviewer should be able to
check. `git log --format='%an <%ae>'` shows both; `git log --format=%h` shows
every commit is a single-parent commit on one linear branch.

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
   workbook.xlsx  ───────▶│  0 · ENGINE-TRUST GATE        │  ✅ 12/12 usable
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

| #   | Component                                       | Why it exists                                                                                                                                                                                                                                                            |
| --- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0   | Engine-trust gate                               | Without it the oracle could be silently wrong, and every number downstream is worthless. **Executed: 12/12 usable workbooks, 36,500 cells, 0 disagreements.**                                                                                                            |
| 1   | Formula-DAG extractor                           | Deterministic. Porting a _derived_ cell as an _input_ is a whole failure family the model cannot see and the DAG cannot miss.                                                                                                                                            |
| 2   | Per-block translation                           | 2,300 formulas in one context window degrades badly. Blocks also cut cost per workbook.                                                                                                                                                                                  |
| 3   | Differential fuzzer                             | Converts "looks right" into a counterexample. This is the measurement, not a check on it.                                                                                                                                                                                |
| 4   | Shrunk counterexample as the only repair signal | Tests the claim that a _minimal failing input_ repairs better than a critic's narrative. **The ablation that would prove it came back null** — at 0.08 repairs per case the corpus needs repairing too rarely to separate the arms. Kept and shipped, labelled UNPROVEN. |
| 5   | Invariant layer                                 | Point equality on sampled vectors misses structural bugs; invariants derived from the DAG catch them.                                                                                                                                                                    |
| 6   | Refusal gate                                    | Ground Rules 04/05. Unsupported function ⇒ escalate, never a silent pass.                                                                                                                                                                                                |
| 7   | Signed certificate                              | Ground Rule 05 and the End-to-End Quality row: a human owns the decision, and the artifact says what it does _not_ cover.                                                                                                                                                |

---

## Does the agent solve it well

**Primary metric: certified-equivalence rate at 9,000 fuzzed vectors per case —
`pass^3000` across 3 independent seeds, not `pass@15`.**

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

Three commands, no Docker, no database, no network at judge time. All 17
workbooks are vendored into `corpus/`.

```bash
git clone <repo> && cd witness
uv sync
uv run python -m witness.verify
```

`verify` re-derives every figure published below from the raw artifacts in
`results/` and turns red if any of them no longer holds. It is the fastest way
to check that this README is telling the truth, and it exits non-zero when it
is not:

```
[GREEN]  engine-trust gate     12/17 workbooks · 36,500 cells · 0 disagreements
[GREEN]  harness self-test     37/37 cases · identity 300/300 · shortcut caught
[GREEN]  rejection tests       3 passed
[GREEN]  experiment            baseline 24/37 → witness 32/37 (+22pp) at pass^3000
[GREEN]  mutation score        189/231 semantic mutants killed (81.8%) · 0/165 false alarms
[GREEN]  oracle coverage       91.4% mean cell coverage · 100% branch coverage
ALL 6 CHECKS GREEN — every figure in README.md is backed by results/.
```

Add `--run` to regenerate those artifacts first instead of reading the
committed ones.

To watch the argument happen on a single cell instead of reading a scoreboard —
both ports loaded from disk and fuzzed live against the workbook, nothing
replayed:

```bash
uv run python -m witness.demo
```

It ties both ports out against the values the workbook was saved with (they
match, which is where a migration is normally signed off), then generates 3,000
inputs the history never contained and shrinks the first failure to the smallest
input that still breaks it.

To run the engine-trust gate alone:

```bash
uv run python -m witness.gate corpus
```

Current output, reproducible from a clean checkout:

```
GATE: 12/17 workbooks reproduce their own cached values
usable workbooks (had cached formula values): 12
total formula cells compared: 36500
total disagreements: 0
```

The five excluded workbooks carry no cached formula values at all — they were
saved without calculation, so there is nothing to validate the engine against.
That is a property of those files, not an engine failure, and the exclusion is a
**disclosed case-selection criterion**, not a hidden filter.

---

## Result

Command: `uv run python -m witness.evaluate 3000` · Raw: `results/evaluation.json`

| METRIC                                                          | SIMPLE BASELINE | AGENT SOLUTION | CHANGE     |
| --------------------------------------------------------------- | --------------- | -------------- | ---------- |
| **Certified-equivalence rate** (`pass^3000`, 3 seeds, 37 cases) | **65%**         | **86%**        | **+22 pp** |
| Ports certified                                                 | 24 / 37         | 32 / 37        | +8         |
| **Median error when it failed**                                 | **$47,482**     | **$1**         | —          |
| Largest undetected error in a self-certified port               | **$50,951**     | $9,132         | —          |

Paired: **9 Witness wins, 1 loss, 23 both-certified, 4 both-failed.**
**McNemar exact two-sided p = 0.0215 — significant at α = 0.05.**

### What this number attributes, and what it does not

The +22pp is the **whole scaffold** measured against the whole baseline. It is
not evidence that any one component caused the gain, and it is not offered as
such.

The Witness arm differs from the baseline in four ways at once: it receives the
extracted formula cone instead of a raw file, a typed input domain, a repair
loop, and a shrunk counterexample as that loop's only feedback. Model, cases,
fuzzer, tolerance, seeds and scorer are held fixed across the arms — so the
+22pp is attributable to **scaffolding rather than to the model**, and to
nothing finer than that.

The one component I tried to isolate is the fourth, and the attempt failed.
The ablation (`results/ablation.json`, 12 cases) fed the repair loop a shrunk
counterexample, a prose critique, or both:

| Repair signal       | Certified | Mean repairs when certified |
| ------------------- | --------- | --------------------------- |
| Counterexample only | 12 / 12   | 0.08                        |
| Prose critique only | 11 / 12   | 0.00                        |
| Both                | 12 / 12   | 0.08                        |

**The result is null, and the reason is diagnosable rather than mysterious:
mean repairs of 0.08 means the loop fired roughly once across twelve cases.**
You cannot compare two repair signals on a corpus that almost never needs
repairing. So the design claim in row 4 of the component table — that a minimal
failing input repairs better than a critic's narrative — is **stated but
unproven**, and it is labelled that way everywhere it appears. Testing it needs
a corpus selected for cases the first draft actually fails. That is the next
experiment, not this one.

### The finding that matters more than the rate

**When the baseline fails, it fails by a median of $47,482. When Witness fails,
it fails by a median of $1.**

Both arms produce imperfect ports. The difference is the size of what survives.
Thirteen baseline ports certified _themselves_ as correct while sitting on
five-figure errors — chained `EDATE` date arithmetic landing years off the
correct value. Witness's five failures are dominated by ±1 rounding-mode
disagreements that it found and reported rather than shipped.

A verifier that turns a $47,000 silent error into a $1 disclosed one has done its
job even when it does not reach GREEN.

### Supporting measurements

|                   |                                                                        |
| ----------------- | ---------------------------------------------------------------------- |
| Engine-trust gate | 12/12 usable workbooks, **36,500 formula cells, 0 disagreements**      |
| Harness self-test | identity 300/300 per case; always-zero shortcut caught on every case   |
| Mutation score    | **189/231 semantic mutants killed (81.8%), 0/165 false alarms (0.0%)** |
| Coverage          | **91.4% mean cell coverage, 100% branch coverage**                     |

Verified from a clean clone (`git clone` → `uv sync` → run).

Full evolution, removed experiments, the null-result ablation, and the failure
analysis: [CHANGELOG.md](CHANGELOG.md).

---

## Status

| Stage                                 | State                                                                                                    |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 0 · Engine-trust gate                 | ✅ 12/12 usable workbooks, 36,500 cells, 0 disagreements                                                 |
| 1 · Formula-DAG extractor             | ✅ 17 workbooks parsed, inputs typed                                                                     |
| 2 · Case scoping + sensitivity screen | ✅ **37 cases**, always-zero shortcut caught on every one                                                |
| 3 · Differential fuzzer               | ✅ 9,000 vectors per certified case (3,000 trials × 3 seeds)                                             |
| 4 · Shrink + repair loop              | ✅ only the shrunk counterexample is fed back                                                            |
| 5 · **Invariant layer**               | ✅ scale-homogeneity + monotonicity, each confirmed on the oracle before being enforced on the port      |
| 6 · Refusal gate                      | ✅ volatile and unsupported functions rejected                                                           |
| 7 · Certificate                       | ✅ signable, with a **quantified** coverage section                                                      |
| 8 · **Mutation suite**                | ✅ 7 semantic mutants + 5 equivalent false-alarm controls                                                |
| 9 · **Coverage map**                  | ✅ 91.4% mean cell coverage, 100% branch coverage                                                        |
| 10 · **pytest plugin**                | ✅ `certify_equivalent()` — ships as a CI gate                                                           |
| 11 · **Claim verifier**               | ✅ `witness.verify` — all 6 published figures re-derived from the raw artifacts, exits non-zero on drift |
| 12 · **Single-case walkthrough**      | ✅ `witness.demo` — historical tie-out, live fuzz, shrunk counterexample, on one cell                    |

Data: 17 municipal finance workbooks published by the Commonwealth of
Massachusetts, Division of Local Services. Public records. Provenance and
licences in [PRIOR-WORK.md](PRIOR-WORK.md).
