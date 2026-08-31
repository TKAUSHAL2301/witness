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

## What a good result means, defined before the evaluation ran

The rulebook asks for this to be settled *before* running, so it is stated here
as it was fixed in `results/cases.json` — frozen before any port was generated:

> **A port is CERTIFIED for a case only if, across all three seeds, every one of
> 3,000 generated input vectors produces a value matching the workbook within
> relative 1e-9 / absolute 1e-6 — and no confirmed structural invariant is
> violated. Anything less is not equivalent.**

This is all-or-nothing per case on purpose. Owen does not get partial credit for
a port that is right 99% of the time; one wrong quarter is a restatement. A case
where the target depends on a volatile function (`NOW`, `RAND`, `OFFSET`,
`INDIRECT`) is **refused rather than scored**, because it cannot have a stable
oracle.

The tolerance, the seeds, the trial budget and the pass criterion were fixed
before generation and never adjusted afterwards.

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
| **10 · Invariant layer** | Point equality on sampled vectors is blind to a port that is structurally wrong but agrees on the values drawn. Derive scale-homogeneity and monotonicity from the DAG. | 212 invariants proposed, **106 confirmed against the oracle** (18 scale, 88 monotone), **0 violated by any port** | **Kept, and it found nothing.** Reported as a null contribution rather than presented as a success — see below. |
| **11 · Mutation suite** | The first suite used one mutant (blank-as-zero) and killed 0/10 — the wrong mutant for this corpus, not a weak fuzzer. Rebuild around the families the corpus actually exhibits. | **189/231 semantic mutants killed (81.8%)**, **0/165 false alarms (0.0%)** across 33 certified ports | **Kept.** The 0% false-alarm rate is what the equivalent-mutant controls exist to prove; without them a kill rate just rewards paranoia. |
| **12 · Coverage map** | "9,000 vectors agreed" is weak if every vector drove the calculation down the same branch. Measure which cells and IF-branches actually varied. | **91.4% mean cell coverage, 100% branch coverage** | **Kept.** The certificate's limits section is now a number, not a disclaimer. |
| **13 · pytest plugin** | A report is a deliverable; a CI gate is a tool. `certify_equivalent(workbook, target, port)` produces a normal pytest test whose failure message *is* the shrunk counterexample. | tests pass for a certified port and **fail for a banker's-rounding mutant** | **Kept.** Turns a migration project into a regression gate. |
| **14 · Claim verifier** | Green tests prove the stages pass; they do not prove the README is telling the truth about them. Two committed artifacts had already drifted behind the prose citing them — `gate.json` said 14 workbooks after the corpus grew to 17, and `selftest.json` held 10 cases at 100 trials while the README claimed 300 across 37. Both survived every green test run, because the claims and the evidence were never compared to each other. | `witness.verify` re-derives all six published figures from the raw artifacts and diffs them against the claimed values; **caught both stale artifacts**, exits non-zero on red | **Kept.** Ground Rule 09 says every claim must connect to submitted evidence. This makes that checkable in ten seconds instead of trusted. |
| **15 · Single-case walkthrough** | The scoreboard proves the numbers; it does not show a reviewer *why* a fixed test set fails them. Replay one cell end to end: historical tie-out, then fuzz, then shrink. | on `Available Funds.T48` both ports reproduce Excel's cached **48,030.00** from the saved inputs, then the baseline **returns no value at all** on the same calendar date in a different representation | **Kept.** It is the one screen that shows why tying out on history is not evidence. Both ports are loaded from disk and fuzzed live — nothing is replayed from a stored result. |
| **8 · Final comparison** | Both arms, 37 cases, 3 seeds, 3,000 vectors per seed (9,000 per case).                                                                                                                                                      | See [Final result](#final-result)                                                                                                        | —                                                                                                                                                                                                                                                                        |

---

## The challenging case, and what it revealed

The rulebook asks for one hard case explained. This is it, and it is the single
most informative row in the whole evaluation.

**`financial-forecasting-template-10-year::Available Funds.S48`** — 35 formula
nodes, and exactly **one** free input: a date in `Fiscal Years!B13` that a chain
of `EDATE` calls walks forward year by year.

| | Baseline | Witness |
| --- | --- | --- |
| First disagreement | **trial 0** — the workbook's own saved inputs | **trial 132** |
| Excel expected | 47,665 | 7,364 |
| Port returned | `None` | 7,365 |
| Error | **−$47,665** | **+$1** |

Three things this case revealed:

**1. The baseline failed on the workbook's own data.** Trial 0 is not a fuzzed
vector — it is the values already saved in the spreadsheet. The baseline port
returned `None` where Excel returns a date serial, and it had *self-certified as
correct* before the fuzzer ever ran. Its own checking looked at the sheet and
concluded it matched.

**2. One input is enough to be hard.** With a single free variable there is no
combinatorial explosion to hide in — and it still took **132 generated vectors**
to expose Witness's defect. A fixed test set of ten or fifteen cases would have
declared this port correct. That is the entire thesis of the project reproduced
inside one case.

**3. The surviving defect is a $1 rounding-mode disagreement**, not a logic
error. `ROUND` half-away-from-zero versus Python's banker's rounding, surfacing
only on inputs where the intermediate lands exactly on .5. It is the smallest
class of bug the fuzzer can find, it is invisible to historical tie-out, and it
is precisely the class that quietly accumulates across a quarter.

A related case, **`financial-forecasting-template-5-year::CPF.Q20`**, revealed a
limit of the method rather than of a port: the oracle returned an *empty* value
where both ports returned `-730.21`. That is the recalculation engine declining
to evaluate a construct, not a port defect — and it is why unsupported
constructs are reported as "cannot certify" rather than as failures.

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
| Machine time to certify one port | — | **236 s** (3 seeds × 3,000 vectors), measured | — |
| Human time per port | *estimated* 2–4 h manual tie-out | **0 min** — no human in the measurement loop | *estimate, not measured* |
| Cost per certification | — | **$0** to run; the fuzzer calls no model | — |

The machine-time figure is measured: 222 fuzz runs totalling 290.9 minutes
(`results/evaluation.json`, `seconds` field per run). **The human-time row is an
estimate and is labelled as one** — I did not run a timed human tie-out, so it
carries no evidence and should not be read as a measured result. Cost is $0
because certification is pure computation; only *generating* a port calls a
model, and that is a separate step.

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

## Mutation score — what the verifier can actually detect

Accuracy on a fixed case set tells you whether an agent guessed right. It does
not tell you whether your *verifier* could detect a defect at all. So: inject a
known defect into a port the fuzzer has already certified, and see if it notices.

| | |
| --- | --- |
| Certified ports mutated | 33 |
| Semantic mutants killed | **189 / 231 (81.8%)** |
| **False alarms on equivalent mutants** | **0 / 165 (0.0%)** |

The 0% false-alarm rate matters more than the kill rate. Five of the twelve
mutants per case are *equivalent* — `float()` casts, `+ 0.0`, double negation,
a subtraction below tolerance — semantics-preserving changes the fuzzer must
**not** flag. Without those controls, a high kill rate only proves the verifier
is trigger-happy.

**The 18% it misses is informative.** The most-missed mutants are
`date_serial_off_by_one` (15 cases), `rounding_bankers` (10) and
`truncate_not_round` (10). Those are misses by *inapplicability*, not blindness:
a date-serial mutant cannot be detected on a case whose target never produces a
date-magnitude value, and a rounding mutant cannot be detected where the target
is already integral. The honest reading is that the corpus does not exercise
every failure family on every case — which is the same corpus-difficulty
limitation the ablation ran into.

## The invariant layer found nothing, and that is worth saying

The invariant layer proposed 212 properties and confirmed 106 of them against
the oracle — 18 scale-homogeneity, 88 monotonicity. **Ports violated zero of
them.**

Every case that the invariants could have caught, the differential fuzzer had
already caught by value comparison. On this corpus the component contributed no
additional detection.

I am shipping it anyway, and labelling its contribution as **zero on this
evidence**, for two reasons. It is a per-run structural guarantee rather than a
probabilistic one, so it covers a failure mode sampling cannot reach in
principle. And its design is the defensible part: each invariant is confirmed
against the workbook *before* it is enforced against the port, so an invariant
the spreadsheet does not itself satisfy is discarded rather than used to fail
correct code — which is how this kind of check usually goes wrong.

A component with no number is decoration. This one has a number, and the number
is zero.

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
