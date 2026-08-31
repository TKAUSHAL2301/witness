# Equivalence certificate — `capital-targets-template::Debt.I8`

## Verdict: **NOT EQUIVALENT**

| | |
| --- | --- |
| Target cell | `Debt.I8` |
| Workbook | `capital-targets-template.xlsx` |
| Formula nodes behind it | 62 |
| Free inputs | 23 |
| Trials per seed | 3,000 |
| Seeds | 11, 23, 47 |
| Total input vectors tested | 9,000 |
| Numeric tolerance | rel 1e-9, abs 1e-6 |
| Generated | 2026-08-31 03:14 UTC |
| Python | 3.13.14 |

The port **disagrees** with the workbook. The smallest input vector that
reproduces the disagreement:

- First failing trial: **20**
- Excel returned: `970,327`
- The port returned: `970326`
- Difference: **-1.00**
- Minimal differing inputs: `Debt!I11, Debt!I15, Debt!I19, Debt!I24`

Full failing vector:

```json
{
  "Debt!I11": 0,
  "Debt!I12": 45000,
  "Debt!I13": 17000,
  "Debt!I14": 20000,
  "Debt!I15": -1,
  "Debt!I16": 0,
  "Debt!I19": 35984.5,
  "Debt!I22": 2000,
  "Debt!I23": 0,
  "Debt!I24": -1,
  "Debt!I31": 155000,
  "Debt!I32": 40000,
  "Debt!I33": 0,
  "Debt!I34": 338000,
  "Debt!I35": 85000,
  "Debt!I36": 0,
  "Debt!I37": 0,
  "Debt!I38": 0,
  "Debt!I41": 1743.75,
  "Debt!I43": 0,
  "Debt!I46": 0,
  "Debt!I47": 0,
  "Debt!I48": 0
}
```

## Coverage — what the trials actually exercised

Agreement on N vectors means little if every vector drove the
calculation down the same branch. Measured on the oracle:

| | |
| --- | --- |
| Formula cells in this target's cone | 14 |
| Cells whose value varied across sampling | **9 (64%)** |
| Cells constant for this input domain | 5 |

Cells that never varied — effectively constants over this domain:

- `Debt!I21`
- `Debt!I20`
- `Debt!I45`
- `Debt!I42`
- `Debt!I44`

## What this certificate does NOT cover

- **Only the target cell above.** Other outputs in this workbook are
  unexamined; a port correct here may be wrong elsewhere.
- **Only the declared input domain.** Inputs are sampled from types and
  boundary values inferred from the workbook. An input outside that domain
  has not been tested.
- **Sampling, not proof.** Agreement on N vectors is strong evidence, not a
  formal proof of equivalence over the whole input space.
- **The oracle is a re-implementation of Excel, not Excel.** It reproduced
  this workbook's own cached values exactly, which is why it is trusted here
  — but a function it computes differently from Excel would be invisible to
  this method. Cells depending on unsupported functions are refused, not
  passed.
- **Volatile functions excluded.** Targets depending on `NOW`, `TODAY`,
  `RAND`, `RANDBETWEEN`, `OFFSET` or `INDIRECT` cannot have a stable oracle
  and are rejected during case selection.

## Sign-off

This certificate is a recommendation to a qualified human reviewer. It is
**not** an authorization to cut over. The reviewer below owns that decision.

```
Reviewed by: ______________________________   Date: ______________

Role:        ______________________________

Accepted for production cut-over:   [ ] yes   [ ] no
```