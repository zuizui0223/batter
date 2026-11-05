# Seasonal *day-specific* geographic co-location after preserving adjacent-day GPS trajectories

**21 October 2026 — original-public-GPS exploratory replication and anchor-direction falsification.**

## Main finding

**The source-clock timing of close geographic use is not fully captured by
seasonal spatial overlap, and the *strength* of day-specific co-location
depends on the animal dataset.** Wild turkeys in the published
southeastern-US GPS source show a winter excess of same-day
time-matched location proximity compared with both the preceding and
following days' original movement sequences. This is observed for
both 2019 and 2020 and survives **reversing which tagged animal
anchors the dates/times**. White-tailed deer in the western-Virginia
source show a much weaker winter excess that does **not** meet the same
predeclared two-direction, 500m-and-1km stability gate.
Black bears cannot support this particular trajectory-preserving
comparison under the prespecified sample-size threshold.

This is evidence for **observed source-specific movement-space
configuration**, not an identified seasonal mechanism, social
interaction, cooperative grouping or food-resource separation.

## 1. Source population and exact comparison

The three complete original Movebank GPS/reference archives have been
independently downloaded and checked against the **publisher MD5
and fixed SHA256/source-reference/event-position receipts**, again
confirming **954,688 accepted 2019–2020 GPS fixes**:
- wild turkey, southeastern US: [DOI 10.5441/001/1.671](https://doi.org/10.5441/001/1.671), 435,214 accepted fixes
- American black bear, Connecticut: [DOI 10.5441/001/1.706](https://doi.org/10.5441/001/1.706), 148,394 accepted fixes
- white-tailed deer, western Virginia: [DOI 10.5441/001/1.718](https://doi.org/10.5441/001/1.718), 371,080 accepted fixes.

A source dataset and a named geographical region **do not certify
local population membership**. All compared dyads were previously
selected by annual GPS-usage-center distance <=25 km, >=7 common
source-GPS dates in >=2 months in both season categories.
No within-source independent demographic/local population labels
were validated.

For each source-year, winter is **Jan, Feb and Dec of the same
calendar year**, *not* a continuous winter running across the
calendar-year boundary. Summer is Jun/Jul/Aug.

The [prespecified-after-inspection day-shift design](DAY_SHIFT_PRESERVED_TRAJECTORY_DESIGN_2026_10_21.md)
uses exactly the same real focal animal A GPS fixes at the same
source-clock times to compare:
- **O0**: GPS nearness to B's original track on the SAME date;
- **O−1**: GPS nearness to B's full original path the PRECEDING day
  of the same month, at matched recording time of day;
- **O+1**: nearness to B's full original path the FOLLOWING day,
  again at matched recording time of day;
- **L1 = O0 − (O−1 + O+1)/2**, a descriptive day-specific proximity
  surplus beyond the two neighboring original daily paths.

No B locations are artificially shuffled within the day. The
alternative day's original time-ordered trajectory is preserved,
unlike the earlier within-day independent position permutations.
The day-shift reference **does not** preserve weather, habitat
availability, multi-day movement phases or all autocorrelation.
It is NOT an exchangeable causal null model.

A shared source GPS fix has a recorded time offset at most
**15 min (primary)**, or **30 min (secondary)**. The position
response is *haversine distance* <=500m (primary fine radius),
or <=1km/2km (sensitivities), with no grid boundary effects.
All 12 SHA256-deterministic observation subsamples retain exactly
2 supported months × 7 pair-common dates × 3 matched GPS
fixes per date in each season. The same real focal A source
fixes enter all three date treatments, per orientation, and
the source dyad membership is identical across winter/summer.

## 2. Main 15-minute/500-m result

The winter and summer L1 values below are **proportion-point units**
and represent the additional fraction of original time-matched GPS
fix pairs within 500 m on the same date rather than on the
adjacent-day tracks. They are NOT an animal encounter rate.

| Published source-year | Fixed dyads | Original A->B winter L1 | Original A->B summer L1 | Winter-minus-summer, A->B | Winter-minus-summer, reversed B->A | Positive draws, original/reversed |
|---|---:|---:|---:|---:|---:|---|
| Wild turkey 2019 | 112 | +0.068302 | +0.017503 | **+0.050799** | **+0.052473** | 12/12 · 12/12 |
| Wild turkey 2020 | 21 | +0.071287 | +0.044643 | **+0.026644** | **+0.027211** | 12/12 · 12/12 |
| White-tailed deer 2019 | 55 | +0.004672 | +0.000198 | +0.004473 | +0.002255 | 11/12 · 9/12 |
| White-tailed deer 2020 | 205 | +0.001723 | +0.000339 | +0.001384 | +0.000982 | 11/12 · 10/12 |
| Black bear 2020 | 5 dyads at 15 min | — | — | **NOT ESTIMABLE** | **NOT ESTIMABLE** | STOP |

One tabulated fraction of 0.050799 corresponds to **5.0799
percentage points** of sampled GPS fix-pair nearness surplus in
the winter-minus-summer contrast for this specific source
and recording design.

### Interpretation of the turkey contrast

For turkey 2019 in winter, O0 is approximately **0.2522**
within 500 m, whereas the two original neighboring day tracks
average **0.1839**: the day-specific surplus is +0.0683.
In summer, the corresponding O0 is approximately **0.0523**
and neighboring-day mean **0.0348**, with surplus +0.0175.

Turkey 2020 similarly shows winter +0.0713 and summer +0.0446.
Thus the difference cannot be attributed *solely* to a
completely arbitrary choice of original A/B ID anchoring:
when the focal animal is reversed, the comparison remains
positive in 12/12 dependent samples for both study years.

These values do NOT establish that tracked turkeys formed
social flocks, interacted, visited shared food patches or
actively timed their presence. A one-day temporal shift also
changes the environment/date and can reduce spatial overlap
through ordinary day-to-day movement without social mechanisms.
The regional source dataset could contain multiple sampling
sites and dependent animals/years, so these are **source-year
patterns** rather than independent population replicates.

### Deer: small effect, not anchor-stable across fine distances

White-tailed deer 2019 and 2020 exhibit weaker 500m L1 contrasts
and fewer positive original/reversed draws.
At 1 km and <=15 minutes, they are:

| Deer year | Original A->B winter-minus-summer L1 | Reverse B->A | Positive source subsamples, original/reversed |
|---|---:|---:|---|
| 2019 | +0.001389 | +0.002092 | 7/12 · 9/12 |
| 2020 | +0.001234 | +0.000455 | 10/12 · **6/12** |

The previously fixed [anchor-symmetry stability gate](DAY_SHIFT_ANCHOR_SYMMETRY_DESIGN_2026_10_21.md)
requires >=10/12 positive samples in BOTH orientations
at BOTH 500m and 1km. **All four turkey year/tolerance
settings pass; none of the four deer settings pass.**
This does not establish a species-general
turkey-versus-deer effect or statistical interaction
because each taxon is represented by only one source study,
and observation periods/animal selection differ.

An important apparent reversal remains: the **absolute observed
within-500-m deer GPS nearness is higher in summer** in
both years. The small positive winter L1 instead refers
only to the local difference from preceding/following-day
original tracks, NOT higher absolute winter encounter rates.

## 3. Explicit STOP and measurement opportunity

The earlier black-bear 2020 time-matched source risk set had
38 qualified GPS dyads for 15 min, 47 for 30 min.
Demanding 7 matching dates/month across 2 months/season with
both preceding AND following original full B daily GPS paths
reduces first-anchor eligibility to **6 dyads**. In the
two-anchor intersection, eligibility is **5 at 15 min**
and **6 at 30 min**; 2019 has no eligible dyads.
The protocol fixed >=8 dyads and >=3 animals, so **all
four black-bear source/year/tolerance entries STOP**.
This is lack of observation opportunity, not absence
of biological day-specific proximity or avoidance.
Changing the gate to salvage a bear effect is prohibited.

## 4. Robustness and results hierarchy

- **Original fixed population of comparisons:** all 3
  sources, 2019/2020, 15/30 min and 0.5/1/2 km.
- **Complete original GPS-replay:** both the first-anchor
  [source-day analysis](DAY_SHIFT_PRESERVED_TRAJECTORY_SUMMARY_2026_10_21.json)
  and independently run [reversed-anchor archive](DAY_SHIFT_DUAL_ANCHOR_SUMMARY_2026_10_21.json)
  pass published source receipts and full original GPS time/position
  source reconciliation.
- **Pair-set support:** for turkeys 112/21 and white-tailed
  deer 55/205 the two orientations retain the entire
  first-anchor pair set in both 15/30-min analyses.
- **Reproducibility:** the original A->B source result has
  been replayed **exactly** for all 288 eligible
  forward-orientation seed/radius rows in the independent
  two-direction pipeline.
- **Strict source-year STOPs:** four black-bear
  source/year/tolerance combinations are explicitly absent,
  not encoded as zero.
- **Original 10 synthetic contracts, six reverse-anchor
  synthetic contracts and full receipt/error/denominator
  independent validation** are in the repository.
- **576 orientation×seed×radius source results**, 24
  comparative source/year/tolerance/radius summary rows.
  The same source animals, overlapping pair structures and
  randomized subsamples mean there are NOT 576 independent
  ecological tests.

The successful original data Actions:
[day-shift original GPS source runs](https://github.com/zuizui0223/batter/actions/runs/39595138997),
[reversed-anchor original GPS runs](https://github.com/zuizui0223/batter/actions/runs/39596916860).
The [SHA256-pinned dual-anchor publishing/verification run](https://github.com/zuizui0223/batter/actions/runs/39598092121)
published original-source **aggregated results only**, with
no raw animal IDs, exact calendar dates/times, positions or tracks.

## 5. What can now be claimed in ecology?

**The strongest defensible statement is source-specific:**
In the wild turkey GPS study, the winter change in within-500m
and within-1km **day-specific source-recorded proximity above an
adjacent-day recorded-path reference** is larger than the summer
counterpart in both 2019 and 2020, and its direction is
insensitive to reversing the arbitrary tag-ID anchor
and to widening source timestamp tolerance from 15 to 30 min.
This does not alone identify sociality, winter resource
competition, a general law across clades, or actual encounters.

A valuable comparative boundary also emerges: the
white-tailed deer source has a positive but smaller 500m
trend that does not pass the equally stringent 1km,
two-anchor rule. The black-bear source has too little
pair/date support to evaluate this test. **No taxon-general
cross-source causal mechanism is established.**

Before promotion to a publication hypothesis test, obtain
publisher-documented capture groups/local populations and
tag-specific GPS recording schedules/accuracy, then attempt
an independent study replication under fixed seasons.
A lagged day is a useful trajectory-preserving sensitivity
but is **not a validated no-association null**; different
weather, food and day-specific movement can explain the result.
The new finding should therefore remain exploratory and
qualify any subsequent social or ecological mechanism story.
