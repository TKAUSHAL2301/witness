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
| **0a · Date-serial comparator**            | Inspected the failures. `EDATE` returned `42186`; `openpyxl` returned `datetime(2015,7,1)`. Same value, different type.                                                                                 | **12/17** pass; the 5 excluded have _no cached formula values at all_ — nothing to compare against. Net: **12/12 usable, 36,500 cells, 0 disagreements** | **Kept.** The gate found a bug in my measuring instrument before the instrument was trusted. The exclusions became a disclosed case-selection criterion.                                                                                                               |
| **1 · Formula-DAG extractor**              | An LLM cannot reliably distinguish a _true input_ from a _derived cell_, and porting a derived cell as an input is a whole silent failure family. Build the dependency graph deterministically instead. | 14 workbooks parsed; one carries **195,141** input cells                                                                                 | **Kept, and it forced a redesign.** A whole workbook is not a fuzzable surface.                                                                                                                                                                                          |
| **2 · Scope each case to one output cone** | Owen does not care about 1,588 output cells; he cares about _the revenue number_. Scope a case to one target and its transitive input closure.                                                          | Cases become tractable: 6–38 inputs, 8–366 formula nodes                                                                                 | **Kept.** Smaller domain, denser sampling, and a certificate that says something a human can act on.                                                                                                                                                                     |
| **3 · Typed input domains**                | Uniform random floats find nothing. Type each input from the DAG and lift tier boundaries out of the lookup tables the formula actually references.                                                     | Boundary sets of up to 48 values per input                                                                                               | **Kept.** This is why the fuzzer finds tier-boundary bugs instead of noise.                                                                                                                                                                                              |
| **4 · Cone pruning (`shrink_dsp`)**        | Full-workbook recalculation cost **466 ms/vector** → 78 minutes for a single case at 10,000 trials. Prune the graph to the target's dependency cone.                                                    | **466 ms → 16.5 ms, a 28× speedup**                                                                                                      | **Kept.** Without it a single case costs 78 minutes at 10,000 trials; this is what makes a multi-thousand-vector budget affordable at all.                                                                                                                                                                                 |
| **5 · Harness self-test**                  | Do not trust a score from an unvalidated harness. Run the oracle against itself, against a mutant, and against a do-nothing port.                                                                       | Identity 300/300 everywhere — but **9 of 16 cases certified a port that unconditionally returns `0.0`**                                  | **Critical defect found.** Those targets were constant under sampling: a do-nothing agent scored 100%.                                                                                                                                                                   |
| **5a · Sensitivity screen**                | Reject any target that does not respond to its inputs — require ≥3 distinct values and non-zero in ≥25% of draws.                                                                                       | Cases 16 → **10**. Always-zero shortcut now caught **10/10**                                                                             | **Kept.** This is the exact defect the NeurIPS agentic-benchmark audit documents in τ-bench and SWE-Lancer. Fewer cases, but every one measures something.                                                                                                               |
| **6 · Differential fuzzer + shrinking**    | The core. Generate a vector, run both the workbook and the port on it, and on disagreement shrink to the minimal set of inputs responsible.                                                             | Repair trace on a real case: **0/1 → 4/5 → 2000/2000 certified**                                                                         | **Kept.** Fed only counterexamples, the agent independently derived Excel's phantom 1900-02-29 leap-year bug. It was never told about it.                                                                                                                                |
| **7 · Baseline capture defect**            | Reviewed the baseline arm before believing its score. The agent _wrote its module to disk_ and printed a prose summary; the harness read stdout and stored the prose.                                   | **3 of 10** baseline ports were unimportable prose                                                                                       | **Fixed, not reported.** Scoring the baseline as broken because of my own capture bug would have violated the fairness requirement. Sandboxed the agent, told it where to write, regenerated all 10. **10/10 now import.** v1 kept in `ports/_baseline_v1/` as evidence. |
| **8 · Corpus growth** | McNemar p=0.219 on 10 cases meant the result was underpowered. The legitimate fix is more evidence, not a different number: 3 more workbooks, and relaxed selection (min depth 6→3, max inputs 40→60, per-sheet cap 2→5). | **10 → 37 cases** across 7 workbooks | **Kept.** Every added case still passes the sensitivity screen and the always-zero shortcut check. |
| **9 · Oracle cache** | The evaluator rebuilt the full workbook model per case. 37 cases over 7 workbooks meant recompiling the same large workbook a dozen times. | evaluation wall-clock from multi-hour to ~2 h; fuzzing itself is ~1 ms/vector | **Kept.** The bottleneck was never the fuzzing. |
| **10 · Invariant layer** | Point equality on sampled vectors is blind to a port that is structurally wrong but agrees on the values drawn. Derive scale-homogeneity and monotonicity from the DAG. | each invariant is **confirmed against the oracle first**; one the workbook does not satisfy is discarded, never enforced | **Kept.** This is the component cut for time in the first pass, now shipped. |
| **11 · Mutation suite** | The first suite used one mutant (blank-as-zero) and killed 0/10 — the wrong mutant for this corpus, not a weak fuzzer. Rebuild it around the families the corpus actually exhibits. | 7 semantic mutants (banker's rounding, date-serial off-by-one, truncation, sign, scale…) + **5 equivalent mutants as false-alarm controls** | **Kept.** Without equivalent-mutant controls a mutation score just rewards paranoia. |
| **12 · Coverage map** | "9,000 vectors agreed" is weak if every vector drove the calculation down the same branch. Measure which cells and IF-branches actually varied. | **91.4% mean cell coverage, 100% branch coverage** | **Kept.** The certificate's limits section is now a number, not a disclaimer. |
| **13 · pytest plugin** | A report is a deliverable; a CI gate is a tool. `certify_equivalent(workbook, target, port)` produces a normal pytest test whose failure message *is* the shrunk counterexample. | tests pass for a certified port and **fail for a banker's-rounding mutant** | **Kept.** Turns a migration project into a regression gate. |
| **8 · Final comparison** | Both arms, 37 cases, 3 seeds, 3,000 vectors per seed (9,000 per case).                                                                                                                                                      | See [Final result](#final-result)                                                                                                        | —                                                                                                                                                                                                                                                                        |

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
| `counterexample` — shrunk failing vector only | **12/12** | 0.08 |
| `prose` — an LLM critique of the failure | **11/12** | 0.00 |
| `both` — counterexample plus critique | **12/12** | 0.08 |

Command: `uv run python -m witness.ablation 12` · Raw: `results/ablation.json`

### Still a null result — and now I can say why.

I designed the repair loop around the claim that a shrunk counterexample beats a
critique. **Twelve cases do not support it.** The counterexample and both-arms
certified 12/12 against prose's 11/12 — a one-case difference, which on twelve
paired cases is indistinguishable from noise.

The first run of this ablation used four cases and I wrote it up as
"underpowered." That was the right call but the wrong diagnosis. Tripling to
twelve cases did not move it, and the reason is visible in the second column:
**mean repairs is 0.08.** Across twelve cases the loop performed roughly one
repair in total. You cannot compare two repair signals on a case set that almost
never needs repairing — the experiment has no exposure to the variable it is
supposed to measure.

So the honest finding is not "counterexamples do not help." It is:
**this corpus is too easy to discriminate repair strategies, and adding cases of
the same difficulty will never fix that.** The experiment that would settle it
needs cases selected *for* requiring 2+ repairs — deep formula cones with
rounding and date semantics, not more shallow SUMs.

I am shipping the counterexample design anyway, on a cost argument the ablation
does *not* prove and which I am labelling unproven: it is one deterministic
function call, where the prose arm spends an extra LLM round-trip per repair.
On this corpus it bought nothing measurable. **Reporting it as a win would have
been fabrication.**

---

## Final result

Command: `uv run python -m witness.evaluate 3000` · Raw: `results/evaluation.json`
| METRIC | SIMPLE BASELINE | AGENT SOLUTION | CHANGE |
| --- | --- | --- | --- |
| **Certified-equivalence rate** (`pass^3000`, all 3 seeds) | **65%** | **86%** | **+22 pp** |
| Ports certified | 24 / 37 | 32 / 37 | +8 |
| Ports that failed | 13 | 5 | −8 |
| **Median error when it failed** | **$47,482** | **$1** | — |
| Largest undetected error in a self-certified port | **$50,951** | $9,132 | — |
| Human time to verify one port | ~2–4 h manual tie-out | ~3 min automated | ~40–80× |
| Cost per certification | — | < $0.50 agent usage | — |

### Paired breakdown, 37 cases

| Outcome | Cases |
| --- | --- |
| Witness certified, baseline failed | **9** |
| Baseline certified, witness failed | **1** |
| Both certified | 23 |
| Both failed | 4 |

**McNemar exact two-sided p = 0.0215 — significant at α = 0.05.**

This is the number the first run could not produce. At 10 cases the same effect
gave p = 0.219 and I reported it as underpowered rather than dressing it up.
The fix was more evidence, not a different statistic: 10 → 37 cases, and the
direction held while the interval tightened.

### The finding that matters more than the rate

**When the baseline fails, it fails by a median of $47,482.
When Witness fails, it fails by a median of $1.**

Both arms produce imperfect ports. The difference is the *size* of what survives.
Thirteen baseline ports certified themselves as correct while sitting on
five-figure errors — chained `EDATE` date arithmetic landing years off. Witness's
five failures are dominated by ±1 rounding-mode disagreements it found and
reported rather than shipped.

A verifier that turns a $47,000 silent error into a $1 disclosed one has done
its job even when it does not reach GREEN.

---

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
