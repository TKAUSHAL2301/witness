All tests pass. The port correctly computes `Available Funds!T48`:

- **Formula chain**: `T48 = 'Fiscal Years'!S13`, where `S13 = EDATE(R13,12)`, chaining back 17 times to `B13`
- **Logic**: 17 successive `EDATE(_, 12)` calls — adds 17 years to the input date
- **Input**: `Fiscal Years!B13` (date as Excel serial `41821` = 2014-07-01)
- **Output**: Excel serial `48030` (= 2031-07-01) — matches the cached workbook value

The module handles serial numbers, date strings, floats, and `None` inputs correctly.