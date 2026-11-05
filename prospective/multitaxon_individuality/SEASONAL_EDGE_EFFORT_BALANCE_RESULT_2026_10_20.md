# Same-day GPS-effort standardized seasonal geographic sharing across published animal tracking sources

**2026-10-20. Original-data executed, post-inspection exploratory sensitivity.**
Code and previously fixed sampling design:
[SEASONAL_EDGE_OBSERVATION_BALANCE_DESIGN_2026_10_20.md](SEASONAL_EDGE_OBSERVATION_BALANCE_DESIGN_2026_10_20.md).
Original full-Movebank GPS files and reference tables were fetched in GitHub
Actions from the publisher and independently checked against original MD5,
previously pinned SHA256 and the exact 2019–2020 V2 source-event QC. No raw
animal IDs, exact dates, coordinates or tracking records were committed.

**The central observed ecological pattern is not a universal winter/summer
mean-overlap effect. Instead, the fraction of spatially overlapping dyads
and the strength of overlap among positive dyads may change in opposite
directions.** This configuration survives the declared observation-count
equalization at 5 km for black bears and white-tailed deer, although the
full-grid conclusions need the more restrictive caveats below.

## 1. What this new test controls

Every dyad is compared using its own **same seven observed calendar dates
in each of exactly two months per season**. On a selected date, each partner
contributes exactly **one or two original GPS fixes**. There are **24
checksum-seeded, reproducible draws** for each fix number and each grid.
The primary grid is 5 km at origin (0,0); the declared spatial
sensitivities are 1 km origin (0,0), 5 km with a half-cell shift on both
axes, and 10 km origin (0,0).

Winter is Jan/Feb/Dec *within the same source calendar year*, not a
chronologically continuous winter interval; summer is Jun/Jul/Aug.
A dyad needs seven pair-common observed dates in at least two months
in each season and must have annual utilization centroids ≤25 km apart.
This is a post-inspection geometric opportunity proxy, NOT proof of
one local biological population. None of the three source reference
tables provides a usable verified individual-group label.

The 1-fix eligibility masks **exactly reproduce** the prior source
V2 masks in all six source/year combinations, including one
not-estimable black-bear 2019 dyad. At two fixes/day, bear 2020 drops
from 104 to 69 supported pairs (66.3% retained); the other estimable
cohorts retain all pairs. The k=2 contrast is thus NOT a same-risk-set
paired effect against k=1 for bear 2020.

## 2. Original GPS source receipts and sample sizes

| Movebank source | DOI | Fully verified GPS fixes (2019–2020) | Original animal-dates | Median fixes/animal-date |
|---|---|---:|---:|---:|
| Wild turkey (*Meleagris gallopavo*) | [10.5441/001/1.671](https://doi.org/10.5441/001/1.671) | 435,214 | 26,851 | 17 |
| Black bear (*Ursus americanus*) | [10.5441/001/1.706](https://doi.org/10.5441/001/1.706) | 148,394 | 12,024 | 9 |
| White-tailed deer (*Odocoileus virginianus*) | [10.5441/001/1.718](https://doi.org/10.5441/001/1.718) | 371,080 | 15,648 | 24 |

All sources passed full original-file MD5, size, pinned SHA256, and
original event/reference/QC equality. These are not equal animal counts,
populations, habitats or annual sample designs.

## 3. Five estimable year cohorts at the 5-km reference grid

The following values are the *means across 24 sampling configurations*;
they are not population point estimates corrected for source sampling
bias, confidence intervals or independent replications. Define
\(p =\) fraction of fixed dyads with positive sampled geographic X and
\(m_+ =\) mean X among positive dyads. As before,
\(\Delta\bar X = (p_W-p_S)(m_W+m_S)/2 +
(m_W-m_S)(p_W+p_S)/2\).
The first and second terms below are these **descriptive, algebraic**
incidence and conditional-strength contributions.

| Source/year | Eligible dyads k=1/k=2 | k=1 winter–summer mean X | k=1 incidence term | k=1 conditional-strength term |
|---|---:|---:|---:|---:|
| Turkey 2019 | 112 / 112 | +0.14203 | +0.07925 | +0.06278 |
| Turkey 2020 | 21 / 21 | +0.36990 | +0.52258 | −0.15268 |
| Bear 2020 | 104 / 69 | +0.00097 | −0.01743 | +0.01840 |
| White-tailed deer 2019 | 55 / 55 | +0.00265 | +0.03168 | −0.02903 |
| White-tailed deer 2020 | 205 / 205 | +0.00616 | +0.03739 | −0.03124 |

**Turkey 2019**: at 5 km the incidence, conditional strength, and
total mean X winter–summer differences are all positive for **24/24**
one-fix draws and **24/24** two-fix draws. Both components are
positive across the four declared grids and both fix rates.

**Turkey 2020**: the winter mean X and incidence contribution are
positive in every one of the 24 draws for both fix settings and all
four grids. But conditional positive-overlap *strength* is
**summer-biased** at the unshifted 1, 5, 10-km grids, while it becomes
**winter-biased** at the half-shifted 5-km grid. Thus the old statement
that changes in intensity have a universally known direction would
be wrong; a more stable seasonal pattern concerns the presence of
positive spatial-overlap edges and the total reference-grid mean.

**Black bear 2020**: the unshifted 5-km incidence term is
negative (summer has more positive-overlap dyads) for **24/24**
one-fix and two-fix draws; the conditional positive-overlap
strength term is positive (winter has stronger positive overlap)
for **24/24** draws. At k=1, the mean X contrast is positive in
11 draws, negative in 12 and near zero in 1. This is strong
evidence **against** a confidently signed seasonal change in
*mean* geographic overlap from this source. The opposite component
signs remain for the shifted 5-km and 10-km grid. At 1 km the
incidence sign is not stable (3 positive, 13 negative, 8
near-zero k=1 draws). An all-resolution universal incidence rule is
NOT supported. With two fixes/day, bear retained dyads drop to 69;
the same opposite component directions survive in all 24 5-km
draws conditional on those 69 dyads, but the magnitude must not be
compared as a same-cohort effect.

**White-tailed deer 2019**: the 5-km incidence contribution is
positive in 22/24 one-fix draws (2 near zero), while positive-overlap
strength is negative in 23/24 draws. The mean difference changes sign
with the grid, so avoid a universal mean-overlap claim.

**White-tailed deer 2020**: strongest same-source structural result.
The incidence contribution is **positive and the conditional
strength contribution is negative in all 24 draws at every one of
the four declared spatial grids, using both one and two fixes/day**.
The total winter–summer mean X contrast, however, is **positive
at 5 km without origin shift and negative at 1 km, shifted 5 km
and 10 km**. This is a concrete case of grid-dependent average
overlap coexisting with opposed, stable component signs.

### A further boundary: apparent pair persistence changes with observation effort

The exact *same original eligible pairs* are carried into k=1 sampling,
but the number of evaluated months, common dates and fixes per day is
standardized. The Jaccard index of active spatial-overlap dyads
(positive in both seasons / positive in either season) changes:

| Source/year | Original V2 geographic edge Jaccard | Equal-effort k=1 average across 24 draws |
|---|---:|---:|
| Turkey 2019 | 0.895 | 0.821 |
| Turkey 2020 | 0.476 | 0.313 |
| Black bear 2020 | 0.389 | 0.540 |
| White-tailed deer 2019 | 0.467 | 0.675 |
| White-tailed deer 2020 | 0.667 | 0.670 |

This is evidence that an estimated *edge-retention value* is itself
observation-protocol dependent even if key signs of the incidence/strength
decomposition persist. It is **not** an isolated causal effect of fix
frequency: the standardization changes months and pair-shared dates in
addition to fixes per day. No Jaccard persistence constant should be
compared across species without matching observation support. This
restriction is consistent with previously established general concerns
about tracking sampling and space-use estimation, e.g.
[Terayama et al. 2023](https://doi.org/10.1155/2023/1384365) and
[He et al. 2023](https://doi.org/10.1111/2041-210X.13999).
Seasonally different overlap *number and strength* are also not
conceptually unprecedented (e.g.
[wild-pig GPS study, 2022](https://doi.org/10.1038/s41598-022-07297-y)).
Our independent addition is the transparent, cross-source,
observation-matched numerical configuration comparison.

## 4. What observation balancing does NOT solve

A positive edge simply means overlap of sampled 2D GPS cell-usage
distributions. The number of positive edges is sensitive to cell
size, fix count, missing observation dates, temporal placement of
GPS fixes, location error, and chance overlap in accessible habitats.
Exactly equal per-date/per-month counts remove a narrow observation
effort imbalance but **do not estimate undetected use, true co-presence
or actual joint spatial availability**. The 24 draws are dependent
from each same finite GPS archive and measure finite-source sampling
sensitivity only.

All dyads within a year share individual animals, and source years
may reuse the same animals. Seasonal pooling treats Dec/Jan/Feb
within a calendar year as one categorical season, not a connected
overwintering sequence. No source-specific verified group/colony or
within-source local population labels were available, so a 25-km
centroid rule is not sufficient to infer population membership.
Taxa have different geographical ranges and deployment schemes.
These contrasts cannot yet establish social association, diet
partitioning, resource exposure E, actual encounters T, or
behavioral-decision identity R, nor a universal seasonal
specialization mechanism or ecological threshold.

## 5. Reproduction, independent checks and durable outputs

Source-verified original-GPS execution:
[GitHub Actions run 39407212721](https://github.com/zuizui0223/batter/actions/runs/39407212721),
four jobs PASS (synthetic contracts and three source-matrix jobs).

Fixed [design](SEASONAL_EDGE_OBSERVATION_BALANCE_DESIGN_2026_10_20.md),
[executable original-source pipeline](seasonal_edge_observation_balance_v1.py),
[synthetic contracts](tests/test_seasonal_edge_observation_balance_v1.py).
Stored full, **aggregate-only** seed×grid results:
[turkey](SEASONAL_EDGE_EFFORT_BALANCED_TURKEY_2026_10_20.json),
[bear](SEASONAL_EDGE_EFFORT_BALANCED_BLACK_BEAR_2026_10_20.json),
[white-tailed deer](SEASONAL_EDGE_EFFORT_BALANCED_WHITE_TAILED_DEER_2026_10_20.json).
The upload/publication workflow also enforces the **three exact source
result SHA256s, original cohort counts, 24-seed/four-grid completion and
an aggregate-only output schema**. The independent
[archive/result validator](validate_seasonal_effort_output_v1.py)
recalculates each seed's dyad-state partition, incidence/strength
identity, Jaccard, null handling and saved 24-draw summaries.
Raw original data were downloaded only to temporary GitHub Actions
runners, not exported to the research branch.

## Scientific synthesis

The strongest current descriptive contribution is a **configuration-based
comparison**, not evidence that one universal winter-sharing rule applies
across taxa. White-tailed deer 2020 and black bear 2020 provide two
different spatial-sharing configurations whose incidence and conditional
intensity contributions oppose at the primary grid after observed
GPS effort is standardized. Turkey 2020 shows winter expansion in
positive-overlap dyads despite an intensity component whose sign
depends on grid placement. These are empirical **boundaries on the
interpretation of pairwise mean geographic overlap**, not a new
causal theory of ecological niche partitioning.

**Next biological gate:** corroborate source study/local-population
membership and model fix-detection/precision processes with independent
data; independently test R, X, T and E rather than labelling all 2D X
as social or resource partitioning.
