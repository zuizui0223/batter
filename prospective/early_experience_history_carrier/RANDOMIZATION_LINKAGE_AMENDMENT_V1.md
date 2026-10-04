# Randomization-block linkage amendment v1

## Status

**FROZEN AFTER THE OUTCOME-BLIND OUTDOOR STRUCTURAL GATE AND BEFORE ANY NIGHTLY BEHAVIOURAL OUTCOME VALUE IS OPENED.**

The first structural run passed replication support but returned
`STOP_STRUCTURAL_SUPPORT_OR_LINKAGE`
because exactly one GPS bat, `Yamit`, had missing `Origin` in `Outdoor data.xlsx`.

No value from:
- Time Out (Minute);
- Max distance (meters);
- Explored area

has been read.

## Why a linkage check is admissible

The public dataset contains an independent baseline/personality table with source-native fields:
- `Bat_no`;
- `Individual`;
- `Season`;
- `Origin`;
- `Colony`;
- `Colony type`.

These headers were opened before this amendment.

Recovering a missing source-defined randomization/block variable from that table does not use or condition on the prospective nightly behavioural outcome.

## Authorized row values

From:
`All seasons personality data.xlsx`, sheet `Full_Data`

read only:
- `Bat_no`
- `Individual`
- `Season`
- `Origin`
- `Colony`
- `Colony type`

Do not read any baseline behavioural response, including:
- time2exit;
- time2explore;
- time2action;
- ActiveTime_Sec;
- Boldness;
- boxes_activity;
- boxes_all_enter;
- AllActivityNormed;
- ExpuNIQUE.

## Linkage rule

1. Match Outdoor `Bat_ID` to baseline `Individual` by exact trimmed string.
2. If an Outdoor bat has exactly one non-missing source-native `Origin` and `Season` across its baseline rows, record them.
3. Existing non-missing Outdoor origins must agree with baseline Origin.
4. Outdoor calendar year must map one-to-one to baseline Season across bats with both values.
5. The missing Yamit Origin may be filled only if Yamit has one unique non-missing baseline Origin.
6. Any conflict or ambiguity = STOP.

## Block definition if linkage passes

Use source-native:
`Season × Origin`

for treatment-label randomization blocks.

Calendar year remains only an audit crosswalk and is not the final block variable.

## Support rule

After linkage, retain the existing frozen support floor:
- >=5 enriched bats with >=10 unique Outdoor dates;
- >=5 impoverished bats with >=10 unique Outdoor dates.

A bat with <10 dates remains structurally ineligible for the later fixed-window primary.

## No outcome opening

This amendment authorizes no nightly behavioural outcome value and no treatment contrast.
