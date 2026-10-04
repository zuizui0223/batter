# Route-conditioned pulse-identity sensitivity contract v1

## Status

**POST-PRIMARY MECHANISM DIAGNOSTIC. NOT CONFIRMATORY.**

Frozen after:
- cross-configuration pulse identity was supported;
- movement-conditioned pulse identity was supported;
- absolute route centroid was identified as the strongest within-configuration route-position carrier;
- scale-free geometry identity was supported but environment-sensitive.

No result from the present residualizations has yet been calculated.

## Question

Can portable pulse-timing individuality be explained by the bat flying:
1. with a different measured movement policy, and/or
2. through a different absolute lane in the arena, and/or
3. with a different scale-free route geometry?

If pulse identity remains after these are removed, sensing individuality is not adequately explained as a downstream consequence of where or how the bat moved.

## Data

Use exactly the 45 authoritative *Rhinolophus nippon* trajectories.

Pulse response:
the exact six pulse features from `RHINO_PULSE_IDENTITY_CONTRACT_V1.md`.

### Movement predictors

The exact eight Primary B features:
- median speed;
- p90 speed;
- median absolute vertical speed;
- p90 absolute vertical speed;
- median absolute horizontal turn rate;
- p90 absolute horizontal turn rate;
- path efficiency;
- vertical range.

### Absolute lane predictors

Three coordinates of the exact route-centroid definition used in the post-primary route-axis diagnostic:

`centroid_xyz = mean(route101, axis=0)`.

### Scale-free geometry predictors

The exact eight geometry-only features from
`GEOMETRY_ONLY_POLICY_DIAGNOSTIC_CONTRACT_V1.md`.

## Common first-stage standardization

Within each environment and for every pulse or predictor feature:
- subtract environment arithmetic mean;
- divide by environment sample SD;
- require finite positive SD.

This removes configuration-level means before residualization.

## C3 — movement + absolute-lane conditioned pulse identity

Predictor matrix:
- 8 movement features;
- 3 route-centroid coordinates.

For the six standardized pulse features jointly:
- include intercept;
- fit ordinary least squares using the Moore-Penrose least-squares solution;
- fitted values are the projection onto the observed predictor column space;
- collinear predictor columns are allowed;
- report numerical matrix rank and condition number;
- require residual degrees of freedom `45 - rank(X) >= 15`.

Re-standardize residual pulse features within environment.

Apply the exact pulse cross-configuration identity estimator and cluster-label permutation null.

Permutations: **9,999**  
Seed: `202610042271`.

## C4 — movement + geometry + absolute-lane conditioned pulse identity

Predictor matrix:
- 8 movement features;
- 8 scale-free geometry features;
- 3 route-centroid coordinates.

Use the same projection/residualization rules.

Require residual degrees of freedom >=15.

Permutations: **9,999**  
Seed: `202610042272`.

## Residual pulse feature support

After residualization and within-environment re-standardization:
- drop a pulse feature species-wide if any environment has zero/nonfinite residual SD;
- require >=4 of the original six pulse features.

No feature selection based on identity performance.

## Identity support

Descriptive diagnostic support requires:
- residual pulse identity statistic > 0;
- one-sided permutation p <= 0.05;
- >=70% evaluable bats have positive individual means;
- >=9,500 valid permutations.

## Interpretation

### C3 supported

Pulse individuality is not explained by measured movement policy plus absolute lane placement.

### C4 supported

Pulse individuality is not explained by measured movement policy, scale-free trajectory geometry, or absolute lane placement.

This is strong evidence for a portable individual **sensing component** of the broader sensorimotor policy.

## Ceiling

Even C4 support does not identify the origin of the sensing component. It may reflect:
- long-lived learned sensing style;
- stable physiology;
- vocal-motor constraints;
- developmental history;
- morphology not represented by the measured movement/route variables.

It is not evidence for a specific cognitive mechanism.
