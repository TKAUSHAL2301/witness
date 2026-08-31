# Reproduction guide

Written for someone starting from a clean machine who has never seen this
project. Every command below is meant to be pasted verbatim.

---

## 0. What you need

|         |                                                                      |
| ------- | -------------------------------------------------------------------- |
| OS      | macOS or Linux (developed on macOS 15, arm64)                        |
| Python  | **3.12+** (3.13.14 used for every number here) — `uv` installs it; your system Python is not used |
| Disk    | ~400 MB (deps + the vendored workbook corpus)                        |
| Network | **Only for `uv sync`.** The evaluation itself needs no network.      |
| API key | **Not required** to reproduce the results. See §5 for regeneration.  |

The only prerequisite is [`uv`](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh      # macOS / Linux
```

No Docker. No database. No `ffmpeg`. Nothing to configure.

---

## 1. Set up (about 60 seconds)

```bash
git clone <REPO-URL> witness
cd witness
uv sync
```

`uv sync` reads `uv.lock` and installs the exact pinned versions used to produce
every number in this repository — `openpyxl 3.1.5`, `formulas 1.3.4`,
`hypothesis 6.165.10`, plus their transitive dependencies.

Verify:

```bash
uv run python -c "import openpyxl, formulas, hypothesis; print('ok')"
```

Expected output: `ok`

---

## 2. The engine-trust gate — run this first

Nothing else in this project means anything unless the acceptance oracle is
sound. This step proves it: for every workbook, it recalculates each formula
cell with the pure-Python engine and compares against **the value Excel itself
last cached inside the file**.

```bash
uv run python -m witness.gate corpus
```

**Expected output** (~2 minutes):

```
[PASS] appropriation-template.xlsx                  139/139 cells
[PASS] budget-and-tax-rate-planning-tool.xlsx       3265/3265 cells, 36 no-cache
[FAIL] budget-calendar.xlsx                         0/0 cells  :: no formula cells with cached values
...
================================================================
GATE: 12/17 workbooks reproduce their own cached values
```

**How to read it.** 12 of 14 workbooks pass. The 2 that "fail" contain no
cached formula values at all — they were saved without calculation, so there is
nothing to validate the engine against. That is a property of those files, not
an engine failure, and they are excluded from the corpus as a **disclosed
case-selection criterion**. Across the 12 usable workbooks the engine
reproduced **36,500 formula cells with 0 disagreements**.

Machine-readable detail: `results/gate.json`.

---

## 3. Harness validation — before trusting any score

Running a known-good reference through the harness and checking it passes
N-for-N is the standard defence against a leaky environment. This runs three
checks per case:

| Check      | What it runs                     | Must                                       |
| ---------- | -------------------------------- | ------------------------------------------ |
| `IDENTITY` | the oracle against itself        | **certify** — no false alarms              |
| `MUTANT`   | a port that treats blank as zero | detect, where applicable                   |
| `SHORTCUT` | a port that always returns `0.0` | **fail** — the metric must not be gameable |

```bash
uv run python -m witness.selftest 300
```

**Expected output** (~3 minutes):

```
[PASS] budget-and-tax-rate-planning-tool::Recap Page 2.L52   identity=300/300 shortcut=caught
... (10 cases)
harness valid on 10/10 cases  (300 trials each)
```

If `identity` is ever less than `300/300`, the environment is leaking
nondeterminism and **no number from it should be trusted**. If `shortcut` ever
reports `PASSED(!!)`, the metric is gameable and that case is worthless.

Machine-readable detail: `results/selftest.json`.

---

## 4. The experiment — baseline vs Witness

Both arms are evaluated on the same cases, with the same fuzzer, the same three
seeds, the same tolerance, and the same scorer. The only difference is how the
port was produced. This uses the **committed** ports, so it needs no API key.

```bash
uv run python -m witness.evaluate 3000
```

**Runtime:** roughly 2 hours for the full 37 cases. A port that disagrees stops early; a port
that certifies runs the full 3,000 vectors x 3 seeds = 9,000. For a fast smoke check
that finishes in ~3 minutes, use a smaller budget — the shape of the result is
the same, the confidence is lower:

```bash
uv run python -m witness.evaluate 400
```

**Expected output:**

```
==========================================================================
CERTIFIED-EQUIVALENCE RATE  (pass^3000, all of seeds [11, 23, 47])
==========================================================================
METRIC                                    BASELINE     WITNESS      CHANGE
Ports certified                                ...         ...         ...
Certified-equivalence rate                     ...         ...         ...
Largest undetected baseline error              ...           —           —
==========================================================================
```

A case counts as certified only if **all three seeds** survive the full trial
budget with zero disagreements outside tolerance.

Machine-readable detail: `results/evaluation.json` — including, for every
failure, the shrunk counterexample and the exact dollar delta.

---

## 5. Certificates

```bash
uv run python -m witness.certificate witness
```

Writes one signable equivalence certificate per case to `certificates/witness/`.
Each states what was proven, over what domain, at what tolerance — and five
things it explicitly does **not** cover.

---

## 6. Optional — regenerate the ports (needs credentials)

Everything above evaluates committed artifacts. To regenerate the ports
themselves you need a working `claude` CLI:

```bash
uv run python -m witness.port both        # ~25 min, both arms
uv run python -m witness.ablation 4       # the repair-signal ablation
```

Approximate cost of a full regeneration: **under $5** of agent usage on the
model used here. The evaluation is free.

---

## 7. Approximate runtime and cost

| Step                     | Time      | Network | Credentials |
| ------------------------ | --------- | ------- | ----------- |
| `uv sync`                | ~60 s     | yes     | no          |
| `witness.gate`           | ~2 min    | no      | no          |
| `witness.selftest 300`   | ~3 min    | no      | no          |
| `witness.evaluate 400`   | ~3 min    | no      | no          |
| `witness.evaluate 3000` | ~2 h | no | no |
| `witness.certificate`    | < 5 s     | no      | no          |
| `witness.port both`      | ~25 min   | yes     | **yes**     |

---

## 8. Data

`corpus/` contains 14 municipal finance workbooks published by the
**Commonwealth of Massachusetts, Division of Local Services** — debt-service
schedules, tax-rate planning tools, and 5- and 10-year financial forecasting
templates. Public records of a US state government, downloaded 2026-08-29 from
`mass.gov/info-details/municipal-finance-tools-templates-calculators`.

They are vendored into the repository, so **no network access is required at
evaluation time** and the corpus cannot drift underneath the results.

Provenance and licences: [PRIOR-WORK.md](PRIOR-WORK.md).

---

## 9. If something goes wrong

| Symptom                                       | Cause                                                  | Fix                                                                 |
| --------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------- |
| `No module named witness`                     | package not installed into the venv                    | `uv sync` again                                                     |
| `identity` below 300/300 in the self-test     | nondeterministic environment                           | Stop. Do not trust any score until this is 300/300.                 |
| tqdm progress bars flood the output           | the `formulas` engine's own bars                       | prefix with `TQDM_DISABLE=1`                                        |
| `Error in loading '[2]SHEET!A1:B2'` on stderr | workbook links to an external file not shipped with it | Harmless. Those ranges are excluded from case selection.            |
| `witness.port` fails                          | no `claude` CLI or not authenticated                   | Only affects regeneration. Every result above uses committed ports. |
