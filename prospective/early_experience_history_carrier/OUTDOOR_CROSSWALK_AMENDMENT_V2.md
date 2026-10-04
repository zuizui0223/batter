# Outdoor GPS crosswalk amendment v2

## Status

**FROZEN AFTER V1 LINKAGE STOP AND BEFORE ANY NIGHTLY BEHAVIOURAL OUTCOME VALUE IS OPENED.**

V1 established:
- 19 Outdoor bats;
- >=10 unique dates in 8 enriched and 10 impoverished bats;
- exactly one Outdoor Origin missing (Yamit);
- the baseline table's `Individual` field is not the Outdoor name key, so exact-name linkage to that table is unavailable.

No nightly outcome value has been read.

## Independent public crosswalk table

`Exploraion in squares.xlsx`, sheet `Exploration`, has exactly 19 data rows and source-native headers:
- `Bat no.`
- `Name`
- `Season`
- `Sex`
- `Origin`
- `Colony`
- `Enrichment`

These identity/design fields are sufficient to test a direct crosswalk to the 19 Outdoor bats.

## Authorized row values

Read only:
- `Bat no.`
- `Name`
- `Season`
- `Sex`
- `Origin`
- `Colony`
- `Enrichment`

Do not read:
- No of squares on the grid;
- Total nights out;
- avg. squares per night;
- total in km2;
- average in km2;
- Max age;
- Boldness_B1;
- Explore_B1;
- Active_B1;
- any later column containing a behavioural result.

## Linkage rules

1. Match Outdoor `Bat_ID` to crosswalk `Name` by exact trimmed string.
2. Require a one-to-one match for all 19 Outdoor bats.
3. Require Outdoor `Environmental condition` to agree exactly in meaning with crosswalk `Enrichment`.
4. Existing non-missing Outdoor `Origin` must agree with crosswalk `Origin`.
5. Yamit's missing Outdoor Origin may be filled only from a unique non-missing crosswalk Origin.
6. Require one unique Season and Origin per bat.
7. Record the calendar-year ↔ source-Season crosswalk and require it to be one-to-one.

Any failure = STOP.

## Randomization blocks

If all checks pass, freeze:
`Season × Origin`

as the treatment-label randomization block for the prospective nightly-strategy analysis.

## Support floor

The later fixed-window primary may use only bats with >=10 unique Outdoor dates.

Require:
- >=5 enriched;
- >=5 impoverished.

No nightly behaviour value is authorized by this amendment.
