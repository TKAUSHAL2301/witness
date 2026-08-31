# Equivalence certificate — `financial-forecasting-template-5-year::CPF.Q20`

## Verdict: **NOT EQUIVALENT**

| | |
| --- | --- |
| Target cell | `CPF.Q20` |
| Workbook | `financial-forecasting-template-5-year.xlsx` |
| Formula nodes behind it | 72 |
| Free inputs | 24 |
| Trials per seed | 3,000 |
| Seeds | 11, 23, 47 |
| Total input vectors tested | 9,000 |
| Numeric tolerance | rel 1e-9, abs 1e-6 |
| Generated | 2026-08-31 03:14 UTC |
| Python | 3.13.14 |

The port **disagrees** with the workbook. The smallest input vector that
reproduces the disagreement:

- First failing trial: **6**
- Excel returned: `''`
- The port returned: `-730.212`
- Minimal differing inputs: `CPF!G18, CPF!H18, CPF!I17, CPF!J18, CPF!R7`

Full failing vector:

```json
{
  "CPF!G16": 0,
  "CPF!G17": 0,
  "CPF!G18": -1,
  "CPF!G7": 0,
  "CPF!G8": 0,
  "CPF!G9": 0,
  "CPF!H16": 0,
  "CPF!H17": 0,
  "CPF!H18": -1477.9126759061398,
  "CPF!H7": 0,
  "CPF!H8": 0,
  "CPF!H9": 0,
  "CPF!I16": 0,
  "CPF!I17": -1,
  "CPF!I18": 0,
  "CPF!I7": 0,
  "CPF!I8": 0,
  "CPF!I9": 0,
  "CPF!J16": 0,
  "CPF!J17": 0,
  "CPF!J18": 3665.5480418993943,
  "CPF!R7": "",
  "CPF!R8": 0,
  "CPF!R9": 0
}
```

## Coverage — what the trials actually exercised

Agreement on N vectors means little if every vector drove the
calculation down the same branch. Measured on the oracle:

| | |
| --- | --- |
| Formula cells in this target's cone | 16 |
| Cells whose value varied across sampling | **16 (100%)** |
| Cells constant for this input domain | 0 |
| Branching cells (IF/IFS/CHOOSE) | 5 |
| Branches observed both ways | **5 (100%)** |
| Branches observed one way only | 0 |

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