# Original GPS source-day shift control for near-time geodesic proximity

**21 October 2026: post-inspection exploratory design, fixed before opening
the following day's shifted-track outcome.** Earlier 2D X, coarse-clock T,
same-day shuffled-time reference D and its 0.5/1/2-km distance-band
results are known. This is NOT independent preregistration.

## Falsifiable ecological question

Is geodesic spatial proximity of two animals recording on the *same day*
greater than could be achieved by matching one animal's same-day original
GPS fixes to the *other animal's consecutive previous/next calendar-day
trajectories at the same source-clock time*? This conservative
time-series-preserving diagnostic avoids inventing independent spatial
locations or randomizing single within-day GPS positions. It can reveal
whether a prior fine-distance time-assignment excess D is explained by
stable home-range and repeated daily sampling clocks alone. A positive
contrast is still NOT confirmed synchronized behavior, interaction,
competition or an encounter.

## Completely predetermined source and time frame

Use precisely these original publisher-MD5 and previous-SHA256 verified,
complete Movebank GPS/reference sources: wild turkey DOI 10.5441/001/1.671,
American black bear 10.5441/001/1.706, white-tailed deer
10.5441/001/1.718. Evaluate both years 2019 and 2020. Keep
the fixed annual source-calendar winter category Jan/Feb/Dec
(not chronologically connected across the calendar year), and
summer Jun/Jul/Aug. The original biological group/source-population
metadata and GPS clock basis remain unknown; a 25-km annual usage-center
restriction is an analytical proximity proxy, NOT a verified local
population or social group.

Start from the exact original prior V2 matched pair geometric support:
- turkey 2019/2020 n=112/21
- black bear 2019/2020 n=1/104
- white-tailed deer 2019/2020 n=55/205.
Verify the source-original GPS MD5/pinned SHA256, full original
event/reference QC counts and native GPS time/position multiset
before using any source positions, and require exact agreement with
these old pair denominators. No outcome-selected sources/years/animals.

## Strict common-Animal-A fix/day support

For each fixed pair (A,B), source-native year/month/date d, and each
predeclared matched-time tolerance **15 min primary**, **30 min secondary**,
build maximum one-to-one time matches between A(d)'s original fixes and:
  (i) B(d), the same source-calendar date;
  (ii) B(d-1), the prior date;
  (iii) B(d+1), the following date.

All day-shift records must be from **the same source calendar month**
as d; the shift is exactly one consecutive calendar day, with
native time-of-day tolerance applied after day shifting.
The three matchings are performed independently with the identical
sorted greedy maximum-cardinality pairing. Take the **intersection of
A's actual source fixes participating in ALL THREE matches**. Thus
the identical A time/location observations enter all treatments,
and in each comparison B's original fix times differ from A's
source clock by at most the chosen 15/30 minutes. Each original B
fix can appear only once within one day/treatment matching.
No GPS interpolation or manufactured track points.

A date qualifies only if at least **3 such anchor A original GPS fixes**
have three valid B matches; a month qualifies with at least
**7 qualifying dates**, and each dyad must qualify in at least
**2 separate months of both winter and summer**. The same eligibility
is applied to A->B only, not symmetrically B->A. This direction is
chosen *a priori*, by stable lexicographic sorting of the two
original source animal IDs, and MUST be disclosed as a possible
anchor-direction dependence rather than hidden as biology.
Hard-stop any model run if original pair support changes or 15-minute
qualifying dyads are not a subset of 30-minute qualifying dyads.
A source/year/tolerance with fewer than **8 supported dyads or 3
distinct animals** is NOT_ESTIMABLE, not an ecological zero.

## Sampling and metrics fixed before outcome

For each supported dyad and each deterministic SHA256 **seed 0–11**:
sample exactly 2 supported months/season, exactly 7 qualifying
A-source dates/month, and exactly 3 **identical A anchor fixes/day**
from their intersection. The same sample applies to ALL spatial
distance thresholds below and to same-day/lagged B alternatives.

For each original sampled A anchor fix and each treatment B(d),
B(d-1), B(d+1), compute haversine great-circle distance on the
unchanged original source positions. Define O0(r), Ominus1(r),
Oplus1(r) as the fractions ≤r for the original matched three-fix
sample, averaged equally per day, per selected month and per
eligible dyad. Let **L1(r) = O0(r) - [Ominus1(r)+Oplus1(r)]/2**.
The lag controls preserve the within-day *order and original
locations* of B's movement sequence instead of independently
permuting individual B positions, but they do not preserve
between-day weather, actual day-specific resource availability
or true interactions.

Predeclare radii **0.5, 1 and 2 km**. Report original O0, both
one-day-shift controls, their average, and L1 for EACH season
and winter-minus-summer, under both 15- and 30-minute
source-clock tolerances. Report all 12 seed results, mean,
range, signs, dyad/date/fix denominators and attrition from
previous same-day source match support. No p-values or confidence
intervals; seeds and dyads share the same dependent GPS sources
and are not independent population replications.

All outputs are source/year/tolerance/radius/season/seed aggregate
numbers only: no original animal ID, original source date/time,
GPS coordinates or individual pair values may be stored.

## Hypothesis discrimination and interpretation limits

If a positive conditional same-day D observed in a previous
time-bin/within-day permutation analysis disappears or changes
sign against this stricter adjacent-day ordered-track reference,
the previous D should be interpreted primarily as a
source-clock/within-day layout property rather than direct
ecological co-use. If L1 remains positive across fixed radii,
gaps, years and samples, it supports *day-specific* additional
geographic co-location in these source cohorts but not
biological attraction: animal location autocorrelation,
habitat/weather variation and GPS accuracy are not
independently estimated.

The lagged B tracks are **original, unaltered daily
sequences**; only their dates are exchanged. This is a
trajectory-preserving **sensitivity reference**, NOT a fully
autocorrelation-adjusted randomization test or a proven
biological no-association null. Source fix-time schedules may
be coordinated by tracking devices. It cannot settle
whether the deer fine-scale winter pattern is caused by
group behavior, common movement opportunities or instruments.

Follow-up only if source reports demonstrate real local
population membership and source-tag GPS error/schedule
parameters. Never reinterpret matched GPS locations as
actual direct encounters, resource niches or causality.
