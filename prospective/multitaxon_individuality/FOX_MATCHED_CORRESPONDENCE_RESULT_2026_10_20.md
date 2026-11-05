# Fox continuation: temporal correspondence and geographic overlap are now paired

**Status:** completed exploratory analysis of one public source, with explicit
support limits. No new cross-taxon or causal individuality claim.

## What is completed

The original Movebank source DOI `10.5441/001/1.304` was retrieved and checked
against its public bitstream MD5 values. The event file has **166,338 rows**;
source manual-outlier removal and the declared GPS quality filters retain
**145,581 positions from 35 source animal identifiers**. These produce
**130,923 same-day 9--15-minute steps**. All retained observations are GPS and
visible; their animal/tag pair and timestamp match one source deployment.
Four adjacent pairs across collar/deployment changes are excluded.

The former pilot is now fully reproducible: **all 60 reported count values
match exactly, and all 30 reported gains match within 7.64e-17**. The former
numbers were not a transcription or computational error. See
[legacy reproduction](FOX_LEGACY_REPRODUCTION_2026_10_20.json).

The new analysis makes two contrasts explicit: (a) the same calendar dates
train every animal and every later date is held out; (b) an alternative animal
must have enough observations in every context used to score the target. It
also computes geographic overlap from the **same animals and heldout period**.
The design was recorded in local commit `e8198f0` before these new outputs were
calculated; it was uploaded with the results, rather than independently registered
in advance. The source and older pilot outcomes had already been inspected, so
the work remains exploratory.

## Full primary-scale results

R here is represented by descriptive log predictive gain B: individual model
minus the context-matched pooled model, averaged equally over days and then
animals. Positive B favors the personal model; negative B favors pooling.
X is day-balanced 2D occupancy overlap, from zero to one. It is not resource
sharing or simultaneous encounters. The table uses 1-km cells and 6-hour UTC
contexts; the JSON reports **both fixed 1- and 2-km scenarios**.

| Source site and month | Evaluated animals | Test steps | B, nats/step | Mean X at 1 km | Allowable whole-identity maps | Reference tail fraction |
|---|---:|---:|---:|---:|---:|---:|
| Somerley 2019-05, designated primary | 4 | 5,783 | +0.001442 | 0.182089 | 2 | 0.500000 |
| Britford 2016-05 | 4 | 5,521 | -0.011198 | 0.759472 | 24 | 0.041667 |
| Britford 2017-03 | 0 | 0 | Not estimable | Not estimable | — | — |
| Britford 2017-04 | 3 | 1,990 | +0.048854 | 0.277725 | 1 | Not calibratable |
| Somerley 2019-06 | 5 | 5,874 | +0.000029 | 0.284894 | 1 | Not calibratable |
| Britford 2016-06 | 1 | 171 | Not estimable | Not estimable | — | — |
| Britford 2016-04 | 0 | 0 | Not estimable | Not estimable | — | — |
| Britford 2017-05 | 4 | 2,878 | -0.007804 | 0.431011 | 1 | Not calibratable |
| Somerley 2018-05 | 4 | 2,652 | -0.037996 | 0.188254 | 1 | Not calibratable |
| Somerley 2019-04 | 0 | 0 | Not estimable | Not estimable | — | — |

The six rows with paired descriptive R/X have only **3--5 evaluated animals**.
None supplies a large-population independent validation. Months reuse animals;
the source contains two sites and four deployment-year labels, not ten independent
populations. Animals were not permanently marked, so distinct identifiers across
years do not prove different biological individuals.

### The designated primary is support-limited

Somerley May 2019 had nine evaluated animals under the former animal-specific
calendar halves. The shared-calendar analysis retains four, contributing 59
animal-days. Only **two** of those four identities can move between permissible
whole-profile assignments. Its smallest possible reference tail fraction is
therefore 1/2. This data configuration cannot provide a fine-resolution identity
test, regardless of its 5,783 test steps.

The former +0.023361 and new +0.001442 gains use different animals and time windows.
Their difference **is not** an estimated percentage loss of a biological effect
or an isolated effect of calendar leakage. The old calculation remains a valid
reproduced description of its stated split. The new split answers a more stringent
common-future-period question, which is a sensitivity analysis within the broader
pattern-first ecology programme, not a requirement that all ecological work be
framed as forecasting.

### Correspondence and positive model gain are different claims

Britford May 2016 gives the smallest observed reference tail fraction: the true
mapping ranks first among 24 allowed mappings. But its personal model has
**B = -0.011198**, below the pooled model. Thus the true correspondence beats
alternative correspondences while pooling still predicts better. It is incorrect
to promote the 1/24 result as positive personal-versus-pooled R.

The reference averages complete identity assignments on fixed observations. Its
tail fraction assumes uniform correspondence over allowed maps. That assumption
is not guaranteed by this observational study; the number is **not a randomized
biological p-value**. The ten reused source months, two scales and secondary
assays were all disclosed; no multiplicity-controlled biological significance
claim is made.

## What the measurement diagnostics show

The source paper reports active-animal GPS accuracy of 10--15 m for 90% of fixes.
The old 0.05 km/h boundary is only 8.3 m per ten minutes. Therefore the low-speed
class may contain persistent GPS-error characteristics. The source also provides
activity sensors, with activity defined as >=2 seconds on **both** axes during a
90-second fix attempt. We applied that published rule as an additional observed
channel, without substituting it for the original outcome.

| Cohort | Original three speed classes: B / reference tail | Binary speed >=0.5 km/h: B / reference tail | Activity sensor: B / reference tail |
|---|---:|---:|---:|
| Somerley 2019-05 | +0.001442 / 0.500 | +0.003754 / 0.500 | -0.003849 / 1.000 |
| Britford 2016-05 | -0.011198 / 0.041667 | +0.001679 / 0.125 | -0.011015 / 0.125 |

The smallest three-class tail fraction is not repeated by these two diagnostics.
That does not identify GPS noise as its cause: the channels measure different
behavioral quantities, and the limited mapping resolution remains. Activity is a
different sensor channel on the same collars, not independent equipment. Collar
fit, duty cycle, reproductive role, sex and fine-scale habitat remain possible
carriers of correspondence.

Source methods: Porteus et al. (2024),
https://doi.org/10.1007/s10344-023-01759-y . The paper already described home-range,
site-density, overlap and activity differences. We do not claim discovery of those
species-level patterns.

## Spatial scale is consequential

For the matched four Somerley foxes, mean X is **0.148719 at 0.5 km** and **0.182089
at 1 km**. Three of six dependent pairs have no shared occupied cells at the
unshifted 1-km grid. For matched Britford foxes, X is **0.282124 at 0.5 km**,
**0.759472 at 1 km**, and **0.959129 at 2 km**. The latter source's small spatial
extent makes coarse-cell saturation especially influential.

Even a fixed 1-km width has origin sensitivity: four zero/half-cell origins give
mean X **0.173181--0.254024** at Somerley and **0.336124--0.759472** at Britford.
Hence these cannot be presented as scale-free measures of ecological niche
overlap. Geographic X differs in these sampled cohorts, but this does not
establish that individuality causes or prevents resource partitioning.

## Reproduction and validation

Run with the original files obtained separately from Movebank:

```bash
python prospective/multitaxon_individuality/fox_source_pipeline_v1.py \
  --events /path/to/original-events.csv \
  --reference /path/to/original-reference.csv \
  --output /tmp/fox-legacy-reproduction.json

python prospective/multitaxon_individuality/fox_matched_correspondence_v1.py \
  --events /path/to/original-events.csv \
  --reference /path/to/original-reference.csv \
  --output /tmp/fox-matched-correspondence.json
```

Original event MD5: `5a997cd23c18f8cc9435636b5376b3ec`.
Reference MD5: `c2cc154a65ab0bdba1834532398ebd6c`.
Both SHA256 values and aggregate attrition are in the result JSON.

Validation covers source quality and deployment boundaries, fixed calendar
separation, true day weighting, identical/known/reversed correspondence,
identity-only support, actually movable identities, activity thresholds,
geographic extremes and missing shared-date opportunity. An independent review
also matched the reference enumerator against brute force for 40 asymmetric
support matrices with two through five identities.

**Next substantive work:** expand actual shared-place cohorts using the existing
database-derived source queue; retain this source as a small, fully reproducible
R/X example. Do not repeatedly tune its cutoffs or reuse these months as external
replication. Resource exposure E and encounter T remain unmeasured.
