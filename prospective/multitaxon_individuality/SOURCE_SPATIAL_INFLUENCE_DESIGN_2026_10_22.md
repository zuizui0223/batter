# Source geography, repeated-year subjects and leave-one-animal influence audit

**22 October 2026. This is POST-INSPECTION source-specific exploratory follow-up,
not preregistration. Prior seasonal X, within-day matching, day-shift contrast and
A/B anchor directions have already been observed.** This document fixes all
stratifications and ecological inference boundaries before opening the new
spatial-component/influence results.

## Ecological question

The previous southeastern-US wild turkey source showed a winter excess
of same-day GPS nearness relative to preceding/following-day original
GPS paths, insensitive to reversing which original animal's time/day
anchors the source GPS comparison. Does this signal survive
(1) geographically tighter pairs, (2) removal of any single tagged
animal, and (3) treating reused animals across 2019/2020 as
REPEATED SUBJECTS rather than independent study replicates?
Were multiple spatially distinct original-population components
represented, or only one original-source sample?

## Frozen complete source frame

Use exactly wild turkey [10.5441/001/1.671],
white-tailed deer [10.5441/001/1.718], and black bear
[10.5441/001/1.706]. For each, use complete original publisher
GPS and reference files, with publisher MD5, earlier SHA256,
exact original event/reference QC, independently reconstructed
native source-time plus position multiset. Read original-source
GPS only on an ephemeral GitHub runner, emitting exclusively
aggregate source/year metrics (no original animal IDs, dates,
times, locations, pair-level estimates, site centroids or map
coordinates). Do not alter the original score or support rules.

Compare both preselected years 2019/2020 and both original
GPS time gap thresholds 900 and 1800 seconds. Require
>=7 calendar dates in 2 separate winter and 2 summer
months with 3 same-anchor original GPS fix triples per date,
and BOTH anchor orientations A->B and B->A. Winter is
Jan/Feb/Dec within the same calendar year (noncontinuous);
summer Jun/Jul/Aug. The old annual-centroid <=25km
risk set is unchanged. Reproduce exactly the ORIGINAL
complete-source *A/B anchor* pair counts: wild turkey
2019 112 and 2020 21; white-tailed deer 2019 55
and 2020 205 at both gaps; black bear 2020 5 at
900 sec and 6 at 1800 sec, both STOP due n<8.
No new pairs may be admitted by reviewing outcomes.

All years, radii (0.5,1,2 km) and 12 original SHA256
seeds (0..11) remain in the analysis even if the
result is negative. The original day-shift L1
estimand remains O0 - [O-1+O+1]/2 on exactly
the same focal A GPS fixes in each source-date
comparison, and the two anchor directions are
evaluated on a common pair membership set.

## Geographic substructure sensitivity: not declared populations

Reconstruct the unit-sphere equal-original-day-weighted
annual animal usage centroids from original source GPS.
For each source/year/score-compatible dyad, compute
the great-circle distance between animal centroids.
Before viewing the outputs, declare geographic
pair filters at <=5, <=10, <=25 km.
For each threshold, report supported pair counts,
distinct animal counts, mean and seed sign of
winter-minus-summer L1 by original/reversed A/B,
at radii 0.5,1,2 km and both time gaps.
Declare NOT_ESTIMABLE if <8 filtered pairs or
<3 distinct animals. The three distance thresholds
are *dependent sensitivity filters*, not new
independent population replicates.

At each threshold, construct the undirected graph
of eligible animals and eligible dyads whose
annual centers are <=threshold apart.
Connected components of this graph are described
only by aggregate distributions of animal count,
pair count, and number meeting >=3 animals/8 pairs.
No site coordinates or animal labels are emitted.
An edge/path between annual GPS centers does NOT
certify that the animals were in the same true
social/ecological population; a connected component
is strictly a geometric sample cluster.

## Individual influence and year continuity

For each source/year/tolerance and each existing
orientation, recompute exactly the original 12 seed
L1 results by generating the same per-dyad
deterministic original-fix samples and averaging
them over the full pair risk set. **HARD STOP if
any of the 576 old aggregate source/orientation/
seed/radius scores cannot be reconstructed.**

Next, leave out each source animal, ONE AT A TIME,
and remove all pair edges incident to that animal,
WITHOUT resampling the other dyads or their
original source GPS positions. Recompute the
12-seed winter-minus-summer L1 on the remaining
pairs, for radii .5 and 1 and 2 km, separately
for each original/reversed anchor. Exclude LOO
replicates retaining fewer than 8 pairs/3
animals as NOT ESTIMABLE; never code them zero.
Aggregate across omitted animals: n valid
omissions, min/median/max of the seed-mean
delta, smallest fraction of the 12 seeds with
positive contrast, and fraction of valid
omissions retaining positive mean and >=10/12
positive seeded contrasts. **Never publish any
individual omission identity or per-animal value.**
Not a jackknife confidence interval; pair edges
are dependent and source subjects not iid.

Privately reconstruct the exact year-specific
source animal-ID sets of eligible dyads for
2019 and 2020; report only the number of
animals and eligible dyad pairs reused across
the two years and denominator counts.
No individual identifiers are output.
This is an observational *sample independence
audit*, not an independent population replication.

## Source reference metadata scope audit

Read the original public animal-tag reference
CSV only after the same verified full-source
download and report counts of non-missing
original animal-level source group/study-site
fields, plus presence of explicit accuracy or
tag duty-cycle/source-time calibration metadata
columns. Never infer a capture site or device
accuracy from animal ID prefixes or from study
titles; never output original field values,
IDs, personal names, raw coordinates or site
names. Absent fields lead to
POPULATION_MEMBERSHIP_NOT_VERIFIED /
GPS_ACCURACY_NOT_VERIFIED, not guessed values.

## Inference and falsification

A signal can be called source-specific
*robust to these diagnostics* only when its
winter-minus-summer L1 is >0 in both anchor
orientations under >=10/12 source draws
at BOTH .5/1km radii, at both 900/1800s
time tolerances, and remains positive
under all estimable single-animal exclusions.
If stronger geographic restriction
leaves no supported pairs, STOP rather
than claiming spatial robustness.
Even if all sensitivities agree, the inference
remains original-source recorded
day-specific geographical nearness, NOT
social association, observed encounters,
winter flocking causation, resource overlap,
ecological specialization or a taxon-general law.
Report repeat-year animals as repeated subjects,
not independent replicate populations.

No fishing for a better 500m threshold, no
post-hoc removal of inconvenient source-year
strata, no populations inferred from disconnected
sample centroids. New evidence must be interpreted
beside the original README and source publisher
DOIs, including their unresolved location error
and native-clock basis.
