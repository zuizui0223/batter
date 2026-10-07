# Rhino-to-Mini exact-N support resampling contract v1

## Status

**POST-PRIMARY CROSS-SPECIES SUPPORT-STRESS DIAGNOSTIC.**

Frozen after:
- Rhino portable one-dimensional identity was supported;
- Miniopterus failed PCA dimensions 1–8 and supervised identity dimensions 1–3;
- a four-bat / sparse-training-centroid Rhino stress test remained supported in all leave-one-bat-out subsets.

No exact-total-N=19 Rhino resampling outcome has been calculated before this contract.

## Question

Can the Rhino–Mini contrast be explained simply by Miniopterus having only 19 trajectories?

## Structural target

Use the already-opened Miniopterus archive only to determine its **sampling structure**:
- total trajectory count;
- trajectory count per obstacle environment;
- number of distinct bats per environment.

Do not use Mini individual-identity outcomes to construct a favorable Rhino resample.

The target total must equal the Mini archive total: **19 trajectories**.

## Rhino source

Use the authoritative 45 feature-valid *Rhinolophus nippon* trajectories.

For every resample:

1. choose one of the five possible four-bat Rhino subsets;
2. in each of Env1–Env7, sample without replacement exactly the number of trajectories observed in Mini for that environment;
3. require the sampled environment to contain at least the Mini number of distinct bats observed in that environment;
4. require all four selected Rhino bats to be evaluable by the leave-one-environment identity estimator (>=3 sampled environments);
5. require exactly 19 sampled trajectories.

If a proposed sample fails, reject and redraw.

## Standardization

For each accepted 19-trajectory Rhino sample, use the **same standardization family as the Mini dimensionality scan**:

- subtract each sampled environment's feature mean;
- pool the environment-centered residuals across environments;
- divide by the pooled residual SD feature-wise.

This avoids giving sparse Rhino samples the denser within-environment SD estimation available in the original Rhino primary.

## Representations

Evaluate two predeclared one-dimensional representations.

### R1 — sample-specific training-only PCA1

For every held-out target environment:
- fit PCA only on sampled training-environment rows;
- project training and target rows on PC1;
- compute leave-one-environment self-versus-other identity advantage.

### R2 — transparent FlightIntensity

Within each accepted sample:

[
FlightIntensity = mean(z_1,z_2,z_3,z_4)
]

using the first four standardized speed / vertical-speed features.

Use the same leave-one-environment identity estimator.

## Identity estimator

For both R1 and R2:
- training centroid averages trajectories within bat × environment first;
- then averages training environments equally within bat;
- require >=2 non-target environments for focal and donor centroids;
- target K = mean distance to donor centroids − distance to own centroid;
- aggregate equal target trajectory -> equal biological bat -> sample K.

## Resampling plan

For each omitted Rhino bat A–E:
- obtain **1,000 valid exact-N=19 resamples**;
- total planned valid resamples = **5,000**.

Seed:
`20261007941`.

Maximum proposal budget:
500,000 proposals.

Stop with a structural failure rather than relaxing any condition if 5,000 valid samples cannot be obtained.

## Reporting

For each omitted-bat subset and pooled across all five subsets, report for PCA1 and FlightIntensity:

- median K;
- 5th and 95th percentiles;
- fraction K > 0;
- fraction with >=3/4 positive bat means;
- fraction satisfying both directional conditions;
- empirical percentile of the already-opened Mini value within the Rhino exact-N distribution.

Reference Mini values:
- PCA1 K = **-0.1687569214**;
- full 8-D Mini is not used in this one-dimensional stress test;
- Mini transparent/fixed-Rhino-axis failures remain contextual references only.

## Descriptive support-stress rule

Call the Rhino one-dimensional signal **robust to Mini-like total N** for a representation if, pooled across all exact-N samples:

1. >=90% of resamples have K > 0;
2. >=80% have >=3/4 positive bat means;
3. the Mini PCA1 K lies below the 5th percentile of the Rhino exact-N PCA1 distribution for R1.

For FlightIntensity, criteria 1–2 are used; there is no numerically identical Mini species-specific transparent scalar primary for criterion 3.

## Interpretation

If Rhino remains strongly positive under exact-N=19 resampling, the species contrast is not plausibly explained by total trajectory count alone.

If Rhino frequently loses identity at N=19, the current Mini failure cannot be cleanly separated from support/power.

## Ceiling

This diagnostic still does not equalize:
- species-specific measurement noise;
- exact bat × environment presence pattern;
- flight morphology;
- sensory system;
- nonlinear policy structure.

It is a support stress test, not a causal species comparison.
