# Improvement Changelog

How this solution evolved, from the simple baseline to the final result. One
entry per meaningful experiment, each tied to the evidence that drove the next
decision — including the experiments that were removed and what they taught.

Every number below was produced by a command in this repository and is
reproducible from a clean checkout (see [REPRODUCE.md](REPRODUCE.md)).

---

## The baseline

**One general-purpose agent with basic tools**, given the workbook, the target
cell, the input list, and one instruction:

> _"Read the workbook, work out what the target cell computes, and write the
> port. Check your work however you think best."_

It has Read/Write/Edit/Bash/Glob/Grep and a Python interpreter. It self-checks
however it likes — typically by tying out against the values already in the
sheet. **This is not a strawman.** It is the PDF's own allowed baseline, and
"tie out a few historical rows and ship it" is the actual industry practice
this project exists to challenge.

Both arms receive the same cases, the same fuzzer, the same three seeds, the
same tolerance, and the same scorer. The only difference is how the port was
produced.

**Resource difference, disclosed:** the baseline is allowed file access and up
to 30 agent turns. The Witness arm gets no file access and ≤6 turns per call,
but is called up to 4 times (once to draft, up to 3 to repair). Witness sees
the extracted formula cone; the baseline sees the raw workbook and must extract
it itself.

---

## Changelog

| Stage                                      | What was tried, and why                                                                                                                                                                                 | Evidence                                                                                                                                 | Decision / learning                                                                                                                                                                                                                                                      |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **0 · Engine-trust gate**                  | Before building anything, check the premise: can a pure-Python engine reproduce Excel? Recalculate every formula cell and compare against the value Excel itself cached in the file.                    | 9/14 workbooks                                                                                                                           | **Investigate.** A 64% pass rate was too low to build on.                                                                                                                                                                                                                |
| **0a · Date-serial comparator**            | Inspected the failures. `EDATE` returned `42186`; `openpyxl` returned `datetime(2015,7,1)`. Same value, different type.                                                                                 | **12/14**, and the 2 remaining have _no cached values at all_ — nothing to compare. Net: **12/12 usable, 36,500 cells, 0 disagreements** | **Kept.** The gate found a bug in my measuring instrument before the instrument was trusted. The 2 exclusions became a disclosed case-selection criterion.                                                                                                               |
| **1 · Formula-DAG extractor**              | An LLM cannot reliably distinguish a _true input_ from a _derived cell_, and porting a derived cell as an input is a whole silent failure family. Build the dependency graph deterministically instead. | 14 workbooks parsed; one carries **195,141** input cells                                                                                 | **Kept, and it forced a redesign.** A whole workbook is not a fuzzable surface.                                                                                                                                                                                          |
| **2 · Scope each case to one output cone** | Owen does not care about 1,588 output cells; he cares about _the revenue number_. Scope a case to one target and its transitive input closure.                                                          | Cases become tractable: 6–38 inputs, 8–366 formula nodes                                                                                 | **Kept.** Smaller domain, denser sampling, and a certificate that says something a human can act on.                                                                                                                                                                     |
| **3 · Typed input domains**                | Uniform random floats find nothing. Type each input from the DAG and lift tier boundaries out of the lookup tables the formula actually references.                                                     | Boundary sets of up to 48 values per input                                                                                               | **Kept.** This is why the fuzzer finds tier-boundary bugs instead of noise.                                                                                                                                                                                              |
| **4 · Cone pruning (`shrink_dsp`)**        | Full-workbook recalculation cost **466 ms/vector** → 78 minutes for a single case at 10,000 trials. Prune the graph to the target's dependency cone.                                                    | **466 ms → 16.5 ms, a 28× speedup**                                                                                                      | **Kept.** This is the entire reason `pass^10000` is affordable rather than aspirational.                                                                                                                                                                                 |
| **5 · Harness self-test**                  | Do not trust a score from an unvalidated harness. Run the oracle against itself, against a mutant, and against a do-nothing port.                                                                       | Identity 300/300 everywhere — but **9 of 16 cases certified a port that unconditionally returns `0.0`**                                  | **Critical defect found.** Those targets were constant under sampling: a do-nothing agent scored 100%.                                                                                                                                                                   |
| **5a · Sensitivity screen**                | Reject any target that does not respond to its inputs — require ≥3 distinct values and non-zero in ≥25% of draws.                                                                                       | Cases 16 → **10**. Always-zero shortcut now caught **10/10**                                                                             | **Kept.** This is the exact defect the NeurIPS agentic-benchmark audit documents in τ-bench and SWE-Lancer. Fewer cases, but every one measures something.                                                                                                               |
| **6 · Differential fuzzer + shrinking**    | The core. Generate a vector, run both the workbook and the port on it, and on disagreement shrink to the minimal set of inputs responsible.                                                             | Repair trace on a real case: **0/1 → 4/5 → 2000/2000 certified**                                                                         | **Kept.** Fed only counterexamples, the agent independently derived Excel's phantom 1900-02-29 leap-year bug. It was never told about it.                                                                                                                                |
| **7 · Baseline capture defect**            | Reviewed the baseline arm before believing its score. The agent _wrote its module to disk_ and printed a prose summary; the harness read stdout and stored the prose.                                   | **3 of 10** baseline ports were unimportable prose                                                                                       | **Fixed, not reported.** Scoring the baseline as broken because of my own capture bug would have violated the fairness requirement. Sandboxed the agent, told it where to write, regenerated all 10. **10/10 now import.** v1 kept in `ports/_baseline_v1/` as evidence. |
| **8 · Final comparison**                   | Both arms, 10 cases, 3 seeds, 10,000 vectors each.                                                                                                                                                      | See [Final result](#final-result)                                                                                                        | —                                                                                                                                                                                                                                                                        |

---

## Removed experiments

The rulebook asks for the experiments that were cut and what they taught. These
are the ones that did not survive.

| Removed                                              | Why it was tried                                                                                                              | What happened                                                                                                                          | What it taught                                                                                                           |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Prose critique as the repair signal**              | The obvious design, and what most agent repair loops do: have a model explain the failure, hand the explanation to the fixer. | See [Ablation](#ablation-what-the-repair-loop-is-fed)                                                                                  | A shrunk counterexample is a _fact_; a critique is a _hypothesis_, and a wrong hypothesis actively misdirects the fixer. |
| **Invariant layer** (monotonicity, totals = Σ parts) | Point equality on sampled vectors misses structural bugs.                                                                     | Cut for time when the schedule collapsed from 34 to ~16 build-hours.                                                                   | Not a finding — an honest scope cut. It would likely have added detection power and is the first thing to build next.    |
| **Per-block (per-SCC) translation**                  | 2,300 formulas in one context window degrades badly.                                                                          | Collapsed to whole-cone translation once cases were scoped to a single output — the cone is small enough that blocking bought nothing. | Solving the right problem upstream (case scoping) removed the need for the downstream mitigation entirely.               |
| **Whole-workbook fuzzing**                           | The first design: fuzz every input in the workbook.                                                                           | 195,141 inputs on one workbook. Not a fuzzable surface.                                                                                | Scope the verification to the claim a human actually needs to sign, not to the artifact's full surface area.             |

---

## Ablation: what the repair loop is fed

Witness hands the agent **only** a shrunk counterexample — the minimal failing
vector, both outputs, and which inputs differ. No explanation of what went
wrong. Three arms, same cases, same budget:

| Repair signal | Certified | Mean repairs when certified |
| --- | --- | --- |
| `counterexample` — shrunk failing vector only | **4/4** | **0.5** |
| `prose` — an LLM critique of the failure | **4/4** | **0.5** |
| `both` — counterexample plus critique | **4/4** | **0.5** |

### This is a null result, and it does not support my hypothesis.

I designed the repair loop around the claim that a shrunk counterexample beats a
critique. **The ablation does not show that.** All three arms certified all four
cases in the same mean number of repairs.

The honest read: these four cases were too easy to discriminate between the arms
— most certified in 0 or 1 repairs, so there was barely any repair signal to
differentiate. The experiment as run cannot distinguish the hypothesis from the
null, and a larger, harder case set is needed before the claim means anything.

I am shipping the counterexample design anyway, for a reason the ablation does
*not* prove and which I am labelling as unproven: a counterexample is a fact the
agent can execute against and costs one deterministic function call, whereas a
critique costs an extra LLM round-trip per repair. On these cases it bought
nothing measurable. **Claiming it as a win would have been a fabricated result.**

Command: `uv run python -m witness.ablation 4` · Raw: `results/ablation.json`

---

## Final result

Command: `uv run python -m witness.evaluate 10000` · Raw: `results/evaluation.json`
| METRIC | SIMPLE BASELINE | AGENT SOLUTION | CHANGE |
| --- | --- | --- | --- |
| **Certified-equivalence rate** (`pass^10000`, all 3 seeds) | **40%** | **80%** | **+40 pp** |
| Ports certified | 4 / 10 | 8 / 10 | +4 |
| Largest undetected error in a self-certified baseline port | **$50,951** | — | — |
| Human time to verify one port | ~2–4 h manual tie-out | ~3 min automated | ~40–80× |
| Cost per certification | — | < $0.50 agent usage | — |

### Paired breakdown

| Outcome | Cases |
| --- | --- |
| Witness certified, baseline failed | **5** |
| Baseline certified, witness failed | **1** |
| Both certified | 3 |
| Both failed | 1 |

**Statistical honesty.** Six discordant pairs, 5–1 in Witness's favour. McNemar
exact two-sided **p = 0.219 — not significant at α = 0.05.** The effect direction
is consistent and the effect size is large, but ten cases is underpowered to
establish it. That is a limitation of corpus size, not evidence against the
method, and it is the strongest argument for expanding the corpus next.

**The four largest baseline errors were all date arithmetic** — chained `EDATE`
calls where the baseline port landed tens of thousands away from the correct
Excel date serial, i.e. a date years wrong. Every one of those baseline ports had
self-certified as correct.

**Witness's one loss is worth more than its wins.** On
`capital-targets-template::Debt.H8` the port returned `101090` where Excel returns
`101089.0` — **a delta of exactly 1.00**, from `ROUND` half-away-from-zero versus
Python's banker's rounding. That is precisely the failure family this project was
built to catch; it survived to trial 10 of 10,000, and the baseline's port
happened not to contain it. Reported as a loss, because it is one.


## Main failure mode

**The oracle is a re-implementation of Excel, not Excel.** It reproduced this
corpus's own cached values on 36,500 cells with zero disagreements, which is why
it is trusted here — but a function it computes _differently_ from Excel would
be invisible to this method, because both sides of the comparison would be
wrong in the same direction.

The mitigation is structural rather than hopeful: any target cell depending on
a function the engine does not support is **refused, not passed**, and every
certificate carries an explicit "what is NOT covered" section. Volatile
functions (`NOW`, `TODAY`, `RAND`, `OFFSET`, `INDIRECT`) cannot have a stable
oracle and are rejected during case selection.

Second failure mode, stated plainly: **10 cases is thin.** The PDF asks for ten
or more, so it clears the bar — barely. Five cases have a single free input.
A larger corpus is the highest-value next investment.

---

## Hot take

**"It ties out on historical data" is the most dangerous sentence in software
migration.**

Historical inputs are a measure-zero slice of the input space, and they are
precisely the slice the bug already avoided. A port that agrees on three
historical quarters has demonstrated agreement on three points of an infinite
domain — and the defect that will restate your quarter lives in the region
nobody has ever fed it.

The generalisation for anyone building agents: **if your acceptance test is a
fixed case set, you are testing the cases the bug already avoided.** Give the
verifier a _generator_, not a checklist. And when it finds a failure, give the
repair loop the shrunk counterexample rather than a critic's opinion about it —
a counterexample is a fact the agent can execute against, an opinion is a
hypothesis it has to trust.

The sharpest evidence for this is not in the final table. It is in stage 5:
**my own evaluation certified a port that did nothing at all, on 9 of 16 cases,
and I only found out because I ran the do-nothing port on purpose.** Every
agent evaluation should include a shortcut arm. Most do not.
