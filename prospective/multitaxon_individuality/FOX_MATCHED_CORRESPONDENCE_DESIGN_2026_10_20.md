# Fox shared-place temporal correspondence: bounded exploratory continuation

Date: 2026-10-20. Source baseline: `fcbc2a3094786d669c9e8d0711d04414caa48c63`.

## Purpose and evidence status

Advance the existing pattern-first R/X programme using the already opened red-fox
source, DOI `10.5441/001/1.304`. The 19 October pilot contains descriptive gains
without a null calibration. These are known exploratory outcomes. This document
fixes the following continuation before its new numerical outcomes are computed;
it does not turn the reused source into an independent confirmatory experiment.

Primary reported cohort is Somerley, deployment year 2019, May 2019, previously
the largest heldout pilot cohort. Run **all ten** site-year-month combinations in
`FOX_COMMON_PLACE_HELDOUT_R_PILOT_2026_10_19.json`, without selection by new gain
or significance. Months reuse animals and are not independent studies. Source
animals were not permanently marked across years (Porteus et al. 2024), so unique
reference labels across years do not establish biological independence.

## Data and chronology

Use the pinned public CC0 original event and reference files, verify original
MD5 and record SHA256. Raw data remain in temporary storage, never in git.
Reproduce the original manual-outlier, HDOP <=5, satellite >=4, GPS-visible,
9--15-minute same-UTC-date, speed <=10 km/h rules. Retain animal identity from
the original reference table, not the tag identifier. Never join a step across
a collar change. Audit source-time/deployment discrepancies explicitly.

The pilot split dates separately for each animal. The continuation uses a
**common calendar cut**: dates 1 through floor(days_in_month/2) are training;
all later dates are testing. No animal's training observation may lie on any
animal's testing date. Cohort source eligibility remains >=80 valid steps on
>=6 observed dates. No date-specific outcome enters the cut.

## Fixed opportunity and models

At the primary 1-km grid and 6-hour UTC bin, an animal supports a training context
only with >=15 steps on >=2 dates. The context must have >=2 supported animals.
Use the existing equirectangular grid: longitude x111.32 xcos(mean retained source
latitude), latitude x111.32, floored from geographic origin. Keep this spatial
reference for every outcome. This is coarse shared place, not identical resource
opportunity or proven synchronous co-presence.

For each target, freeze test observations at contexts supported by the target
and >=1 other training animal. Require >=15 test steps on >=3 test dates. Pool
the training counts of supported animals within a context with Jeffreys 0.5 per
class; shrink each personal multinomial toward that pooled probability with
15 pseudo-observations. No test outcomes train either model. Average log
personal/pooled gain within test day, then over days, then equally over targets.

Compute a complete target x donor score matrix on **each target's same frozen
observations**. A donor is allowed only if it independently supports **every**
context of that target's frozen test mask. A missing donor model cannot be
replaced with pooled probabilities and then used to create a diagonal advantage.
Only final evaluated targets enter the bijective mapping set; extra training-only
animals may inform the pooled comparator but cannot become fictitious test targets.

## Conditional correspondence reference, not a causal biological p-value

Enumerate every support-compatible bijection of whole training identity profiles
to heldout target identities. Include the true identity and other maps with fixed
points. Preserve complete observations, temporal order, all dates, context masks,
class counts and fitted profiles. There is no fix-level shuffle and no eligibility
reselection for a map. Report allowed-map count, movable animals, observed gain,
reference mean, excess, exact tail fraction and reference score quantiles.

This tail fraction assumes **uniform correspondence conditional on the allowed
mapping set**. Shared geographic support alone does not establish that assumption
for wild foxes. Sex, reproductive role, collar fit/noise, duty cycles and persistent
fine-scale geography remain possible correspondence carriers. Therefore call the
number a conditional mapping-reference tail fraction, not a design-based biological
randomization p-value, and never infer causal specialization from it.

If only the identity map exists, report NOT CALIBRATABLE, with no tail fraction.
If fewer than 20 maps exist, report the reference descriptively and the attainable
resolution; do not claim 5% evidence. Exactly 20 maps only permits <=0.05, not
<0.05. Do not widen cells, drop animals, select contexts or change cutoffs to obtain
a smaller tail fraction. Fixed animals are explicitly not tested by the mapping.

## Paired X and measurement diagnostics

For the **same final R animals and heldout calendar period**, estimate day-balanced
2D geographic overlap from **all quality-controlled fixes**, not only R's selected
shared contexts. Dyads require >=3 jointly observed dates. Missing temporal support
is missing, not zero overlap. Report dependent dyad counts and exact cohort size;
do not bootstrap pairs as independent units or fit a cross-taxon regression.

Report the primary 1-km/6-hour result and a fixed 2-km/6-hour sensitivity, each with
its own disclosed support. No result determines which scale is presented. Calculate
X also at 0.5/1/2 km and four zero/half-cell origins for the fixed primary R cohort
to disclose grid sensitivity without claiming a new inferential endpoint.

On the same observed step masks, retain the pilot three speed classes (<0.05,
0.05--<0.5, >=0.5 km/h), and add two expressly secondary diagnostics:

1. Binary >=0.5 km/h, merging the two low-speed classes. The old 0.05 km/h cutoff
   corresponds to about 8.3 m in ten minutes, below the source's 10--15 m accuracy
   range for 90% of active fixes. This is a noise-sensitivity check, not calibration
   of actual location error.
2. Source-defined activity: both x and y recorded >=2 seconds during the 90-second
   fix attempt (Porteus et al. 2024). Use origin activity and keep missing activity
   separate. It is an independent sensor channel, not independent equipment or
   an independent ecological resource measure. Collar fit may still carry identity.

No diet, habitat-resource E, encounter T, resource competition, stable personality,
or cross-clade law is established by this continuation.

## Verification and deliverables

Before computing real corrected outcomes, test: fixed global calendar split;
day/animal weighting; a diagonal-only support matrix; identical profiles; known
four-identity synthetic correspondence; reverse correspondence; and geographic
overlap with absent time opportunity. Then save code, all aggregate outputs,
original checksums, a concise result document and updated current-state README.

Source article: https://doi.org/10.1007/s10344-023-01759-y .
No new literature survey is part of this work.
