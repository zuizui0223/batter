# Original-source seasonal geographic X: independent aggregate checks

**20 October 2026 — descriptive exploratory evidence only.** The already archived source-run JSON is checked for internal numerical and dyad-risk-set consistency. This review **does not independently download raw animal GPS** or verify biological co-location, and it is not a formal preregistration. Original source manifest MD5 checks were reported in the source-run artifact and the [source workflow](https://github.com/zuizui0223/batter/actions/runs/39382193098) concluded successfully.

Pinned source blob: `ad029188e4878ad8812ab72ea383bf93bc3e6e68`, source commit `c1c8d1116f814c2bb4b8adcb07f4b05cfd040a79`. No observed-row arithmetic or state-count contradictions: **0**.

## Unshifted 5 km geography; pair risk set matched across seasons

State counts in the last column are `00 / 10 / 01 / 11`: neither, first-season only, second-season only, both.

| Source | Year | Window | Animals | Dyads | First mean X | Second mean X | Difference | 00/10/01/11 |
|---|---:|---|---:|---:|---:|---:|---:|---|
| turkey | 2019 | winter_summer | 19 | 171 | 0.316919 | 0.224328 | 0.092591 | undefined/8/0/68 |
| turkey | 2019 | early_late | 31 | 465 | 0.292991 | 0.153783 | 0.139207 | undefined/12/2/165 |
| turkey | 2020 | winter_summer | 8 | 28 | 0.496194 | 0.212201 | 0.283993 | undefined/11/0/10 |
| turkey | 2020 | early_late | 9 | 36 | 0.534397 | 0.291468 | 0.242929 | undefined/0/0/28 |
| moose_snowy_range | 2019 | early_late | 22 | 231 | 0.029134 | 0.023696 | 0.005438 | undefined/5/6/15 |
| moose_snowy_range | 2020 | early_late | 16 | 120 | 0.015043 | 0.017871 | -0.002828 | undefined/4/7/5 |
| black_bear | 2019 | winter_summer | 2 | 1 | 0.000000 | 0.000000 | 0.000000 | undefined/0/0/0 |
| black_bear | 2020 | winter_summer | 17 | 118 | 0.031017 | 0.030495 | 0.000522 | undefined/1/10/7 |
| black_bear | 2020 | early_late | 13 | 78 | 0.035355 | 0.036729 | -0.001374 | undefined/0/3/4 |

Rows with no pair support are absent from this table, **not counted as zero effects**. `winter_summer` compares Dec/Jan/Feb against Jun/Jul/Aug within the same recorded year; `early_late` compares Jan/Feb against Mar/Apr. Source dates do not assert a verified UTC/GPS offset.

## Sensitivity to the full four widths × four origins

Counts are positive / negative / exactly zero across the **estimable** grid scenarios. Each scenario in a given study uses dependent pairs and must not be counted as an independent study.

| Source | Year | Window | + / − / 0 | Minimum difference | Maximum difference |
|---|---:|---|---|---:|---:|
| turkey | 2019 | winter_summer | 15/1/0 | -0.036471 | 0.174580 |
| turkey | 2019 | early_late | 16/0/0 | 0.058992 | 0.139207 |
| turkey | 2020 | winter_summer | 16/0/0 | 0.117701 | 0.392857 |
| turkey | 2020 | early_late | 16/0/0 | 0.167526 | 0.381125 |
| moose_snowy_range | 2019 | winter_summer | 0/0/0 | — | — |
| moose_snowy_range | 2019 | early_late | 12/4/0 | -0.003257 | 0.007896 |
| moose_snowy_range | 2020 | winter_summer | 0/0/0 | — | — |
| moose_snowy_range | 2020 | early_late | 4/12/0 | -0.009810 | 0.009469 |
| black_bear | 2019 | winter_summer | 0/1/15 | -0.032401 | 0.000000 |
| black_bear | 2019 | early_late | 0/0/0 | — | — |
| black_bear | 2020 | winter_summer | 9/7/0 | -0.016841 | 0.034283 |
| black_bear | 2020 | early_late | 8/8/0 | -0.010537 | 0.039942 |

## Interpretation and critical boundary

The black bear 2020 winter–summer 5-km source-wide **118 dyads** have 100 neither, 1 winter-only, 10 summer-only and 7 both-positive. Their mean change +0.000522 is the difference between a **−0.025519 incidence** and **+0.026041 conditional-positive-strength** contribution. This is an exact algebraic cancellation in observed discretized occupancy, **not a demonstrated behavioral compensation mechanism**. Nine of 16 grid settings yield a positive seasonal difference and seven negative; the sign is not robust to all spatial choices.

The turkey 2020 source-wide winter–summer 5-km comparison is positive on 28 supported pairs (8 birds), with 11 winter-only versus 0 summer-only pairs; all 16 grid/origin settings yield a positive mean difference. Turkey 2019 winter–summer is positive in 15/16 settings (171 pairs; 19 birds). The snow-range moose dataset has **no qualified winter–summer dyads** in either year; early-versus-late comparisons are weak and grid-dependent. A separate Bighorn Mountain moose source is **STOP** because source timestamps could not be parsed, not because ecological X was zero.

**Source reference site-label counts are zero across these packages.** The analysis therefore remains a **source-wide geometric comparison**, with some animals potentially in unrelated local populations; it is not evidence of interactions between members of a common population. A further individual-coordinate/site audit and sampling-cadence control is required before ecology claims. In addition, source datasets overlap with a 2026 publication's study family; DOI counts are not independent ecological replications. No cross-taxon R–X coupling, E (resource exposure), or T (encounter) has been measured here.

The earlier session summary values (e.g. turkey 2019 +0.1223, black bear 2020 +0.0002 and moose summer advantage) should not be cited as replications: their exact input cohorts were not saved, and the present reanalysis uses a different, explicitly supported pair risk set.
