# Prior work declaration (Ground Rule 02)

> "Make it clear what existed before the competition and what you added."

## Existed before this competition — not written by me

Third-party libraries, used under their own licences and unmodified:

| Component                                       | Licence    | Role                                             |
| ----------------------------------------------- | ---------- | ------------------------------------------------ |
| `openpyxl` 3.1.5                                | MIT        | Reads `.xlsx` formulas and Excel's cached values |
| `formulas` 1.3.4                                | EUPL-1.1+  | Pure-Python Excel recalculation engine           |
| `hypothesis` 6.165.10                           | MPL-2.0    | Property-based input generation and shrinking    |
| `numpy`, `scipy`, `schedula`, `numpy-financial` | BSD / EUPL | Transitive dependencies of `formulas`            |

Input data — public records, not authored by me:

| Source                         | Provenance                                                                                                                                                                                                     |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 17 municipal finance workbooks | Commonwealth of Massachusetts, Division of Local Services, published at `mass.gov/info-details/municipal-finance-tools-templates-calculators`. Downloaded 2026-08-29 (14 workbooks, commit `494343f`) and 2026-08-30 (3 more, commit `5442840`). Public records of a US state government. |

All 3 workbooks added on 2026-08-30 turned out to contain **no formula cells**, so
they contribute no evaluation cases; the 37 cases come from 7 of the original 14.
They are kept in `corpus/` because the engine-trust gate reports on all 17 and the
exclusion is meant to be visible rather than tidied away.

## Written during the competition — mine

Everything under `src/witness/`, the evaluation harness, the corpus manifest,
the agent instructions, and all documentation.

The repository was created empty at **2026-08-29T11:05:31Z**, after the
hackathon kickoff (2026-08-28T15:00Z). `git log` timestamps are the evidence;
there is no pre-existing history and no squashed or backdated commits.
