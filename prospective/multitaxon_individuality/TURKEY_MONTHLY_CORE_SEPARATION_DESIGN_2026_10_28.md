# Turkey calendar-month geography of the source-defined 2020 single mover

**28 October 2026 — post-inspection original-GPS follow-up design. NOT
preregistered; previous winter/summer 2020 single-mover and component
geometry results are already known.** The objective is to resolve temporal
support and measured within-year geographic reconfiguration, not to find
another posthoc positive threshold or infer social flocking.

## Locked biological question
The source-verified 2020 turkey cohort (7 original animals, 21 eligible
pairs at <=25 km annual-centroid separation) has exactly ONE original
animal with no eligible <=5-km annual-centroid pair. ALL five
10–25-km annual-centroid pairs share that animal. Its early-year
Jan–Feb to summer Jun–Aug original GPS usage center shift is
~14.52 km, versus ~0.455 km median among the other six.
WHEN do the source-measured interanimal centroid distances separate
over the calendar year, and how much does this depend on monthly
tracking-date support? Compare the two already identified disconnected
2019 annual<=5-km turkey pair components as contextual source
configurations without pretending they are independently validated demes.

## Frozen data and source gates
Use original Movebank turkey DOI 10.5441/001/1.671, full event
GPS + reference files; publisher MD5 and pinned SHA256, original
animal-tag QC and independently reconstructed exact GPS timestamp
and coordinate multiset must pass the existing
same_clock_bin_couse_v1 / subhour_geodesic_proximity_v1 chain.
Accept exactly **435214** GPS fixes from 2019–2020.
Use previously fixed original year/season source-clock <=900-second
dual-anchor eligible pair sets: 2019 112/19 animals, 2020
21/7 animals, year-animal-ID sets disjoint (0 overlap).
Annual usage centers are equal-weight over original GPS
dates, using spherical unit-vector centroids, not raw fix-count
averages; validate the 2019 annual<=5-km graph components
(11 animals/53 pairs and 7 animals/20 pairs) and the
2020 graph (6 original animals/14 <=5-km graph edges,
one isolated animal, 15 core–core pairs, 6 isolate–core
pairs, 5 far 10–25km annual-center pairs, all five involving
that same isolated animal). STOP on any changed graph or
original source/event count. The geometric "isolate"
is NOT a known different ecological population, actual migrant,
or social outlier.

## Monthly GPS measurement, no time interpolation
Use *all* month numbers 1 through 12 of 2019 and 2020,
chosen independently of observed outcomes. For each original
animal/month, construct the unit-sphere mean of daily
source GPS unit-vector centers; equal weight per recorded
calendar date, with >=7 independent GPS-recorded calendar
dates required. No month without >=7 observed dates gets a
centroid, and no missing months are filled by interpolation.
Output **only month/group-level aggregate metadata and
pair-distance summaries**; never individual-level monthly
trajectories, original animal IDs, source timestamps,
calendar dates, latitude/longitude, GPS cells or geographic
centroid coordinates.

### 2020 predeclared comparison sets
(A) six source animals in annual<=5-km connected graph:
all 15 of their eligible source pair combinations;
(B) unique annual<=5km unpaired animal versus these 6,
all 6 pair combinations;
(C) the original five annually separated 10–25km pairs,
which are a subset of B, not independent replicates;
(D) all 21 year-2020 eligible dyads.
For each month record number of sampled source animals
with >=7 original GPS dates (overall, core and isolate
supported yes/no), original accepted GPS fix count and
total animal-calendar-date count (cohort aggregate only).
For A–D, compute number of eligible pairs with BOTH
valid monthly centers, number of distinct covered
animals and min/median/mean/max source-month
great-circle centroid distance. Mark group
monthly distance NOT_ESTIMABLE if fewer than
**3 valid pairs / 3 distinct animals**, never impute 0.
Report additionally the fraction of the original six
isolate–core source pair edges with valid monthly
distance as a diagnostic of sampling opportunity.
A source month is **FULLY_TRACKED_2020** only if
all 7 original animals have >=7 source dates;
partial source months are explicitly labeled.

### 2019 predeclared comparison sets
The two source-year <=5-km annual source graph components
(53 and 20 eligible dyad edges), plus all 112
preexisting source-eligible 2019 dyads. Every month
reports the full original component animal/dyad
denominator, the number of animals with >=7
source-recorded dates, valid pair counts, and the
median/range of seasonal same-month source centroid
distances when >=3 eligible pairs / >=3 observed animals.
A component graph is NOT validated demographic or
social-population independence. No 2019 "single isolate"
is assumed or identified by posthoc analogy to 2020.

## Temporal transition classification (before outcome)
Only among 2020 calendar months for which (B) has at
least 4 of its six isolate–core distances from original
GPS monthly centroids, label observed monthly state as
- CLOSE if **median <=1 km**
- SEPARATED if **median >=5 km**
- INTERMEDIATE otherwise.
Output *the ordered sequence of supported states* and
the first observed CLOSE-to-SEPARATED transition bracket,
if such a pair occurs. A month with insufficient source
support is **UNOBSERVED**, not CLOSE or SEPARATED.
A state transition bracket between two observed months
does NOT establish when an actual animal moved, whether
migration was abrupt, or whether it was caused by another
individual, weather, predation or food resources. Report
the number of unobserved months inside any bracket.

Monthly thresholds are descriptive geometry references,
not animal contact or social behavior.
The exact 2020 year-wide Jan–Feb/summer annual5-isolate
result and the 2019 components must be *unchanged
receipt-linked checkpoints*, not reinterpreted as
multiple independent dyad-level biological discoveries.

## Predeclared uncertainty/quality checks and STOP rules
Independently synthesize source-GPS coordinates in tests
for a stationary six-animal core with one known time-shifting
original animal, a stationary all-animal reference, no fixes,
large within-month variation and longitude wraparound.
Fail if date- versus fix-balanced source centers differ
from declared numerical rules, if an original source year
or component is missing, or if a month has insufficient
recorded dates but yields a valid centroid.
Verify every monthly group has valid-pair count within
original denominators, no distinct animal count
inflation, and all geographic distances within
[0,pi*6371.0 km]. Compare seasonal Jan–Feb/Jun–Aug
source geographic summaries against previously pinned
original-source single-mover receipts where estimands
match; do not compare a single month to an aggregated
multi-month centroid as if identical.

The new month-by-month distance record is a sensitivity
of one source study and repeated tracked animals,
not independent samples, animal encounter measurements,
a population confidence interval, geographic source
capture-site metadata or a universal migration law.
Without tag-specific GPS accuracy, certified local
population assignment, actual recording schedule and
environment/resource covariates, only measured
month-level source GPS geographic configuration is supported.
