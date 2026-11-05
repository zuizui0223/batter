# Fixed post-inspection component replication and seasonal range-centroid test

**22 October 2026. Exploratory; original results from geographic subcohorts,
5/10/25-km risk sets, subject reuse and leave-one-animal analysis have been
inspected. This is NOT a preregistration or a causal population test.**
These additional descriptive checks are frozen before opening their outcomes.

## Research questions

1. Are the two already observed, disconnected original-GPS
   **2019 wild-turkey <=5-km** annual-use-centroid graph components
   (11 and 7 tagged birds, 53 and 20 eligible pair edges) both
   characterized by a positive winter-minus-summer within-500m
   *same-day over preceding/next-day original path* surplus?
   The two geographical sample components are **not** verified
   independent demographic/social populations; no GPS/metadata
   permits calling them biological replication.
2. Does the 2020 wild-turkey apparent winter signal among
   annual-center-separated dyads correspond to their **winter
   seasonal GPS-use centroids being closer than summer centroids**,
   or do the seasonal center distances tell a different story?
   This tests a possible geometric precondition of winter
   spatial convergence, NOT synchronous encounters or their cause.

## Original sources, fixed eligibility and observations

Read exactly wild turkey DOI 10.5441/001/1.671, black bear
DOI 10.5441/001/1.706 and white-tailed deer
DOI 10.5441/001/1.718, in both 2019 and 2020,
both previously fixed native source recording-time tolerances
900 and 1800 seconds, both A->B/B->A anchor directions,
radii 0.5,1,2 km and all SHA256 seeds 0–11.
Continue the previously fixed annual GPS center <=25km
dyad selection and source-month/date/recording-time opportunity:
>=7 pair-common days in >=2 January/February/December
months (within the same year, nonconsecutive)
and >=2 June/July/August months.
When doing same-day minus +/-1-day comparison,
use same original A fixes for all three treatments,
3 original matched fixes/date, 7 dates/month, 2
months per season per dyad, as in original pipeline.

Only study/year/gap risk-set matches with >=8
matched dyads and >=3 distinct animals are estimable.
All earlier four black-bear source/year/gap STOPs
must remain STOP, not zeros or dropped studies.
Original published GPS and animal/reference data must
pass complete publisher MD5, previously pinned source
SHA256, unique animal-tag/source sensor reference joins,
accepted source position/native time multiset and
**exact replay of all previously saved 576 source
direction/seed/radius numerical contrasts**.
All animal IDs, dyads, dates, GPS clock timestamps,
coordinates, and graph component site identities
stay only in temporary runner RAM; output only
anonymous source-year/distance/component summaries.

## Frozen spatial-component construction and thresholds

Reproduce annual GPS center as original implementation:
one 3D unit-sphere average per observed GPS animal-date,
then each observed date contributes equal mass to the
unit-sphere source-year average. No new spatial threshold
selection: annual center separations <=5, <=10 and <=25 km.
At each source/year/gap cutoff, form an undirected
animal pair graph whose edges are **only already qualified
same-dyad source pairs**. Compute its connected components
before examining any source outcome. Rank components by
decreasing number of animal members, then number of
eligible pair edges; no source ID or center coordinate
is serialized.

Estimate component-specific original/reversed
winter-minus-summer L1 (same-day recorded
geodesic nearness minus mean preceding/next-day
original movement-track nearness) using the already
verified per-dyad 12-seed GPS samples at all three radii.
Components with >=8 dyad edges and >=3 tracked animals
receive all 12 seed contrast values as a **source
aggregate**; all smaller components are explicitly
NOT_ESTIMABLE, not inferred zeros. Show all components
and counts, including adverse signs and components
with <=1 edge. Multiple components inside ONE named
Movebank source are not independent population
replicates without owner-verified sampling/capture sites.

## Seasonal center calculation

For each source animal/source year/season (winter
Jan/Feb/Dec within that source year vs summer
Jun/Jul/Aug), use only already QC-accepted original GPS
fixes. Compute per observed calendar day a
normalized 3D WGS84 unit-sphere direction-vector
average of all that animal's original GPS positions,
then season unit-vector center by averaging
**each observed date equally** (not each GPS fix equally).
Require >=7 unique observed dates in at least two
separate months of EACH seasonal window for each
animal; otherwise seasonal center is missing.

For each previously matched dyad, compute great-circle
distance between its two animal winter unit-vector
centers and between its two summer centers (km).
A pair with missing winter/summer center is
NOT_ESTIMABLE for seasonal centroids, never treated
as zero geographic distance.

For the SAME original qualified pair population,
report seasonal winter/summer center distance
(mean, median, 10th/90th percentiles),
paired median and mean winter-minus-summer
distance, n and fraction with winter closer.
Stratify by the already frozen ANNUAL source-center
separation bands: <=5km, (5,10]km, (10,25]km,
plus pooled <=25km. The group choices were
made based on earlier results, so are EXPLORATORY,
not independently confirmed. Never output
source animal IDs or raw geographical coordinates.

A winter-minus-summer center distance <0
may be consistent with winter spatial convergence
in a particular source/annulus. It is **not**
proof that animals meet in real time or that
winter food, flocking or resource partitioning
caused convergence; nonconsecutive winter
months, home-range migrations, site-year effort
and spatial uncertainty remain.

## Interpretation and STOP gates

The component source score and seasonal center
results answer DIFFERENT questions:
- a component estimate tests original-source
  near-synchronous day-specific geographic
  sharing among a fixed eligibility graph;
- winter/summer centroid separation tests
  the *configuration of average observed
  geographic space* in a coarse seasonal window,
  independently of matched time of day.

The difference of seasonal centers can be
positive or negative even if the day-specific
L1 is positive. Repeated animals/year members
and geometric graph components are not
statistically independent animal populations.
All effect magnitudes and sensitivity counts
are descriptive; no population p-values,
significance tests, confidence intervals,
active synchronization, food/resource E,
or physical co-presence T inferred.
