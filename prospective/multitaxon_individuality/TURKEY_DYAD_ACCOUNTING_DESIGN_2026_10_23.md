# Declared after prior inspection: source-wide winter GPS-nearness accounting by annual-centroid pair band

**23 October 2026. POST-INSPECTION descriptive algebra, not preregistered.**
Already inspected: the original seasonal GPS day-shift L1 in turkey 2019/2020,
the source-distance filters <=5/10/25 km, and the new original-GPS result
showing one turkey in all five of the 2020 >10-km annual-centroid dyads.
This plan fixes algebra, checks and full source-wide disclosure before any new
decomposed contribution table is committed.

## Question

The 2020 overall winter-excess GPS near-position L1 is positive for the
21 eligible original turkey dyads, yet the 14 <=5-km annual-centroid dyads
show an opposite or near-zero contrast. **How much of the original
dyad-weighted source mean is contributed by the five 10–25-km annual-center
dyads that ALL share the same one GPS-tagged bird?** Do not mistake 5
dependent dyads for independent animal replicates.

## Inputs and frozen universes

Use ONLY already-published verified aggregate files:
- SOURCE_SPATIAL_INFLUENCE_SUMMARY_2026_10_22.json, original Git blob
  12b1551acbf6cdfe2467449d221294e786b60292
- TURKEY_SINGLE_MOVER_ORIGINAL_GPS_2026_10_22.json, pinned byte
  SHA256 7b84c27d0b05449e0a53dc465964c7fd0c8c3aed81478556387cb706598f4225,
  independently verified as original complete wild-turkey Movebank GPS
  DOI 10.5441/001/1.671, with publisher MD5 and source fixed SHA256;
  see the separate original-source audit.

No source GPS tracks, animal tags, exact times/dates, site coordinates,
dyad values or local-population membership are needed or published here.

Treat ALL 2019/2020 source years, BOTH GPS time tolerances 900/1800 sec,
BOTH focal orientations (original A->B and reversed B->A), and ALL
spatial nearness radii 0.5/1/2 km. Original annual-center pair subsets
are <=5, <=10 and <=25 km, with known 2020 dyad counts 14/16/21 and
2019 73/78/112. The year-wide 25km risk set and its L1 score are unchanged.

## Exact algebra

For a fixed source-year/time tolerance/orientation/radius, let
n5,m5, n10,m10, n25,m25 be the existing dyad counts/mean
winter-minus-summer L1 from the nested annual-center sets.
Define **summed per-dyad numerator contribution** A5=n5*m5,
A5to10=n10*m10-n5*m5, A10to25=n25*m25-n10*m10.
Define per-dyad annulus means by dividing each numerator
by its known pair count n5, n10-n5 and n25-n10.
The source mean must exactly reconcile:

(n5*m5 + (n10-n5)*m5to10 + (n25-n10)*m10to25)/n25 = m25.

Define the *fraction of the signed source mean numerator*
contributed by far 10–25km dyads as
C_far=A10to25/(n25*m25), ONLY if abs(n25*m25)>1e-12.
C_far is an arithmetic contribution fraction, NOT a variance
explanation, effect share, causal attribution or probability;
it may be negative or >1 when near and far groups offset.

The previously source-confirmed unique 2020 annual5
isolated animal is in **all 5 10–25km annual-center dyads**
and all six of its isolated-to-core animal pairs, but the
single source ID is never output. All 2019 components'
local-population independence remains unverified.
The 5 to 10km annulus has only two 2020 pairs and can also
include the isolated animal, so don't claim the far5
partition isolates all contributions from that bird.

## STOP, verification and interpretation

Verify immutable source Git-blob/SHA256, exact source-year/scale
cohort denominators, no overlap or missing annulus, and exact
reconstruction of every original 25km mean. Output all
2 years ×2 tolerances ×2 orientations ×3 radii =24 rows
with every numerator and annulus mean, and signed
contribution ratio only when defined.
A 2020 10–25km annulus n5 (and 5–10km n2) is BELOW the
original minimum 8-pair scoring gate for standalone biological
estimands: these are **algebraic components of the previously
estimable 21-pair aggregate only**. Do not report the annulus
as an independent biological statistical effect, p-value or
population replication.

A positive share >100% can occur because the other
16 dependent dyads collectively contribute negative
signed values. That's a statement about this source
estimator and sampling geometry, NOT proof that the
moving turkey caused encounters, coordinated flocking
or resource selection. The original adjacent-day
reference preserves one day's path order but not
between-day habitat/weather. Native source GPS/UTC
clock and location error are uncalibrated.
