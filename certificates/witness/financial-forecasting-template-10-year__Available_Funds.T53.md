# Equivalence certificate — `financial-forecasting-template-10-year::Available Funds.T53`

## Verdict: **CERTIFIED EQUIVALENT**

| | |
| --- | --- |
| Target cell | `Available Funds.T53` |
| Workbook | `financial-forecasting-template-10-year.xlsx` |
| Formula nodes behind it | 37 |
| Free inputs | 1 |
| Trials per seed | 3,000 |
| Seeds | 11, 23, 47 |
| Total input vectors tested | 9,000 |
| Numeric tolerance | rel 1e-9, abs 1e-6 |
| Generated | 2026-08-31 03:14 UTC |
| Python | 3.13.14 |

Across **9,000 independently generated input vectors**, the
Python port and the workbook agreed on every one, within the stated
tolerance. The acceptance oracle is the workbook itself, recalculated by a
pure-Python engine that was first validated against the values Excel had
cached inside the file.

## Coverage — what the trials actually exercised

Agreement on N vectors means little if every vector drove the
calculation down the same branch. Measured on the oracle:

| | |
| --- | --- |
| Formula cells in this target's cone | 18 |
| Cells whose value varied across sampling | **18 (100%)** |
| Cells constant for this input domain | 0 |

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