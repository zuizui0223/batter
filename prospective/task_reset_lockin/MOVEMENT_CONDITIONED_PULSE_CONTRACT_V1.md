# Movement-conditioned pulse-identity sensitivity contract v1

## Status

**POST-PRIMARY / POST-SENSING DIAGNOSTIC SENSITIVITY.**

Frozen after:
- movement Primary B supported;
- pulse-only cross-configuration identity supported.

This sensitivity asks whether the pulse identity can be explained by the already-measured movement-policy features.

It cannot upgrade the pulse result to confirmatory status.

## Data

Use the same 45 *Rhinolophus nippon* trajectories.

Pulse features:
the exact six frozen features from `RHINO_PULSE_IDENTITY_CONTRACT_V1.md`.

Movement features:
the exact eight authoritative Primary B features:

1. median speed;
2. p90 speed;
3. median absolute vertical speed;
4. p90 absolute vertical speed;
5. median absolute horizontal turn rate;
6. p90 absolute horizontal turn rate;
7. path efficiency;
8. vertical range.

All 45 trajectories passed both feature pipelines in the preceding frozen analyses.

## Common preprocessing

For pulse and movement features separately:

- use Env1–Env7;
- within each environment × feature, subtract arithmetic mean and divide by sample SD;
- require finite positive SD.

This removes configuration-level means before conditioning.

## C1 — performance-conditioned pulse identity

Performance predictor matrix uses:

- median speed;
- p90 speed;
- median absolute vertical speed;
- p90 absolute vertical speed;
- vertical range.

For each of the six environment-standardized pulse features separately:

- fit ordinary least squares across all 45 trajectories:
  `pulse_feature ~ intercept + five performance features`;
- retain residuals.

No bat identity is used in the regression.

Within each environment, re-standardize each residual pulse feature by its sample SD; the environment residual mean is re-centered to zero.

Apply the exact pulse leave-one-environment-out identity estimator and cluster permutation null to the six residual pulse features.

9,999 permutations.

Seed:
`202610042251`.

## C2 — fully movement-conditioned pulse identity

Repeat C1 but regress each pulse feature on all eight movement features.

9,999 permutations.

Seed:
`202610042252`.

## Identity null

Exactly as in the frozen pulse result:

- independently within every environment, permute complete bat × environment trajectory clusters among bat labels;
- preserve trajectories and cluster sizes;
- break cross-environment identity correspondence.

Valid-permutation minimum:
9,500.

## Reporting

For C1 and C2 report:

- residual pulse feature count;
- condition number / rank of the movement design matrix;
- P residual identity statistic;
- individual P_i;
- positive fraction;
- one-sided permutation p;
- null 95% interval.

## Interpretation

### C2 supported

Portable sensing individuality contains information not explained by the eight measured movement-policy summaries.

This supports a broader **individual sensing style / sensorimotor policy** rather than pulse timing being merely a by-product of moving differently.

### C1 supported but C2 unsupported

Pulse identity is not explained by performance magnitude alone, but steering/efficiency covariation may account for it.

### Both unsupported

The pulse-only identity may be downstream of stable movement differences rather than an independent sensing component.

## Ceiling

Residual pulse identity still does not identify whether the individual policy is:
- learned;
- morphological/physiological;
- developmental;
- genetically constrained.

