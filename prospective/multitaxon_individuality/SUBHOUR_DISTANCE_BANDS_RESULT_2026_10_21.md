# Fine-distance redistribution of source-GPS time-matched proximity

**Empirical comparative source-aggregate analysis — 21 October 2026.**
**POST-INSPECTION exploratory analysis**, NOT independent preregistration
and NOT a biological social-encounter or avoidance test.

## Main ecological observation

**The seasonal prevalence of spatial proximity and the seasonality of
proximity's source-clock matching are different empirical dimensions.**
In published white-tailed deer GPS data, *fewer* original time-matched
fix pairs lie within 500 m in winter than in summer, yet the
within-day clock-matching surplus (relative to reassigning that day's
three observed positions among recorded time slots) is *higher* in
winter at ≤500 m. Simultaneously, original GPS matches in the
1–2 km distance band show a *negative* clock-matching surplus in winter.

This pattern is also present in different form in wild turkeys,
where absolute winter 500-m proximity is much more common.
It is **not stable in black bears** under changing time tolerance
and the resulting sample eligibility. All observations are confined
to particular published GPS source studies, not independent
populations across clades.

## Inputs and methodological distinction

This result is derived algebraically from the **previously committed,
publisher-MD5/original-SHA256-verified GPS source aggregates**:
- [wild turkey DOI 10.5441/001/1.671](https://doi.org/10.5441/001/1.671)
- [American black bear DOI 10.5441/001/1.706](https://doi.org/10.5441/001/1.706)
- [white-tailed deer DOI 10.5441/001/1.718](https://doi.org/10.5441/001/1.718).

The original GPS (954,688 quality-retained 2019–2020 fixes across
these three sources) was checked in the preceding sub-hour original
analysis, with exact independent positional/time multiset confirmation.
**This turn reuses those verified aggregates, not a newly downloaded
or independently tracked sample.**

Original fixed sampling: for each eligible source-year dyad, exactly
three GPS-fix pairs within ±15 min (primary) or ±30 min (secondary)
on seven pair-shared observed dates in each of two months per
calendar-season category; twelve SHA256-deterministic sample draws;
one-to-one pairing without reuse. Winter means the Jan/Feb/Dec
months **of the same calendar year**, not a continuous
chronologically adjacent winter. Annual GPS-use centroids ≤25 km
apart establish geometric restriction but **not** biological
same-population membership.

For each source/year/tolerance/seed/season, the earlier cumulative
quantities were:
- O(r): observed fraction of the three actual matched GPS fix pairs
  within haversine radius r
- N(r): expected fraction within r after independently permuting the
  pair assignments among those *same three recorded positions/time slots*
  within each observed date
- D(r)=O(r)−N(r): conditional clock-matching surplus. This is an
  algebraic reference, **not an exchangeable biological null or p-value**.

We now express O and N in four **nonoverlapping** spatial bands:
**[0, 0.5] km, (0.5, 1] km, (1, 2] km, (2, ∞) km**, and derive
D_B=O_B−N_B. For each original seed/season, Σ_B O_B=Σ_B N_B=1
and **Σ_B D_B=0**. A positive near-band surplus thus requires an
offset elsewhere *by construction*, but the particular offset distance
does not follow from that identity. Neither positive D_B nor negative
D_B proves social attraction/repulsion.

## 1. All five eligible cohorts: winter-minus-summer D by disjoint band

**Primary ±15-minute GPS time-matching window** and averages over
the same 12 dependent within-source fix subsamples.

| Source, year | Matched dyads | ≤500 m ΔD | 500 m–1 km ΔD | 1–2 km ΔD | >2 km ΔD |
|---|---:|---:|---:|---:|---:|
| Wild turkey 2019 | 112 | +0.014255 | −0.011686 | −0.001583 | −0.000986 |
| Wild turkey 2020 | 21 | +0.028565 | −0.018330 | −0.008440 | −0.001795 |
| Black bear 2020 | 38 | −0.001131 | +0.000661 | −0.000209 | +0.000679 |
| White-tailed deer 2019 | 55 | +0.005195 | −0.002140 | −0.007696 | +0.004642 |
| White-tailed deer 2020 | 205 | +0.003294 | −0.000923 | −0.004197 | +0.001826 |

Columns are proportions, so 0.005195 means **0.5195 percentage
points** in winter−summer difference of conditional source-clock
surplus (NOT an absolute animal encounter probability). Values in
each row sum to zero to floating/rounding precision by the four-band
partition identity. Black bear 2019 did not meet the predeclared
source time-pair support threshold and remains **NOT ESTIMABLE** at
both time tolerances.

### White-tailed deer: absolute near-position rate versus time alignment

| Source-year | Observed ≤500 m winter | Observed ≤500 m summer | ≤500 m D winter | ≤500 m D summer | 1–2 km D winter |
|---|---:|---:|---:|---:|---:|
| White-tailed deer 2019 | 0.03276 | 0.04098 | +0.00415 | −0.00105 | −0.00814 |
| White-tailed deer 2020 | 0.02604 | 0.03471 | +0.00345 | +0.00015 | −0.00438 |

**Absolute 500-m nearby-position use is lower in winter**, but the
*relative clock alignment of those positions*, conditional on same-day
recorded positions and time slots, is more enriched in winter.
Separately, the 1–2 km band in winter is less represented at matching
times than under the within-day position/time reassignment reference.

The source-geography interpretation is therefore **not**
"winter animals meet each other more often" or "they avoid each
other at 1–2 km." This is a more specific observation about the
joint distribution of original-GPS distance and matched source
recording time, conditional on already sampled places.

### Turkey shows a related conditional direction but contrasting prevalence

Turkey 2019/2020 show **higher winter absolute** ≤500 m observed
near-position fractions (0.250 vs 0.054, and 0.560 vs 0.188)
*and* positive winter near-band time-alignment surplus relative
to the within-day reassignment reference. The comparable deer
absolute pattern is reversed (summer > winter). Thus the repeated
positive winter *relative* 500-m direction in these two named
taxa does **not** imply a shared mechanism or a common absolute
seasonal proximity change. The conditional reweighting remains
source-specific and observational.

Black bear 2020 has a near-band winter−summer D of −0.001131
at ±15 min (11/12 seed draws negative) but +0.000169 at
±30 min (7 positive, 1 negative, 4 near zero). Critically the
bear dyad risk set changes **38 → 47** when the allowed
fix-time mismatch is expanded. These comparisons are NOT a
single fixed-pair temporal sensitivity. There is **no supported
stable black-bear sign** for the near-band time surplus.

## 2. Transparent draw and time-tolerance sensitivity

Each count below is the number of deterministic within-source
draws out of 12 where winter-minus-summer D has the stated sign,
*not independent biological replication or a p-value*.

| Source/year | ≤500 m positive, ±15 / ±30 min | 1–2 km negative, ±15 / ±30 min |
|---|---|---|
| Turkey 2019 | 12/12 · 12/12 | 10/12 · 9/12 |
| Turkey 2020 | 12/12 · 12/12 | 12/12 · 12/12 |
| Black bear 2020 | 1/12 · 7/12 | 7/12 · 12/12 |
| White-tailed deer 2019 | 12/12 · 12/12 | 12/12 · **11/12** |
| White-tailed deer 2020 | 12/12 · 12/12 | 12/12 · 12/12 |

**Necessary qualification:** in deer 2019, widening the allowed
time gap from 15 to 30 min yields **11/12** rather than
12/12 negative winter−summer 1–2 km draw contrasts. This
exception was caught by CI and retained *without editing the
underlying source results*. Likewise turkey 2019's 1–2 km
direction is not invariant over all draws.

The 500-m and 1–2 km emphasis was selected **after inspecting
earlier cumulative-radius outputs**. The four-band endpoint
choices and full inclusion of bear and all 900/1800-second source
comparisons were documented in the
[frozen post-inspection design](DISTANCE_BAND_CLOCK_ALIGNMENT_DESIGN_2026_10_21.md)
before the additional derived artifact was published. No
hypothesis-test or taxon-general threshold is claimed.

## 3. Verification and fully inspectable results

- [Source/time-band aggregation Python](distance_band_from_subhour_v1.py)
  requires **exact previously pinned SHA256** for all three source
  aggregate JSONs and original source status flags. It uses no
  original tracking events, animal IDs, GPS coordinates or
  individual GPS times at this stage.
- [Original-source and synthetic unit tests](tests/test_distance_band_from_subhour_v1.py):
  known example with identical distributions but different
  clock assignments; radius monotonicity and nonnegative
  distance bins; O/N/D identity; exact seed/day/pair
  denominators; fail-closed checksum/missingness checks;
  the actual ±30-minute 2019 deer exception.
- [480 original-source-derived band×seed rows and 40 band summaries](SUBHOUR_DISTANCE_BANDS_2026_10_21.json).
- [40-row transparent source/year/band CSV](SUBHOUR_DISTANCE_BANDS_SUMMARY_2026_10_21.csv),
  independently recalculated from the original pinned three-radius
  source outputs by the CI workflow.
- [Successful GitHub Actions source-derived audit](https://github.com/zuizui0223/batter/actions/runs/39592500917).
  The first test pass explicitly revealed an overgeneralized
  "12/12 at 30 min" assertion in deer 2019, corrected to the
  actual **11/12**, then the complete workflow passed.
- Original validated GPS source run:
  [Original within-15/30-minute geodesic analysis](https://github.com/zuizui0223/batter/actions/runs/39418452060);
  [source output publisher and independent verifier](https://github.com/zuizui0223/batter/actions/runs/39419265959).

All source-year/dyad/time masks, 12 seeds, O/N partitions and
four-band D zero sums reconcile numerically; two black-bear-2019
source/time groups are explicit STOP and never imputed as zero.
No raw GPS tracks, source individual names/IDs, original dates,
timestamps or positions were committed.

## 4. Boundary of the ecological claim

This provides evidence that **geographic overlap, observed
near-position frequency and residual time alignment are different
patterns** in these named public animal GPS sources, and that
a single cumulative distance cutoff can hide where timing surplus
is redistributed across distance. It does **not** identify
synchronization or active spatial avoidance, causal competition,
habitat/resource segregation, true contact or a universal
macroecological law.

Sub-hour GPS fixes may be separated by **up to 15 or 30 minutes**,
the source clock's UTC/GPS basis is not independently calibrated,
and location precision/duty cycles may differ across source
animals and seasons. The rematching reference does not preserve
movement autocorrelation. Centroid proximity ≤25 km does not
verify independent shared habitats or social population. One
source may track the same biological animals in different years;
all dyads, years and sampling seeds have dependence.

**Next empirical discriminator**: an original-tag-level GPS
accuracy/duty-cycle audit and a *movement-autocorrelation-
preserving* clock-phase null within confirmed local
populations. Only then can the observed fine-distance
time-assignment surplus support a biological mechanism claim.
