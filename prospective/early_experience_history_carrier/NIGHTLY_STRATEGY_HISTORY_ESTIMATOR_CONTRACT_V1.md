# Randomized early-experience effect on nightly strategy-history dependence — estimator contract v1

## Status

**FROZEN BEFORE ANY VALUE FROM THE THREE NIGHTLY BEHAVIOURAL OUTCOME COLUMNS IS READ.**

Branch:
`prospective/early-experience-history-carrier-v1`

This is a distinct endpoint from raw route geometry.

The public archive does not contain the raw VesperStudio GPS files required to reconstruct trajectories. Therefore the original route-history endpoint remains structurally unavailable from this dataset.

The present contract instead tests a source-supported repeated nightly **behavioural strategy vector**.

## Biological question

Does randomized early environmental experience alter how strongly a bat's later nightly foraging strategy remains tied to its own recent behavioural history?

This is a test of the **strength of the personal history carrier**, not of 2-D route identity.

## Nightly strategy vector

From `Outdoor data.xlsx`, define for each bat-night:

- `Time Out (Minute)`;
- `Max distance (meters)`;
- `Explored area`.

These are all source-published nightly behavioural dimensions.

For each dimension k:

`u_k = log(1 + y_k)`.

Require y to be finite and >=0.

For the primary window, pool complete rows from the first 10 chronological Outdoor records of every structurally eligible bat and compute one global mean and sample SD for each transformed dimension.

Then:

`z_k = (u_k - mean_k) / sd_k`.

The same three global scales are used for all bats and both treatments.

If any dimension has zero/nonfinite SD: STOP.

## Structural eligibility

A bat enters outcome support screening only if:

1. it passes the frozen v2 crosswalk;
2. treatment, Season and Origin are uniquely resolved;
3. it has >=10 unique chronological Outdoor dates.

The source-native randomization block is:
`Season × Origin`.

## Primary time window

Target observation ordinals are fixed at:
**3 through 10**.

Ordinal is defined by chronological Outdoor date for that bat, before considering outcome missingness.

This window is fixed because the structural gate required >=10 dates and it targets early post-release history formation/maintenance while keeping a common observation window.

## Self history

For focal bat i at target ordinal t:

- use only complete focal rows with ordinal < t;
- take the most recent at most **5** complete prior nights;
- require at least **2** prior complete nights.

The self-history centroid is the equal-night mean of their 3-D standardized strategy vectors.

Distance:

`D_self(i,t) = Euclidean(z_it, centroid_self_it)`.

No future night enters self history.

## Other-history comparator

For the same target ordinal t:

Eligible donors are:
- different bat j;
- same source Season;
- same randomized treatment under the labeling being evaluated;
- j has at least 2 complete nights before its own ordinal t.

For each donor j:
- construct the donor history centroid from the most recent at most 5 complete nights before donor ordinal t;
- compute Euclidean distance from focal target `z_it` to that donor centroid.

Require >=2 donor bats.

`D_other(i,t)` is the equal-donor mean distance.

This comparator keeps broad treatment-level behavioural differences out of the definition of individuality: focal history is compared against peers exposed to the same early environment.

## Nightly personal-history advantage

`R_it = D_other(i,t) - D_self(i,t)`.

Interpretation:
- positive: the focal bat's own recent history predicts its nightly strategy better than histories of same-treatment, same-season peers;
- zero: no personal-history advantage;
- negative: peers' histories are closer.

## Individual history-carrier strength

For bat i:

`H_i = mean_t R_it`

over valid target ordinals 3–10.

Require at least **5 valid target nights** for H_i.

Outcome support gate after opening:
- >=5 enriched bats with valid H_i;
- >=5 impoverished bats with valid H_i.

If this fails: STOP. Do not shorten the target window.

## Primary treatment statistic

`T_obs = mean(H_i | Enriched) - mean(H_i | Impoverished)`

with equal bat weighting.

The primary alternative is **two-sided**.

- T > 0: enrichment strengthens personal-history dependence.
- T < 0: impoverishment produces stronger behavioural lock-in / lower flexibility.

Direction is not chosen after opening.

## Randomization calibration

Use the source randomization blocks:
`Season × Origin`.

Generate **9,999** treatment-label permutations, seed:
`202610041733`.

Within every block:
- preserve the observed number of enriched and impoverished bats;
- permute labels among bats in that block.

For every permutation:
1. relabel treatment;
2. recompute same-treatment donor sets;
3. recompute R_it, H_i and T.

A permutation is valid only if:
- >=5 H_i exist in each treatment;
- all included target R_it satisfy the >=2-donor rule.

If fewer than 9,500 of 9,999 permutations are valid:
**STOP_RANDOMIZATION_SUPPORT**.

Otherwise:

`p_two_sided = (1 + count(|T_perm| >= |T_obs|)) / (1 + n_valid)`.

Primary support requires p <= 0.05.

No additional sign-consistency threshold is imposed on T.

## Descriptive maintenance quantities

Report without converting them into additional primary tests:

- mean H in each treatment;
- median H in each treatment;
- number/proportion H_i > 0 in each treatment;
- R mean by target ordinal 3–10.

These show whether a treatment contrast occurs in a regime where personal-history advantage itself is positive.

## Interpretation ceiling

If T is supported, the allowed causal claim is:

> randomized early experience altered the later strength of individual-specific temporal dependence in a multivariate nightly foraging strategy.

It is **not** equivalent to:
- route-memory causation;
- a cognitive-map mechanism;
- spatial lane formation;
- fitness optimization.

Combined with the independent first-flight route result, it can motivate the broader mechanism class:
**experience-shaped history dependence can maintain individual strategy without requiring continued spatial exclusion**.

## No rescue

After outcome opening:
- no alternate transformation;
- no dropping one of the three dimensions;
- no changing target ordinals;
- no changing history length;
- no switching to same-origin donors;
- no changing donor number;
- no one-sided treatment test;
- no post-hoc subgroup analysis as a replacement primary.
