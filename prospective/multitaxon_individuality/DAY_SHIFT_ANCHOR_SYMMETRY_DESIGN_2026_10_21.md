# Pre-outcome robustness design: reverse focal animal in day-shift GPS control

**21 October 2026; POST-INSPECTION sensitivity.** Previous original
GPS same-day versus previous/next-day results have been inspected.
This design is fixed before opening the reversal outcomes. NOT an
independent preregistration or causal null hypothesis test.

## Primary methodological risk to falsify

The first source-day trajectory comparison anchored original animal A's
fixes while shifting only original animal B to its preceding/following
calendar-day path. The fixed direction A->B was determined by
lexicographic ordering of the original animal IDs. Because animals may
have unequal GPS schedules and movement patterns, the sample of
qualifying anchor fixes, and hence any observed excess, can depend on
which animal is designated A. **A biological ecology conclusion
should not depend strongly on arbitrary alphanumeric IDs.**

## Frozen population and source acceptance

Revisit exactly three originally MD5- and pinned-SHA256-verified published
Movebank sources: wild turkey DOI 10.5441/001/1.671, black bear DOI
10.5441/001/1.706 and white-tailed deer DOI 10.5441/001/1.718.
All source 2019 and 2020 original GPS positions/time/reference
joins must replay exactly as in previous original-GPS V2 and
same-day source-time inspections. Preserve the existing original
geometric pair denominator (annual usage-center <=25 km; >=7
pair-common observed dates in >=2 winter and >=2 summer months),
then require SAME source-day matched GPS paired-fix support at
<=15 minutes (primary) and <=30 minutes (secondary).

For each fixed original pair (a,b):
1. Recompute the already reviewed primary lexicographic orientation
   a->b, matching identical A source fixes to B(d), B(d-1), B(d+1).
2. Independently compute the REVERSED orientation b->a using the
   same original source GPS acceptance, common month/day/time tolerance,
   >=3 shared focal fixes/date, >=7 qualifying dates/month,
   >=2 months per calendar-season category.
3. Preserve the **intersection of the two orientation-eligible
   pair sets** before looking at any nearness outcome. Reanalyse
   BOTH orientations on exactly that same pair membership.
   The underlying selected A or B positions, dates and matched
   fix assignments need not coincide between directions;
   this is a dual-anchoring directional sensitivity, not a
   measurement of the identical GPS fix sample.

Retain source/year/tolerance pair numbers, animals, source-fix
count, and attrition from the known primary anchored risk set:
wild turkey n112/n21, white-tailed deer n55/n205,
black bear 2019 n0, 2020 n6 in the previously inspected A->B
day-shift analysis. 15-minute intersection support MUST be a subset
of 30-minute support. Need >=8 intersecting pairs and >=3 distinct
animals for one source/year/tolerance comparison. Otherwise STOP,
not zero response.

## Outcomes fixed before reversal is computed

Use exactly the already fixed source-day sampling code:
2 months/season, 7 qualifying days/month, exactly 3 original
focal source fixes per date; SHA256 seeds 0–11, ±1 source
calendar day for only the other animal's full daily recorded
trajectory, source-clock tolerance 900/1800 seconds,
geodesic radii 0.5/1/2 km. Season category is Jan/Feb/Dec
within one calendar year versus Jun/Jul/Aug, not one continuous
winter episode.

For each orientation, seed, distance radius and source season,
compute O0 = observed matched same-day GPS near-position fraction,
Oprev, Onext, L1=O0-(Oprev+Onext)/2. Report both A->B and B->A
winter and summer L1, winter-minus-summer L1, positive/negative/
near-zero counts across the 12 dependent source subsamples.
Do not discard negative, undefined, or asymmetric cases.
All outputs are source/year/tolerance/orientation/radius/seed
aggregate-only. No animal ID, exact date/timestamp, GPS position
or individual dyad proximity record may be committed or logged.

The **direction-robust** descriptive pattern requires winter-minus-
summer L1 to have the same sign in BOTH anchor orientations for
at least 10/12 finite-source subsamples, in all predeclared
0.5-km and 1-km radius analyses of a cohort. This is an
exploratory *stability gate* and must not be converted into a
biological significance test. Report 2 km as sensitivity.
If one orientation changes sign or falls below eligibility,
the earlier source A->B result must be described as
**orientation-dependent/unresolved**, rather than as
independently replicated seasonal behavioral co-use.

## Interpretation boundaries

The two original day-shift controls preserve the other animal's
within-day GPS movement ordering but not its whole environment,
time-of-day activity autocorrelation or multiday migration dynamics.
Reversing the anchor does not solve systematic habitat use,
GPS positional error, fix time calibration or local population
membership. No actual animal encounters, sociality, competition,
trophic partitioning, p-values or worldwide law are measured.
If both anchor orientations agree, the finding is still only
an empirically more robust GPS source-day co-location diagnostic.
