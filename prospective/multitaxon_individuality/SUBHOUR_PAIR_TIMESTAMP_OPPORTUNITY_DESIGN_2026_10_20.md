# Fixed pre-outcome design: source-native sub-hour GPS timestamp opportunity

**Exploratory 20 October 2026; previous 2D X and 3h/6h T results have been opened.**
This records the new sub-hour opportunity criteria *before* inspecting
the output. Not a preregistration, significance test or biological encounter
analysis.

## Question
Do original GPS data from turkey, black bear and white-tailed deer have
adequate *actual time-matched measurement opportunity* to attempt a
sub-hour spatial-nearby comparison? An apparent geographic X edge is
not a direct GPS-observed encounter. First estimate whether pairwise
timestamps can be compared without imputing missing co-observation.

## Sources, fixed animals and time basis
All three original published Movebank sources:
- wild turkey DOI 10.5441/001/1.671
- American black bear DOI 10.5441/001/1.706
- white-tailed deer DOI 10.5441/001/1.718.

Use original complete 2019–2020 GPS and unique reference files
with *publisher MD5 and pinned SHA256* and the precise validated
source position/QC logic in cross_source_seasonal_x_v2.py.
Reconstruct native source datetimes independently, verify exact accepted
animal+date+position multiset before counting matches. Source timestamps
may use GPS versus UTC clock; **absolute UTC offset is not established**.
This only compares within the same source and the same source-calendar
date, not across unrelated datasets.

## Screening population and matched opportunity
Start from unchanged old fixed dyad risk sets: annual day-balanced
utilization center distance ≤25 km, at least seven pair-common
recorded dates in at least two separate months **within each**
winter and summer window. Winter=(Jan,Feb,Dec) of a *calendar year*,
not a continuous winter interval; summer=(Jun,Jul,Aug).
Require exact prior V2 source-year dyad denominators, including all
ineligible/missing source years; do not retrospectively change them.

For each dyad/date, independently count maximum one-to-one pairs
of recorded original GPS fixes whose native-clock timestamps differ
by at most **15 minutes** and **30 minutes** (both thresholds declared
now). Use the optimal sorted two-pointer one-to-one maximum
cardinality matching algorithm; never reuse one GPS fix multiple times
within a day and threshold. Locations are *not* used in the timestamp
matching and no proximity/encounter result is calculated in this stage.

A date with **>=3 one-to-one time-matched fix pairs** is qualifying.
A month qualifies with **>=7 qualifying same-calendar dates**.
A dyad passes a year's stated threshold only if >=2 winter and
>=2 summer months qualify. Report the complete original geographic
risk-set denominator, the number of dyads with support at 15/30 min,
how many are retained from the old fixed source-year pool and aggregate
matched fix/dyad-date distributions. 15-min eligibility must be a
subset of 30-min eligibility by design.

Set a source-year future encounter-analysis readiness threshold of
**>=8 eligible dyads and >=3 distinct tracked animals** with complete
paired-season support. This is a *feasibility floor*, not power analysis
or population-level biological replication. Less than this is a
STOP_SMALL_OPPORTUNITY result, NOT absence of encounters.

## Future ecological estimand (not calculated at this stage)
After passing opportunity and confirming acceptable source-location
accuracy and actual local population risk, a separate fixed protocol
would compute spatial proximity conditional on truly time-matched
original fix pairs, compare against a matched time-shift null and
report empirical spatial-nearby use versus recorded spatial
availability. Do **not** claim any physical encounter, niche
partitioning or social association from timestamp opportunity alone.

All outputs are aggregate per source, year and threshold; **never
publish original animal IDs, exact dates/time stamps, lat/lon,
GPS tracks or individual pair IDs**. Any unknown date/time or source
verification error is STOP, not encoded as no temporal overlap.
