# Early-experience structural row-value allowlist v1

## Status

**FROZEN BEFORE NIGHTLY BEHAVIOURAL OUTCOME VALUES ARE READ.**

Parent:
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- `SCHEMA_FILE_OPENING_ALLOWLIST_V1.md`
- `BIOLOGICAL_CONTRAST_CONTRACT_V1.md`

## Primary structural table

File:
`Outdoor data.xlsx`

Sheet:
`exit_time_temp_new`

Authorized row-value columns only:
- `Bat_ID`
- `Sex`
- `Environmental condition`
- `Origin`
- `Date`
- `NumberDaysOut`
- `Age (days)`

Explicitly forbidden at this gate:
- `Time Out (Minute)`
- `Max distance (meters)`
- `Explored area`

## Season definition

The source experiment has two seasons.

For this structural audit:
- derive calendar year from `Date`;
- if all GPS rows fall in exactly two year values corresponding to the two source seasons, use year as the reproducible season block;
- otherwise STOP randomization-block adjudication and freeze a new linkage rule before any outcome opening.

No behavioural outcome may be used to define season.

## Structural counts

Report:
- unique bats;
- unique bats by environmental condition;
- nights per bat;
- unique years;
- condition × year × origin cell counts;
- number of bats in each treatment with >=10 unique dates;
- exact treatment vocabulary.

## Frozen minimum

Proceed only if:
- >=5 enriched bats have >=10 unique dates;
- >=5 impoverished bats have >=10 unique dates.

If either arm fails:
**STOP**.

## Randomization-block candidate

If source-consistent support exists, the preferred randomization block is:

`calendar year × Origin`

because:
- treatment assignment was randomized after baseline;
- the source explicitly balanced bats from origin colonies between environmental conditions;
- calendar year indexes the two experimental seasons.

The exact observed block table must be recorded before outcome values are opened.

## No-outcome rule

Do not calculate any summary of:
- time out;
- maximum distance;
- explored area;
- repeatability;
- self-history prediction;
- treatment effect.
