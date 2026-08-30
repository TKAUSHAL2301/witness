# Equivalence certificate — `financial-forecasting-template-10-year::Available Funds.T48`

## Verdict: **NOT EQUIVALENT**

| | |
| --- | --- |
| Target cell | `Available Funds.T48` |
| Workbook | `financial-forecasting-template-10-year.xlsx` |
| Formula nodes behind it | 37 |
| Free inputs | 1 |
| Trials per seed | 10,000 |
| Seeds | 11, 23, 47 |
| Total input vectors tested | 30,000 |
| Numeric tolerance | rel 1e-9, abs 1e-6 |
| Generated | 2026-08-30 14:28 UTC |
| Python | 3.13.14 |

The port **disagrees** with the workbook. The smallest input vector that
reproduces the disagreement:

- First failing trial: **0**
- Excel returned: `48030`
- The port returned: `None`
- Difference: **-48,030.00**
- Minimal differing inputs: `(baseline inputs)`

Full failing vector:

```json
{
  "Fiscal Years!B13": "2014-07-01 00:00:00"
}
```

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