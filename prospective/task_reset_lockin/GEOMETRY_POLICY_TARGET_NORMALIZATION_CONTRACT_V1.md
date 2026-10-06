# Geometry-policy target-normalization sensitivity contract v1

## Status

**POST-PRIMARY ROBUSTNESS DIAGNOSTIC.**

Frozen after:
- scale-free geometry identity is supported;
- geometry-family ablation is complete.

No alternative-normalization geometry result has yet been calculated.

## Concern

The parent geometry-only diagnostic standardizes each feature within each target obstacle configuration.

That removes legitimate configuration-scale shifts, but it also uses target-environment dispersion.

This diagnostic asks whether portable geometry identity survives when target scaling information is withheld.

## Raw geometry features

Use exactly the eight frozen dimensionless/angular geometry features:

1. 3-D path efficiency;
2. horizontal displacement ratio;
3. absolute vertical displacement ratio;
4. vertical range ratio;
5. median absolute horizontal turn angle;
6. p90 absolute horizontal turn angle;
7. median absolute vertical slope;
8. p90 absolute vertical slope.

Use the exact 45 route-valid *Rhinolophus nippon* trajectories.

No feature deletion.

## S1 — target-centered, training-scaled

For held-out target environment e:

1. within every training environment, subtract that training environment's feature mean;
2. pool all centered training residuals;
3. compute one training-only SD for each feature;
4. target environment contributes its feature mean only;
5. divide target-centered values by the training-only pooled SD.

Thus:
- target location shift is removed;
- target variance is never used.

Apply the same transformation to training trajectories.

## S2 — fully training-only global scale

For held-out target environment e:

1. pool all training trajectories;
2. calculate one training-only global mean and SD per feature;
3. apply those values unchanged to both training and target trajectories.

Target contributes neither mean nor SD.

This is deliberately stronger and allows configuration-level geometry shifts to remain.

Failure of S2 does not refute a relative policy-coordinate interpretation.

## Cross-configuration identity estimator

For each target environment:
- average trajectories within bat × training environment;
- average those environment centroids equally within bat;
- require >=2 training environments for own centroid;
- require >=2 donor-bat centroids;
- K = mean donor distance - own distance;
- equal target trajectories within bat;
- equal bats in programme statistic.

## Null

Within every environment independently permute complete bat labels among trajectories.

The transformation is label-free and fixed for each target-environment fold.

9,999 permutations.

Seeds:
- S1: \`202610061201\`
- S2: \`202610061202\`

Require >=9,500 valid permutations.

## Support

A variant is supported if:
- K > 0;
- p <= 0.05;
- >=70% of evaluable bats positive.

## Interpretation

### S1 supported

Target-specific variance normalization is not required for portable geometry individuality.

### S2 supported

Strongest result:

> scale-free personal route geometry transfers even when the unseen environment contributes no normalization information.

### S1 supported, S2 unsupported

Personal geometry is portable primarily **relative to the current task geometry**, not as one absolute route-shape vector across arenas.

### S1 unsupported

The parent geometry result depends materially on target-environment scaling and must be narrowed.

## No rescue

Do not:
- change feature set;
- select environments;
- switch normalization after output;
- use target SD in S1 or S2;
- drop bats based on result.
