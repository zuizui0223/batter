# Aharon Figure-1 finite-mask audit v2

## Status

**STRUCTURAL NUMERIC-MASK AUDIT ONLY. TURNING MAGNITUDES FORBIDDEN.**

May run only if `AHARON_FIGURE1_STRUCTURE_V2.json` is PASS.

For every bat × condition matrix column:
- valid right side = >=1 finite value among source odd-numbered rows;
- valid left side = >=1 finite value among source even-numbered rows;
- valid trial = both sides valid.

Report only:
- matrix rows/columns;
- count of valid trial columns;
- count of invalid trial columns.

Do not report:
- medians;
- means;
- ranges;
- nonzero magnitudes;
- bat differences;
- condition differences.

PASS requires >=5 valid columns in all 12 cells.
