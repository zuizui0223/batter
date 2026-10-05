# Transparent horizontal-vertical allocation axis contract v1

## Status

**POST-OUTCOME INTERPRETABILITY / FALSIFICATION DIAGNOSTIC.**

Frozen after:
- fixed-bin H-only and V-only individuality were supported in P. hastatus;
- the 2-D (H,V) carrier was supported in both 2022 and 2023;
- H and V individual coordinates were negatively coupled;
- the empirical 2-D PC1 direction was observed to be close to the contrast H-V.

No transparent H-V contrast identity statistic has yet been calculated.

## Question

Can the persistent 2-D field policy be reduced to the simple, non-fitted allocation scalar

`A = (H - V)/sqrt(2)`

where:
- high A = relatively more horizontal movement intensity;
- low A = relatively more vertical movement intensity?

This directly tests whether the joint policy is an **allocation trade-off** rather than an arbitrary two-dimensional fingerprint.

## Data

Use exactly the fixed-bin 360-s P. hastatus 2022 and 2023 sessions from
`PHYLLOSTOMUS_FIXED_BIN_HARMONIZATION_CONTRACT_V2.md`.

Per session:
- H = mean(z median horizontal speed, z p90 horizontal speed);
- V = mean(z median absolute vertical speed, z p90 absolute vertical speed).

No refitting or PCA enters the transparent scalar.

Also define the orthogonal reference:

`I_orth = (H + V)/sqrt(2)`.

This is the same direction as the previously tested scalar FlightIntensity, up to scale.

## Held-out identity statistic

For each target session q from individual i within frozen cohort c:

1. self centroid = equal-session mean A over all other sessions of i in c;
2. donor centroid = mean A for every other evaluable individual j in c;
3. self distance = |A_q - self centroid|;
4. donor distance = equal-donor mean |A_q - donor centroid|;
5. K_q = donor distance - self distance.

Require:
- >=1 other self session;
- >=2 donor individuals.

Aggregate equally:
- within individual;
- then across individuals within year.

## Null

Within each frozen cohort independently, shuffle the exact individual-label multiset across complete session A values.

9,999 permutations.

Seeds:
- 2022: `202610051501`
- 2023: `202610051502`.

## Support rule

A year supports the transparent allocation carrier if:
- K_year > 0;
- one-sided p <= 0.05;
- >=70% of evaluable individuals have positive individual mean K.

## Orthogonal reference

Repeat the identical calculation for `I_orth=(H+V)/sqrt(2)` using independent seeds:
- 2022: `202610051503`
- 2023: `202610051504`.

This is a mechanism reference, not a rescue of the frozen scalar gate.

## Axis geometry

Report:
- empirical individual-centroid PC1 in (H,V);
- cosine of empirical PC1 with A-axis [1,-1]/sqrt(2);
- cosine with I-axis [1,1]/sqrt(2).

## Interpretation

If A is supported in both years while I_orth is weak/unsupported in 2023:

> field individuality is carried primarily by a horizontal-versus-vertical allocation tendency, not by a single overall movement-intensity magnitude.

This provides an interpretable field analogue of a low-dimensional control policy without claiming that the laboratory Rhino axes transfer literally across species.

## Ceiling

This is post-outcome and cannot reopen the frozen JAE bridge or establish that A causes vertical-distribution shape.
