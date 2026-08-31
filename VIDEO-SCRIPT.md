# Solution video — shot list and script

**Limit: 5:00. Target 4:30.** Record twice; keep the second take.

Required beats, per the rulebook: problem → simple baseline → one realistic
execution start to finish → final comparison → changelog → the change that
contributed most → one experiment you removed.

---

## What the product is, in one breath

Say this out loud before you record. If you can't, the video won't land.

> **You give Witness an Excel workbook and a cell you care about.
> It gives you back Python code for that cell, and a signed certificate saying
> the code provably matches the spreadsheet — or it refuses to certify and tells
> you exactly which input breaks it.**

Input: `corpus/*.xlsx` + a target cell.
Output: `ports/witness/<case>.py` + `certificates/witness/<case>.md`.

There is no app and no web page, and that is the point: the deliverable is
*evidence a reviewer can re-run*, not a screen they have to trust.

---

## Before you hit record

```bash
cd witness
uv sync
uv run python -m witness.verify
```

That last command warms every cache and confirms all six checks are green, so
nothing surprises you on camera. Have three tabs open: (1) terminal,
(2) `CHANGELOG.md`, (3) `certificates/witness/appropriation-template__Annual.D31.md`.

Terminal at ~16pt, dark theme, window wide enough that the tables do not wrap.

---

## 0:00–0:30 — The problem. Declarative, no origin story.

> "A finance team runs their quarterly close on a spreadsheet. They want it as
> real code. A contractor writes the port. **How does anyone know the code does
> the same thing as the spreadsheet?**
>
> Today the answer is: check three past quarters, the numbers match, ship it.
>
> That is broken. Historical inputs are a tiny sliver of everything that could
> happen — and they are exactly the sliver where the bug never fired. If the bug
> only shows up when a cell is blank instead of zero, and no past quarter had a
> blank there, you tie out perfectly and you are still wrong. You find out six
> months later, when the quarter gets restated."

## 0:30–0:50 — What Witness produces.

> "So this is Witness. You give it a workbook and a cell. It gives you back
> Python, and a certificate that says the Python provably matches — or it
> refuses, and hands you the exact input that breaks it.
>
> The baseline I am comparing against is a general-purpose coding agent with
> file tools and one instruction: port this workbook and make sure it is
> correct. It checks its own work however it likes. That is not a strawman —
> that is what people actually do."

## 0:50–2:05 — One realistic execution. **This is the money shot.**

```bash
uv run python -m witness.demo
```

_Runs in about a minute. Narrate over it._

When **Step 1** lands, slow down — this is the whole argument:

> "Both ports are being run on the values the workbook was actually saved with.
> Excel's own cached answer is forty-eight thousand and thirty. Both ports
> return forty-eight thousand and thirty. **Both tie out.** On exactly this
> evidence, a controller signs the migration off today."

When **Step 2** lands:

> "Now three thousand inputs the history never contained. The baseline fails on
> the first one — it returns no value at all. Same calendar date, handed over in
> a form it did not anticipate, and it produces nothing. Witness agrees on all
> three thousand."

When **Step 3** lands:

> "And this is the part that matters for building agents. The failure gets
> shrunk to the smallest input that still breaks it — and **that vector is the
> only thing the repair loop ever sees.** No prose, no critique. A fact, not an
> opinion."

## 2:05–2:30 — The scoreboard.

```bash
uv run python -m witness.verify
```

> "Six checks. Every number this project publishes, re-derived from the raw
> artifacts and compared against what the README claims — so you are not taking
> my word for any of it. It exits non-zero if a single figure has drifted.
>
> Baseline twenty-four of thirty-seven. Witness thirty-two of thirty-seven.
> **Twenty-two percentage points, McNemar exact p equals 0.0215.**
>
> But the number I care about more is this one: when the baseline fails, it
> fails by a median of **forty-seven thousand dollars**. When Witness fails, it
> fails by a median of **one dollar**. Both produce imperfect ports. The
> difference is the size of what survives."

## 2:30–2:55 — The artifact a human signs.

_Switch to the certificate tab._

> "And this is what the user actually gets. Not a green checkmark — a
> certificate. What was proven, over what domain, at what tolerance. Five things
> it explicitly does **not** cover. And a signature block, because this is a
> recommendation to a qualified human reviewer, not an authorization to cut
> over. A certificate that only lists its successes is marketing."

## 2:55–3:30 — The change that contributed most.

_Switch to `CHANGELOG.md`._

> "The single change that mattered most was not the fuzzer. It was **stage
> zero — the engine-trust gate.** Before I fuzzed anything, I made the Python
> engine recalculate every formula and compare against the values Excel itself
> had cached inside the file. Twelve workbooks, thirty-six thousand five hundred
> cells, zero disagreements.
>
> That is what makes this defensible. **I do not author the answer key. The
> spreadsheet is the answer key** — and I proved my reader of it works before I
> used it. Every other approach has a step where a human decided what the right
> answer was. This one does not."

## 3:30–4:05 — The removed experiment. Be honest; it scores.

> "Now the experiment I removed, and it is the one I got wrong.
>
> I designed the repair loop around a claim: feed the agent the shrunk
> counterexample, never a written critique. So I ablated it. Three arms.
>
> **Counterexample twelve of twelve. Prose eleven of twelve. Both twelve of
> twelve.** Effectively a tie. And the diagnosis is precise: mean repairs was
> **zero point zero eight** — across twelve cases the loop performed about one
> repair. You cannot compare repair signals on a corpus that never needs
> repairing.
>
> I am shipping the counterexample design anyway, because it is one function
> call instead of an extra model round-trip — but it is labelled **unproven**.
> Claiming it as a win would have been a fabricated result."

## 4:05–4:30 — Hot take, honest limits, close.

> "The hot take: **'it ties out on historical data' is the most dangerous
> sentence in software migration.** If your acceptance test is a fixed case set,
> you are testing the cases the bug already avoided. Give the verifier a
> generator, not a checklist.
>
> And the sharpest evidence is not in the results table. **My own evaluation
> once certified a port that did nothing at all** — and I only found out because
> I deliberately ran a do-nothing port against it. That is now a permanent check:
> every case is tested against a port that always returns zero, and it has to be
> caught. Every agent eval should have a shortcut arm. Most do not.
>
> One honest loss: Witness failed a case by exactly one dollar — `ROUND`
> half-away-from-zero versus banker's rounding. The exact bug family this thing
> was built to catch. I am reporting it as a loss, because it is one.
>
> Clone, `uv sync`, `witness.verify`. No Docker, no database, no API key.
> The spreadsheet is the oracle."

---

## Recording notes

- `witness.demo` takes about a minute and is safe to run live. `witness.verify`
  takes ten seconds. Neither needs the network. This whole video can be one take.
- If you would rather show the full experiment, `witness.evaluate 400` runs in
  ~4 minutes and reproduces the published headline exactly — **cut it in**, do
  not wait on camera.
- Do **not** speed the terminal up so far the numbers are unreadable.
- If a command fails on camera, keep going and say what happened. Judges score
  honesty above polish.
- Export 1080p. Upload unlisted-but-public, then **open the link in a private
  window** before submitting.

---

## Every number spoken in this script, and where it comes from

Run `uv run python -m witness.verify` to confirm all of these in ten seconds.

| Spoken | Source |
| --- | --- |
| 48,030 tie-out, both ports | `witness.demo` step 1, live |
| 3,000 vectors, baseline fails at trial 0 | `witness.demo` step 2, live |
| 24/37 → 32/37, +22pp | `results/evaluation.json` |
| McNemar exact p = 0.0215 | `README.md` § Result |
| median $47,482 vs $1 | `results/evaluation.json` |
| 12 workbooks, 36,500 cells, 0 disagreements | `results/gate.json` |
| ablation 12/12, 11/12, 12/12, mean repairs 0.08 | `results/ablation.json` |
