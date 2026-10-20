# Mule-deer seasonal movement and geographic sharing: analysis design

**Status:** exploratory source-based extension of the pattern-first database
programme; recorded before the deer R/X outputs are opened. Existing source
availability and coarse support counts have already been inspected. This is not
an independent preregistration or a cross-taxon validation.

## Question and source

For the source-labeled Sublette Herd, do persistent individual differences in
two-hour displacement coexist with seasonal changes in shared geographic use?
Analyze all 36 calendar months of 2018–2020, including months whose R is not
estimable. Do not select months by the size or sign of their results.

Source DOI: <https://doi.org/10.5441/001/1.708>, CC0. The verified original GPS
file contains 948,632 rows for 135 reference animals. Reference metadata label
all animals adult female, Sublette Herd, neck-collared, and manipulation `none`.
The source does not label individual migrant/resident strategy, provide location
error estimates, or supply usable deployment dates. A herd label does not establish
instantaneous association or identical resource access. The final 232 source rows
fall in 2021 and are excluded from this analysis window.

## Observations and common time scale

Use the checksum-pinned original GPS and reference files. Require GPS sensor,
explicit visibility, expected taxon, finite in-range coordinates, parseable source
time, and an unambiguous reference animal/tag join. Audit duplicate timestamps,
source order, tag changes, and available outlier flags. Naive source timestamps
remain **source-clock times**: the README permits UTC or GPS time, so their UTC
offset is not asserted independently verified.

Build adjacent steps within the same animal and tag, source-calendar date and
month, with an elapsed time of **108–132 minutes**. Use origin location and origin
time for the context. Endpoint distance is the haversine great-circle net
displacement; it is not traveled path length. No speed cutoff is applied in the
primary analysis. The endpoint is

\[
y=\log\{1+(2\,\mathrm{hours}\times\mathrm{speed}_{km/h})/0.1\,\mathrm{km}\}.
\]

This fixed transformation represents standardized two-hour displacement intensity.
It does not assign rest, feeding or migration states, and it keeps the physical
scale unchanged across months. The source's two-hour observations cannot resolve
fine-scale encounter avoidance.

## R: repeated conditional displacement distribution

Each animal-month initially needs at least 80 valid steps on 10 dates. Split the
calendar month at floor(number of calendar days/2). Fit on the first half and score
the second, then reverse the halves. Every scored date is absent from its fitted
model. This two-fold cross-fitting measures out-of-period repeatability; it is not
restricted to future forecasting.

Primary contexts are **5-km cells × 6-hour source-clock bins**, using a fixed
equirectangular approximation (111.32 km/degree, longitude multiplied by the cosine
of the retained source's mean latitude). Each animal-context training profile
requires ≥15 steps on ≥3 dates. A target's test context needs its own profile and
at least one other qualified animal's profile. Freeze this observation mask before
scoring the two models. An animal must have ≥15 evaluable steps on ≥3 dates in
each fold; the final monthly cohort is the intersection of both folds' animals.

Within a training profile, weight dates equally and steps within a date equally.
The peer distribution P excludes the target animal and weights other qualified
animals equally. The personal distribution is the actual mixture

\[
F_i=(1-\alpha_i)P_{-i}+\alpha_i Q_i,
\quad \alpha_i=d_i/(d_i+5),
\]

where Q is the target's day-balanced empirical profile and d its training-date
count in that context. Five pseudo-days is fixed before output inspection.
Evaluate both distributions with the continuous ranked probability score (CRPS):

\[
C(F,y)=E_F|Z-y|-\tfrac12 E_F|Z-Z'|.
\]

The gain is **peer CRPS minus personal CRPS**: positive favors the personal
distribution. Average scored steps within dates, dates within animal, then animals
equally. Combine both heldout folds at the date level. Report peer/personal scores,
gain, the individual-gain distribution, sample sizes, retained observation fraction,
and peer support. This is conditional distribution predictability, not a full
behavioral phenotype, causal identity effect, or a randomized biological test.
Its units are transformed-displacement score units, **not fox-model nats**.

Report the same analysis at 10 km and at all four zero/half-cell origins for 5 km.
These are declared sensitivity scenarios, not opportunities to select a positive
result. Cohorts can differ across scenarios; retain their denominators.

## X: geographic sharing and turnover control

For the final R animals in each month, use all quality-screened GPS fixes in that
calendar month, not only R's shared-context mask. The two test folds together span
this month. Each pair needs ≥7 common observed dates. Calculate both animals'
occupancy distributions on exactly those common dates, weighting dates equally
and fixes within each date equally. The pair overlap is sum over cells of the
minimum of the two probabilities. Missing shared-date opportunity is missing,
not a zero overlap.

Report **1-, 2-, 5-, and 10-km** grids, each at origins (0,0), (half,0), (0,half),
and (half,half). All pair means are descriptive; dyads sharing animals are not
independent observations. Geographic overlap is neither diet nor synchronous use.

Separately select an **annual constant cohort**, requiring each animal to have
≥80 GPS fixes on ≥10 observed dates in every one of that year's 12 months. Run
the same X calculation on this unchanged set in every month. This controls
within-year animal turnover for X but conditions on long tracking survival. It
is not the matched monthly R cohort and does not by itself establish R seasonality.

Predefine the within-year contrast as winter months **December, January, February**
versus summer **June, July, August**. Average months equally for each pair within
each season; require ≥2 valid months in each season for a pair contrast. Report
the winter-minus-summer differences separately for each of the three years and
each scale/origin. These calendar windows do not classify actual migration events.

A supplementary paired R contrast may use the same animals represented in ≥2
R-estimable months of each season within a year. Report the changing peer references
and qualifying animals; this is a paired descriptive contrast, not independent
population replication. No p-values or population-level confidence intervals are
claimed from treating months, fixes or dyads as independent replicates.

## Validation and output boundaries

Check source receipts and attrition, step origin and cadence boundaries, separation
of fitted/scored dates, peer self-exclusion, day/animal weighting, exact weighted
CRPS against brute force (including mixtures), identical/disjoint spatial examples,
shared-date restrictions, and constant-cohort selection. An independent reviewer
checks the implementation and interpretation before completion.

Commit code, aggregate JSON, tables, a figure and an interpretive report. Do not
export raw animal/tag identifiers, exact tracking dates, coordinates, grid cells
or per-animal source records. Environmental/resource exposure E and encounter T
remain unmeasured. Report observable seasonal patterns with their three-year,
one-source limits; do not promote them to universal individuality–partitioning laws.
