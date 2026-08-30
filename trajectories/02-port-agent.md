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

### `budget-and-tax-rate-planning-tool__Recap_Page_2.L52`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | -/2000 | yes |

### `financial-forecasting-template-10-year__Fiscal_Years.AA13`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | -/2000 | no |
| 1 | -/2000 | no |
| 2 | -/2000 | yes |

### `financial-forecasting-template-10-year__Fiscal_Years.AA16`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | -/2000 | no |
| 1 | -/2000 | no |
| 2 | -/2000 | no |
| 3 | -/2000 | no |

### `financial-forecasting-template-5-year__Available_Funds.N53`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | -/2000 | no |
| 1 | -/2000 | no |
| 2 | -/2000 | no |
| 3 | -/2000 | no |

### `financial-indicators-template-0__6_-_Operating_Expenditures.K35`

| attempt | trials survived | certified |
| --- | --- | --- |
| 0 | -/2000 | yes |
