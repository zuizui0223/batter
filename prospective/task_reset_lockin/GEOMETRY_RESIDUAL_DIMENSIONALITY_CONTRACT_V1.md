# Cross-fitted residual-geometry dimensionality contract v1

## Status

**POST-PRIMARY EXPLORATORY FALSIFICATION DIAGNOSTIC.**

Parents:
- `GEOMETRY_CROSSFIT_IM_EXPRESSION_RESULT_V1.md`
- `GEOMETRY_BEYOND_TRANSPARENT_TWO_AXIS_RESULT_V1.md`

Known:
- within an environment, label-free I/M removal eliminates calibrated geometry identity;
- a single I/M -> geometry map learned from the other six environments leaves held-out residual geometry identity:
  - K = +0.20160;
  - 5/5 positive;
  - p = 0.0156.

Question:

> **Is the held-out geometry identity left beyond cross-fitted I/M itself organized by a stable low-dimensional residual geometry subspace?**

This does not search arbitrary rotations using identity labels.

## Fold residuals

For every held-out environment e:

1. reproduce exactly the parent training-only movement scaling;
2. reproduce exactly the parent training-only geometry scaling;
3. reproduce exactly the parent training-only linear I/M -> geometry map;
4. calculate 8-D residual geometry for training and target trajectories.

No target mean, target SD or target regression coefficient is used.

## Training-only PCA

Within each held-out fold:

- fit PCA/SVD to **training residual geometry only**;
- center training residuals by the training residual mean;
- no bat label enters PCA;
- orient PC signs deterministically by requiring the loading with largest absolute magnitude to be positive.

Apply the frozen fold loadings and training residual mean unchanged to the held-out environment.

## D1 — PC1 residual-geometry identity

Use only the first training residual PC score.

Run the same held-out own-versus-other identity estimator used by the parent.

## D2 — PC1 + PC2

Use the first two training residual PC scores.

This is secondary localization and cannot reclassify D1.

## D3 — residual after PC1 + PC2

For every fold, subtract the reconstruction in the first two training PCs from the 8-D residual geometry.

Run the same held-out identity estimator.

This asks whether identity remains beyond a 2-D residual geometry subspace.

## Null

For D1, D2 and D3 separately:

- within each environment independently permute complete bat labels among bat × environment clusters;
- PCA, scaling and I/M residualization remain label-free and fixed.

9,999 permutations each.

Seeds:
- D1: `202610061901`
- D2: `202610061902`
- D3: `202610061903`

Require >=9,500 valid permutations.

## Report

For each fold:
- PC1 variance fraction;
- PC1+PC2 variance fraction.

Across folds:
- median/min/max variance fractions.

For D1/D2/D3:
- K;
- individual means;
- positive fraction;
- null mean and 95% interval;
- one-sided p.

## Exploratory interpretation

### D1 supported
A single label-free residual-geometry axis carries portable identity beyond the cross-fitted I/M decoder.

### D1 unsupported, D2 supported
The residual carrier requires at least a two-dimensional leading subspace under this diagnostic.

### D2 unsupported
No stable leading two-PC residual carrier is supported.

### D3 supported
Even two leading residual PCs do not exhaust the held-out geometry identity.

### D2 supported and D3 unsupported
The residual geometry carrier is approximately low-dimensional to the resolution of this archive.

## Ceiling

Do not call any residual PC a causal third policy axis.

A residual carrier can reflect:
- omitted personal state;
- task-dependent nonlinear realization;
- model misspecification;
- system-specific geometry structure.

No post-output alternate PCA dimension may rescue the result.
