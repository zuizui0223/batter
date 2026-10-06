# Missing-data and attrition rule v1

## Status

**PROSPECTIVE FAIL-CLOSED RULE.**

Applies after capability screening and treatment randomization.

## Primary paired completeness

An animal is primary-complete only if it has the frozen valid common-OPEN probe in **both** matched families.

No one-family primary contribution is allowed.

## Block completeness

The restricted randomization uses four-animal blocks.

A block is confirmatory-complete only if all four randomized animals are primary-complete.

If any animal in a block lacks either family-specific primary probe outcome:
- the entire block is excluded from the confirmatory randomization analysis;
- the incomplete block remains fully documented;
- no replacement animal is inserted into that already-randomized block;
- no partial-block randomization rescue is allowed.

## Minimum retained support

Confirmatory P1/P2 can open only with:
- >=4 complete randomized blocks;
- >=16 primary-complete animals.

Otherwise:
**STRUCTURAL STOP**.

## Attrition reporting

For every randomized animal report:
- block;
- treatment-family assignment;
- acquisition-start order;
- completion of A acquisition;
- completion of B acquisition;
- completion of A common probe;
- completion of B common probe;
- reason for missingness if any;
- whether the reason occurred before or after treatment exposure.

## Sensitivity boundary

If any randomized block is lost after treatment exposure, label the confirmatory result with an **attrition sensitivity limitation**, even if >=4 complete blocks remain.

Do not perform:
- per-animal complete-case rescue outside the block rule;
- best-case/worst-case outcome imputation as a new primary;
- treatment-specific exclusion;
- replacement of missing trials after viewing route identity.

A predeclared descriptive attrition table is allowed.

## Trial-level missingness

Within an otherwise complete probe:
- only structurally valid trials under the frozen tracking rule are scored;
- the exact minimum valid trial count per individual × family must be frozen in the engineering receipt;
- if that minimum is not met, the animal is not primary-complete and the block rule above applies.

## Rationale

Whole-block fail-closed handling preserves the restricted randomization structure better than post-outcome removal of individual animals.

It does not prove that attrition is ignorable; therefore any post-treatment block loss remains an explicit limitation.