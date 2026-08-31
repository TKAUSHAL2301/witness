# Agent trajectory 2 — the port agent

**Agent:** Claude Code in headless mode (`claude -p`), same model.
**Role:** writes the candidate Python port for one target cell.

## What the agent receives

The **baseline arm** gets the workbook path, the target cell, the input list,
and one instruction — *"read the workbook, work out what the target computes,
check your work however you think best."* It has Read/Bash/Glob/Grep.

The **Witness arm** gets no file access at all. It gets the extracted formula
cone, a typed domain per input, and then — on failure — **only this**:

```json
{
  "failing_inputs": {
    "'Sheet'!B4": null,
    "'Sheet'!C7": 0
  },
  "excel_returned": 2481003.11,
  "your_port_returned": 1286441.02,
  "minimal_differing_inputs": "'Sheet'!B4"
}
```

No critique. No explanation. No hint about *why* it is wrong. The shrunk
counterexample is the entire repair signal, and that constraint is the
subject of the ablation in `CHANGELOG.md`.

## Observed repair loops

Repair histories are shown for **28 of the 37 cases**. The other 9 reused a port
that already existed from an earlier generation run (`[skip] … exists` in
`results/portgen_v3.log`), so there is no loop to render for them. The
`certified` column is the port agent's own verdict at generation time, at 2,000
trials — **not** the reported result. The reported result is `pass^3000` across
3 seeds, and per-case verdicts for all 37 cases are in `certificates/witness/`,
where the Witness arm certified 32 of 37.


### `appropriation-template::Annual.D31`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `appropriation-template::Annual.E31`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `appropriation-template::Annual.F31`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `appropriation-template::Annual.H31`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `appropriation-template::Annual.I31`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `appropriation-template::Impact.C33`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `budget-and-tax-rate-planning-tool::Levy Limit.E31`

| attempt | trials survived | certified |
| --- | --- | --- |
| 2 | 2000/2000 | yes |

### `budget-and-tax-rate-planning-tool::Recap Page 2.L22`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 1/2 | no |
| 1 | 2000/2000 | yes |

### `budget-and-tax-rate-planning-tool::Levy Limit.E19`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 3/4 | no |
| 1 | 2000/2000 | yes |

### `capital-planning-and-budgeting-workbook::Financial Targets.F60`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `capital-planning-and-budgeting-workbook::Financial Targets.J60`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `capital-planning-and-budgeting-workbook::Financial Targets.F41`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `capital-targets-template::Amortization.B48`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `capital-targets-template::Amortization.A48`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `capital-targets-template::Debt.I8`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 20/21 | no |
| 1 | 2000/2000 | yes |

### `capital-targets-template::Debt.J8`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `financial-forecasting-template-10-year::COLA.J122`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 37/38 | no |
| 1 | 2000/2000 | yes |

### `financial-forecasting-template-10-year::Available Funds.T53`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 0/1 | no |
| 1 | 4/5 | no |
| 2 | 2000/2000 | yes |

### `financial-forecasting-template-10-year::Available Funds.S48`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 4/5 | no |
| 1 | 2000/2000 | yes |

### `financial-forecasting-template-5-year::COLA.J122`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `financial-forecasting-template-5-year::CPF.Q20`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 6/7 | no |
| 1 | 7/8 | no |

### `financial-forecasting-template-5-year::Available Funds.M48`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 0/1 | no |
| 1 | 4/5 | no |
| 2 | 2000/2000 | yes |

### `financial-forecasting-template-5-year::Available Funds.M53`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 0/1 | no |
| 1 | 1/2 | no |
| 2 | 4/5 | no |

### `financial-indicators-template-0::6 - Operating Expenditures.K36`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `financial-indicators-template-0::6 - Operating Expenditures.K37`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `financial-indicators-template-0::6 - Operating Expenditures.K38`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `financial-indicators-template-0::6 - Operating Expenditures.K39`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |

### `financial-indicators-template-0::10 - Debt Service.P31`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | 2000/2000 | yes |
