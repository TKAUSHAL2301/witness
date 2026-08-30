# Solution video — shot list and script

**Limit: 5:00. Target 4:30.** Record twice; keep the second take.

Required beats, per the rulebook: problem → simple baseline → one realistic
execution start to finish → final comparison → changelog → the change that
contributed most → one experiment you removed.

## Before you hit record

```bash
cd witness
uv sync                                   # make sure the venv is warm
TQDM_DISABLE=1 uv run python -m witness.gate corpus | tail -3      # pre-warm
open certificates/witness/                # have a certificate ready to show
```

Terminal at ~16pt, dark theme, window wide enough for the tables to not wrap.
Have three tabs open: (1) terminal, (2) `CHANGELOG.md`, (3) a certificate.

---

## 0:00–0:25 — The problem. Declarative first, no origin story.

> "A finance team runs their quarterly close on a spreadsheet. They want it as
> real code. A contractor writes the port. **How does anyone know the code does
> the same thing as the spreadsheet?**
>
> Today the answer is: check three past quarters, the numbers match, ship it.
>
> That's broken, and here's why. Historical inputs are a tiny sliver of
> everything that could happen — and they're exactly the sliver where the bug
> never fired. If the bug only shows up when a cell is blank instead of zero,
> and no past quarter had a blank there, you tie out perfectly and you're still
> wrong. You find out six months later when the quarter gets restated."

_On screen: the failure-family table from README.md._

## 0:25–0:50 — The baseline, run live.

> "So here's the baseline. A general-purpose coding agent, file tools, one
> instruction: port this workbook and make sure it's correct. It checks its own
> work however it likes. This isn't a strawman — it's what people actually do."

```bash
cat ports/baseline/financial-forecasting-template-5-year__Available_Funds.N48.py | head -25
```

> "It read the sheet, tied out against the values already in it, and declared
> victory. It looks completely reasonable."

## 0:50–2:10 — One realistic execution. **This is the money shot.**

> "Witness doesn't check three historical quarters. It makes up ten thousand
> inputs nobody has ever tried, feeds every one to _both_ the spreadsheet and
> the code, and checks they always agree."

```bash
TQDM_DISABLE=1 uv run python -m witness.evaluate 10000
```

_Let it run. Narrate over it:_

> "Left column is the baseline, right is Witness. Watch the baseline fail."

_When `FAILED@0  Δ=50,951.00` appears — **pause on it**:_

> "There. That baseline port had certified itself as correct. It's wrong by
> fifty thousand nine hundred and fifty-one. It's chained date arithmetic — the
> port lands years away from the right date, and no historical tie-out would
> ever have caught it, because no historical quarter goes there."

_When the summary table renders:_

> "Baseline four out of ten. Witness eight out of ten. Forty percentage points."

## 2:10–2:35 — The artifact a human signs.

```bash
cat certificates/witness/capital-targets-template__Debt.H8.md
```

> "And this is what the user actually gets. Not a green checkmark — a
> certificate. What was proven, over what domain, at what tolerance. And
> critically, five things it does **not** cover. A certificate that only lists
> its successes is marketing."

## 2:35–3:20 — The changelog and the biggest contributor.

_Switch to `CHANGELOG.md`._

> "The single change that mattered most wasn't the fuzzer. It was the
> **engine-trust gate** — stage zero. Before I fuzzed anything, I made the
> Python engine recalculate every formula and compare against the values Excel
> itself had cached inside the file. Twelve workbooks, thirty-six thousand five
> hundred cells, zero disagreements.
>
> That's what makes the whole thing defensible. **I don't author the answer key.
> The spreadsheet is the answer key** — and I proved my reader of it works
> before I used it. Every other approach has a step where a human decided what
> the right answer was. This one doesn't."

## 3:20–3:55 — The removed experiment. Be honest here; it scores.

> "Now the experiment I removed, and it's the one I got wrong.
>
> I designed the repair loop around a claim: when the fuzzer finds a
> disagreement, feed the agent the _shrunk counterexample_ — the minimal failing
> input — and never a written critique. A fact, not an opinion.
>
> So I ablated it. Three arms: counterexample, prose critique, both.
>
> **They tied. Four out of four, identical mean repairs.** My hypothesis is not
> supported. The cases were too easy to tell the arms apart.
>
> I'm shipping the counterexample design anyway because it's one function call
> instead of an extra LLM round-trip — but I've labelled that as unproven,
> because claiming it as a win would have been a fabricated result."

## 3:55–4:25 — Hot take and the honest limitation.

> "The hot take: **'it ties out on historical data' is the most dangerous
> sentence in software migration.** If your acceptance test is a fixed case set,
> you're testing the cases the bug already avoided. Give the verifier a
> generator, not a checklist.
>
> And the sharpest evidence isn't in the results table. It's that **my own
> evaluation certified a port that did nothing at all — on nine of sixteen
> cases** — and I only found out because I deliberately ran a do-nothing port
> against it. Every agent eval should have a shortcut arm. Most don't.
>
> Two honest limits. Ten cases: McNemar p is 0.219, so the direction is clear
> but it's underpowered. And Witness lost one case — off by exactly 1.00, from
> `ROUND` half-away-from-zero versus banker's rounding. The exact bug family
> this thing was built to catch. I'm reporting it as a loss, because it is one."

## 4:25–4:35 — Close.

> "Three commands from a clean clone, no Docker, no database, no API key.
> The spreadsheet is the oracle."

---

## Recording notes

- **Record the `evaluate` run separately at 10,000 trials and cut it in.** It
  takes 60–90 minutes; you want the real output, not a real-time wait.
  Alternatively run at `400` live — same shape, and say so on camera.
- Do **not** speed up the terminal so fast the numbers are unreadable.
- If a command fails on camera, keep going and say what happened. Judges score
  honesty higher than polish.
- Export at 1080p. Upload unlisted-but-public, then **open the link in a private
  window** before submitting.
