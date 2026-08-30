# Equivalence certificate — `capital-targets-template::Debt.H8`

## Verdict: **NOT EQUIVALENT**

| | |
| --- | --- |
| Target cell | `Debt.H8` |
| Workbook | `capital-targets-template.xlsx` |
| Formula nodes behind it | 64 |
| Free inputs | 21 |
| Trials per seed | 10,000 |
| Seeds | 11, 23, 47 |
| Total input vectors tested | 30,000 |
| Numeric tolerance | rel 1e-9, abs 1e-6 |
| Generated | 2026-08-30 14:28 UTC |
| Python | 3.13.14 |

The port **disagrees** with the workbook. The smallest input vector that
reproduces the disagreement:

- First failing trial: **10**
- Excel returned: `101,089`
- The port returned: `101090`
- Difference: **1.00**
- Minimal differing inputs: `Debt!H31, Debt!H34, Debt!H35, Debt!H36, Debt!H43, Debt!H47`

Full failing vector:

```json
{
  "Debt!H11": 54620.89,
  "Debt!H12": 45000,
  "Debt!H13": 17000,
  "Debt!H14": 0,
  "Debt!H15": 0,
  "Debt!H16": 0,
  "Debt!H19": 19379.11,
  "Debt!H22": 0,
  "Debt!H23": 0,
  "Debt!H24": 0,
  "Debt!H31": -155000,
  "Debt!H32": 40000,
  "Debt!H33": 0,
  "Debt!H34": null,
  "Debt!H35": -85000,
  "Debt!H36": -100000,
  "Debt!H37": 0,
  "Debt!H38": 0,
  "Debt!H43": 1,
  "Debt!H47": 1,
  "Debt!H48": 0
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