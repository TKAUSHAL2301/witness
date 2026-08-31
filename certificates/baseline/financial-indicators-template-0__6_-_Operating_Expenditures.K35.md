# Equivalence certificate — `financial-indicators-template-0::6 - Operating Expenditures.K35`

## Verdict: **NOT EQUIVALENT**

| | |
| --- | --- |
| Target cell | `6 - Operating Expenditures.K35` |
| Workbook | `financial-indicators-template-0.xlsx` |
| Formula nodes behind it | 40 |
| Free inputs | 23 |
| Trials per seed | 3,000 |
| Seeds | 11, 23, 47 |
| Total input vectors tested | 9,000 |
| Numeric tolerance | rel 1e-9, abs 1e-6 |
| Generated | 2026-08-31 03:14 UTC |
| Python | 3.13.14 |

The port **disagrees** with the workbook. The smallest input vector that
reproduces the disagreement:

- First failing trial: **5**
- Excel returned: `-1.00465`
- The port returned: `-1.00468`
- Difference: **-0.00**
- Minimal differing inputs: `6 - Operating Expenditures!I35, 6 - Operating Expenditures!P51`

Full failing vector:

```json
{
  "6 - Operating Expenditures!H50": 22690243,
  "6 - Operating Expenditures!H51": 0,
  "6 - Operating Expenditures!I34": 1.019273868220529,
  "6 - Operating Expenditures!I35": 643.1349722723168,
  "6 - Operating Expenditures!I50": 3279382,
  "6 - Operating Expenditures!I51": 0,
  "6 - Operating Expenditures!J50": 8128547,
  "6 - Operating Expenditures!J51": 0,
  "6 - Operating Expenditures!K50": 3358161,
  "6 - Operating Expenditures!K51": 0,
  "6 - Operating Expenditures!L50": 2692665,
  "6 - Operating Expenditures!L51": 0,
  "6 - Operating Expenditures!M50": 1754128,
  "6 - Operating Expenditures!M51": 0,
  "6 - Operating Expenditures!N50": 659002,
  "6 - Operating Expenditures!N51": 0,
  "6 - Operating Expenditures!O50": 636052,
  "6 - Operating Expenditures!O51": 0,
  "6 - Operating Expenditures!P50": 531562,
  "6 - Operating Expenditures!P51": -339.224018669533,
  "6 - Operating Expenditures!Q50": 2017127,
  "6 - Operating Expenditures!Q51": 0,
  "6 - Operating Expenditures!R51": 0
}
```

## Coverage — what the trials actually exercised

Agreement on N vectors means little if every vector drove the
calculation down the same branch. Measured on the oracle:

| | |
| --- | --- |
| Formula cells in this target's cone | 6 |
| Cells whose value varied across sampling | **5 (83%)** |
| Cells constant for this input domain | 1 |

Cells that never varied — effectively constants over this domain:

- `6 - Operating Expenditures!R50`

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